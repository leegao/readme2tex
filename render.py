import tempfile
from subprocess import check_output
from glob import glob
import re, os

envelope = r'''%% processed with readme2tex
\documentclass{article}
%s
\pagestyle{empty}
\begin{document}
%s
\end{document}
'''


def rendertex(engine, string, packages, temp_dir):
    if engine != 'latex': raise Exception("Not Implemented")
    source = envelope % ('\n'.join(r'\usepackage{%s}' % package for package in packages), string)
    name = '%x' % hash(string)
    source_file = os.path.join(temp_dir, name + '.tex')
    with open(source_file, 'w') as file:
        file.write(source)
    check_output(
        [engine, '-output-directory=' + temp_dir, '-halt-on-error', source_file],
        input=source.encode('utf-8'))
    dvi = os.path.join(temp_dir, name + '.dvi')
    svg = check_output(
        ['dvisvgm', '-v0', '-a', '-n', '-s', dvi])
    return svg, dvi, name


def extract_equations(content):
    next = lambda n: (content.find('$', n), content.find(r'\begin', n))
    cursor = 0
    while True:
        dollar, begin = next(cursor)
        if dollar is -1 and begin is -1: break
        if (dollar < begin or begin == -1) and dollar is not -1:
            # found a $, see if it's $$
            if dollar > 0 and content[dollar - 1] == '\\':
                cursor = dollar + 1
                continue
            if len(content) > dollar and content[dollar + 1] == '$':
                ## find the next $$
                cursor = content.find('$$', dollar + 2) + 2
                if cursor == -1:
                    cursor = dollar + 1
                    continue
                yield content[dollar: cursor], dollar, cursor
            else:
                cursor = content.find('$', dollar + 1) + 1
                if cursor == -1:
                    cursor = dollar + 1
                    continue
                yield content[dollar: cursor], dollar, cursor
        else:
            leftover = content[begin + 6:]
            if not leftover: break
            match = re.match(r"\{.+?\}", leftover)
            if not match:
                cursor = begin + 6
                continue
            end_marker = '\\end' + match.group()
            end = content.find(end_marker, begin)
            if end is -1:
                cursor = begin + 6
                continue
            cursor = end + len(end_marker)
            yield content[begin: cursor], begin, cursor


def render(readme, output, engine, packages, svgdir, branch):
    # look for $.$ or $$.$$
    temp_dir = tempfile.mkdtemp('', 'readme2tex-')
    if not readme or not open(readme):
        md_files = [file for file in glob("*.md") if file.lower() == 'readother.md']
        if not md_files: raise Exception("Must either pass in a --readme file or have a READOTHER.md file.")
        readme = md_files[0]

    with open(readme) as readme_file:
        content = readme_file.read()
    if not content: raise Exception("Cannot read file.")

    equations = list(extract_equations(content))
    seen = set([])
    equation_map = {}
    for equation, start, end in equations:
        if equation in seen: continue
        seen.add(equation)
        svg, dvi, name = rendertex(engine, equation, packages, temp_dir)
        svg = svg.decode('utf-8')
        equation_map[(start, end)] = (svg, name, dvi)

    # git rev-parse --abbrev-ref HEAD
    old_branch = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8')
    if not branch or branch == old_branch:
        if not os.path.exists(svgdir):
            os.makedirs(svgdir)
        for equation, start, end in equations:
            svg, name, dvi = equation_map[(start, end)]
            with open(os.path.join(svgdir, name + '.svg'), 'w') as file:
                file.write(svg)
    else:
        # git stash -q --keep-index
        check_output(['git', 'stash', '-q', '--keep-index', '--include-untracked'])
        try:
            check_output(['git', 'checkout', branch])

            if not os.path.exists(svgdir):
                os.makedirs(svgdir)
            for equation, start, end in equations:
                svg, name, dvi = equation_map[(start, end)]
                with open(os.path.join(svgdir, name + '.svg'), 'w') as file:
                    file.write(svg)

            check_output(['git', 'checkout', old_branch])
        except Exception as e:
            print(e)
            check_output(['git', 'checkout', '--', '.'])
            check_output(['git', 'clean', '-df'])
            check_output(['git', 'checkout', old_branch])
            pass
        # git stash pop -q
        check_output(['git', 'stash', 'pop', '-q'])


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Render LaTeX in Github Readmes')
    parser.add_argument('--readme', type=str)
    parser.add_argument('--engine', type=str, default="latex")
    parser.add_argument('--output', type=str, default="README_GH.md")
    parser.add_argument('--packages', type=list, action='append', default=['amsmath', 'amssymb', 'amsfont'])
    parser.add_argument('--svgdir', type=str, default='svgs')
    parser.add_argument('--branch', type=str)

    args = parser.parse_args()
    render(args.readme, args.output, args.engine, args.packages, args.svgdir, args.branch)
