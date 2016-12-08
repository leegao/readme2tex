#!/usr/bin/env python

import tempfile
from subprocess import check_output
from glob import glob
import re, os
import hashlib
import xml.etree.ElementTree as ET
import sys

envelope = r'''%% processed with readme2tex
\documentclass{article}
%s
\pagestyle{empty}
\begin{document}
%s%s
\end{document}
'''


def rendertex(engine, string, packages, temp_dir, block):
    if engine != 'latex': raise Exception("Not Implemented")
    source = envelope % ('\n'.join(r'\usepackage{%s}' % package for package in packages), 'a' if not block else '', string)
    name = hashlib.md5(string.encode('utf-8')).hexdigest()
    source_file = os.path.join(temp_dir, name + '.tex')
    with open(source_file, 'w') as file:
        file.write(source)

    try:
        check_output(
            [engine, '-output-directory=' + temp_dir, '-interaction', 'nonstopmode', source_file],
            stderr=sys.stdout)
    except:
        print("'%s' has warnings during compilation." % string)
    dvi = os.path.join(temp_dir, name + '.dvi')
    svg = check_output(
        ['dvisvgm', '-v0', '-a', '-n', '-s', dvi])
    return svg, dvi, name


def extract_equations(content):
    next = lambda n: (content.find('$', n), content.find(r'\begin', n))
    cursor = 0
    lines = [line for line in content.splitlines()]
    while True:
        dollar, begin = next(cursor)
        if dollar is -1: dollar = '-1'
        if begin is -1: begin = '-1'
        if dollar == '-1' and begin == '-1': break
        if dollar != '-1' and (begin == '-1' or dollar < begin):
            # found a $, see if it's $$
            if dollar > 0 and content[dollar - 1] == '\\':
                cursor = dollar + 1
                continue
            # get this line
            cummulative = 0
            line = 0
            for line, string in enumerate(lines):
                cummulative += len(string) + 1
                if dollar < cummulative: break
            if lines[line].startswith('  '):
                cursor = dollar + 2
                continue
            if len(content) > dollar and content[dollar + 1] == '$':
                ## find the next $$
                cursor = content.find('$$', dollar + 2) + 2
                if cursor == 1:
                    cursor = dollar + 1
                    continue
                yield content[dollar: cursor], dollar, cursor, True
            else:
                cursor = content.find('$', dollar + 1) + 1
                if cursor == 0:
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


def render(
        readme=None,
        output='README_GH.md',
        engine='latex',
        packages=('amsmath', 'amssymb'),
        svgdir='svgs',
        branch=None,
        user=None,
        project=None,
        nocdn=False,
        htmlize=False,
        use_valign=False):
    # look for $.$ or $$.$$
    if htmlize:
        nocdn = True
        branch = None
    temp_dir = tempfile.mkdtemp('', 'readme2tex-')
    if not readme or not open(readme):
        md_files = [file for file in glob("*.md") if file.lower() == 'readother.md']
        if not md_files: raise Exception("Must either pass in a --readme file or have a READOTHER.md file.")
        readme = md_files[0]

    with open(readme) as readme_file:
        content = readme_file.read()
    if not content: raise Exception("Cannot read file.")
    content = content.replace('\r', '')

    equations = list(extract_equations(content))
    equation_map = {}
    seen = {}
    for equation, start, end, block in equations:
        if equation in seen:
            equation_map[(start, end)] = equation_map[seen[equation]]
            continue
        seen[equation] = (start, end)
        svg, dvi, name = rendertex(engine, equation, packages, temp_dir, block)
        svg = svg.decode('utf-8')

        if not block:
            xml = (ET.fromstring(svg))
            attributes = xml.attrib
            uses = xml.find('{http://www.w3.org/2000/svg}g').findall('{http://www.w3.org/2000/svg}use')
            use = uses[0]
            # compute baseline off of this dummy element
            x = use.attrib['x']
            y = float(use.attrib['y'])
            viewBox = [float(a) for a in attributes['viewBox'].split()] # min-x, min-y, width, height
            baseline_offset = viewBox[-1] - (y - viewBox[1])
            newViewBox = list(viewBox)

            newViewBox[0] = min(list(float(next.attrib['x']) for next in uses if next.attrib['x'] != x) or [float(x)])
            newViewBox[-2] -= abs(newViewBox[0] - viewBox[0])
            xml.set('viewBox', ' '.join(map(str, newViewBox)))
            xml.set('width', str(newViewBox[-2]) + 'pt')
            xml.find('{http://www.w3.org/2000/svg}g').remove(use)
            top = y - newViewBox[1]
            bottom = baseline_offset
            if not use_valign:
                if top > bottom:
                    # extend the bottom
                    height = 2 * top
                    xml.set('height', '%spt' % (height))
                    newViewBox[-1] = height
                    xml.set('viewBox', ' '.join(map(str, newViewBox)))
                else:
                    # extend the top
                    height = 2 * bottom
                    xml.set('height', '%spt' % (height))
                    newViewBox[-1] = height
                    newViewBox[1] -= (height - bottom - top)
                    xml.set('viewBox', ' '.join(map(str, newViewBox)))
                    pass
            svg = ET.tostring(xml).decode('utf-8')
        else:
            baseline_offset = 0

        equation_map[(start, end)] = (svg, name, dvi, baseline_offset)

    # git rev-parse --abbrev-ref HEAD
    old_branch = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip()
    if not branch or branch == old_branch:
        branch = old_branch
        if not os.path.exists(svgdir):
            os.makedirs(svgdir)
        for equation, start, end, _ in equations:
            svg, name, dvi, off = equation_map[(start, end)]
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
                svg, name, dvi, off = equation_map[(start, end)]
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
        try:
            check_output(['git', 'stash', 'pop', '-q'])
        except:
            pass

    # Make replacements
    if not user or not project:
        try:
            # git remote get-url origin
            giturl = check_output(['git', 'remote', '-v']).strip().decode('utf-8').splitlines()[0]
            start = giturl.find('.com/') + 5
            userproj = giturl[start:]
            end = userproj.find('.git')
            user, project = userproj[:end].split('/')
        except:
            raise Exception("Please specify your github --username and --project.")

    if nocdn:
        svg_url = "{svgdir}/{name}.svg"
    else:
        svg_url = "https://rawgit.com/{user}/{project}/{branch}/{svgdir}/{name}.svg"
    equations = sorted(equations, key=lambda x: (x[1], x[2]))[::-1]
    new = content
    for equation, start, end, block in equations:
        svg, name, dvi, off = equation_map[(start, end)]
        if abs(off) < 1e-2: off = 0
        xml = (ET.fromstring(svg))
        attributes = xml.attrib

        height = float(attributes['height'][:-2]) * 1.8
        width = float(attributes['width'][:-2]) * 1.8
        url = svg_url.format(user=user, project=project, branch=branch, svgdir=svgdir, name=name)
        img = '<img src="%s" %s width=%spt height=%spt/>' % (
            url,
            ('valign=%spx'%(-off * 1.8) if use_valign else 'align=middle'),
            width,
            height)
        if block: img = '<p align="center">%s</p>' % img
        new = new[:start] + img + new[end:]
    with open(output, 'w') as outfile:
        outfile.write(new)

    if htmlize:
        try:
            import markdown
        except:
            print("Cannot render markdown, make sure that the markdown package is installed.")
            return
        with open(output+".html", 'w') as outfile:
            outfile.write(markdown.markdown(new))
