import tempfile
from subprocess import check_output
from glob import glob
import re, os
import hashlib
import xml.etree.ElementTree as ET

import io

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
    name = hashlib.md5(string.encode('utf-8')).hexdigest()
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
                yield content[dollar: cursor], dollar, cursor, True
            else:
                cursor = content.find('$', dollar + 1) + 1
                if cursor == -1:
                    cursor = dollar + 1
                    continue
                yield content[dollar: cursor], dollar, cursor, False
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
            yield content[begin: cursor], begin, cursor, True


def render(readme, output, engine, packages, svgdir, branch, user=None, project=None, nocdn=False):
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
    for equation, start, end, block in equations:
        if equation in seen: continue
        seen.add(equation)
        svg, dvi, name = rendertex(engine, equation, packages, temp_dir)
        svg = svg.decode('utf-8')
        equation_map[(start, end)] = (svg, name, dvi)

    # git rev-parse --abbrev-ref HEAD
    old_branch = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip()
    if not branch or branch == old_branch:
        branch = old_branch
        if not os.path.exists(svgdir):
            os.makedirs(svgdir)
        for equation, start, end, _ in equations:
            svg, name, dvi = equation_map[(start, end)]
            with open(os.path.join(svgdir, name + '.svg'), 'w') as file:
                file.write(svg)
    else:
        # git stash -q --keep-index
        print("Stashing changes...")
        check_output(['git', 'stash', '-q', '--keep-index', '--include-untracked'])
        try:
            print("Checking out %s" % branch)
            check_output(['git', 'checkout', branch])

            if not os.path.exists(svgdir):
                os.makedirs(svgdir)
            for equation, start, end, _ in equations:
                svg, name, dvi = equation_map[(start, end)]
                with open(os.path.join(svgdir, name + '.svg'), 'w') as file:
                    file.write(svg)

            print("Committing changes...")
            check_output(['git', 'add', svgdir])
            check_output(['git', 'commit', '-m', 'readme2latex render'])

            print("Switching back to the original branch")
            check_output(['git', 'checkout', old_branch])
        except Exception as e:
            print(e)
            print("Cleaning up.")
            check_output(['git', 'checkout', '--', '.'])
            check_output(['git', 'clean', '-df'])
            check_output(['git', 'checkout', old_branch])
            pass
        # git stash pop -q
        check_output(['git', 'stash', 'pop', '-q'])

    # Make replacements
    if not user or not project:
        try:
            # git remote get-url origin
            giturl = check_output(['git', 'remote', 'get-url', 'origin']).strip().decode('utf-8')
            start = giturl.find('.com/') + 5
            userproj = giturl[start:]
            end = userproj.find('.git')
            user, project = userproj[:end].split('/')
        except:
            raise Exception("Please specify your github --username and --project.")

    if nocdn:
        svg_url = "https://raw.githubusercontent.com/{user}/{project}/{branch}/{svgdir}/{name}.svg"
    else:
        svg_url = "https://rawgit.com/{user}/{project}/{branch}/{svgdir}/{name}.svg"
    equations = sorted(equations, key=lambda x: (x[1], x[2]))[::-1]
    new = content
    for equation, start, end, block in equations:
        svg, name, dvi = equation_map[(start, end)]
        xml = (ET.fromstring(svg))
        attributes = xml.attrib
        height = float(attributes['height'][:-2]) * 2
        width = float(attributes['width'][:-2]) * 2
        url = svg_url.format(user=user, project=project, branch=branch, svgdir=svgdir, name=name)
        img = '<img src="%s" valign=middle width=%spt height=%spt/>' % (url, width, height)
        if block: img = '<p align="center">%s</p>' % img
        new = new[:start] + img + new[end:]
    with open(output, 'w') as outfile:
        outfile.write(new)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Render LaTeX in Github Readmes')
    parser.add_argument('--readme', type=str)
    parser.add_argument('--engine', type=str, default="latex")
    parser.add_argument('--output', type=str, default="README_GH.md")
    parser.add_argument('--packages', type=list, action='append', default=['amsmath', 'amssymb', 'amsfont'])
    parser.add_argument('--svgdir', type=str, default='svgs')
    parser.add_argument('--branch', type=str)
    parser.add_argument('--username', type=str)
    parser.add_argument('--project', type=str)
    parser.add_argument('--nocdn', default=False)

    args = parser.parse_args()
    render(args.readme, args.output, args.engine, args.packages, args.svgdir, args.branch, args.username, args.project, args.nocdn)
