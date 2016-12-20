#!/usr/bin/env python
import hashlib
import os
import random
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from subprocess import check_output

envelope = r'''%% processed with readme2tex
\documentclass{article}
%s
\usepackage{geometry}
\pagestyle{empty}
\geometry{paperwidth=250mm, paperheight=16383pt, left=0pt, top=0pt, textwidth=426pt, marginparsep=20pt, marginparwidth=100pt, textheight=16263pt, footskip=40pt}
\begin{document}
%s%s
\end{document}
'''

try:
    input = raw_input
except NameError:
    pass


def rendertex(engine, string, packages, temp_dir, block):
    if engine != 'latex': raise Exception("Not Implemented")
    source = envelope % ('\n'.join(r'\usepackage{%s}' % ''.join(package) for package in packages), 'a' if not block else '', string)
    name = hashlib.md5(string.encode('utf-8')).hexdigest()
    source_file = os.path.join(temp_dir, name + '.tex')
    with open(source_file, 'w') as file:
        file.write(source)

    try:
        check_output(
            [engine, '-output-directory=' + temp_dir, '-interaction', 'nonstopmode', source_file],
            stderr=sys.stdout)
    except:
        print("'%s' has warnings during compilation. See %s/%s" % (string, temp_dir, name))
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
            if lines[line].startswith('   '):
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
            cummulative = 0
            line = 0
            for line, string in enumerate(lines):
                cummulative += len(string) + 1
                if begin < cummulative: break
            if lines[line].startswith('   '):
                cursor = begin + 6
                continue
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
        readme,
        output='README_GH.md',
        engine='latex',
        packages=('amsmath', 'amssymb'),
        svgdir='svgs',
        branch=None,
        user=None,
        project=None,
        nocdn=False,
        htmlize=False,
        use_valign=False,
        rerender=False,
        bustcache=False):
    # look for $.$ or $$.$$
    if htmlize:
        nocdn = True
        branch = None
    temp_dir = tempfile.mkdtemp('', 'readme2tex-')

    with open(readme) as readme_file:
        content = readme_file.read()
    content = content.replace('\r', '')

    equations = list(extract_equations(content))
    equation_map = {}
    seen = {}
    has_changes = False
    for equation, start, end, block in equations:
        if equation in seen:
            equation_map[(start, end)] = equation_map[seen[equation]]
            continue
        seen[equation] = (start, end)

        # Check if this already exists
        svg = None
        name = hashlib.md5(equation.encode('utf-8')).hexdigest()
        svg_path = os.path.join(svgdir, name + '.svg')
        if branch:
            try:
                svg = check_output(['git', 'show', '%s:%s' % (branch, svg_path.replace('\\', '/'))]).decode('utf-8')
            except Exception as e:
                print("Cannot find %s:%s" % (branch, svg_path.replace('\\', '/')))
                pass
        else:
            if os.path.exists(svg_path):
                with open(svg_path) as f:
                    svg = f.read()

        try:
            if svg and not rerender:
                xml = ET.fromstring(svg)
                offset = float(xml.attrib['{http://github.com/leegao/readme2tex/}offset'])
                equation_map[(start, end)] = (svg, name, None, offset)
                continue
        except Exception as e:
            print("Cached SVG file for %s is corrupt, rerendering." % svg_path)
            pass

        svg, dvi, name = rendertex(engine, equation, packages, temp_dir, block)
        svg = svg.decode('utf-8')

        xml = (ET.fromstring(svg))
        attributes = xml.attrib
        gfill = xml.find('{http://www.w3.org/2000/svg}g')
        gfill.set('fill-opacity', '0.9')
        if not block:
            uses = gfill.findall('{http://www.w3.org/2000/svg}use')
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
            gfill.remove(use)
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
        else:
            baseline_offset = 0

        xml.set('readme2tex:offset', str(baseline_offset))
        xml.set('xmlns:readme2tex', 'http://github.com/leegao/readme2tex/')
        svg = ET.tostring(xml).decode('utf-8')

        has_changes = True
        equation_map[(start, end)] = (svg, name, dvi, baseline_offset)

    # git rev-parse --abbrev-ref HEAD
    try:
        old_branch = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip()
    except:
        if not nocdn:
            print("Not in a git repository, please enable --nocdn")
        old_branch = "NONE"

    if has_changes:
        if not branch or branch == old_branch:
            branch = old_branch
            if not os.path.exists(svgdir):
                os.makedirs(svgdir)
            for equation, start, end, _ in equations:
                svg, name, dvi, off = equation_map[(start, end)]
                if dvi:
                    with open(os.path.join(svgdir, name + '.svg'), 'w') as file:
                        file.write(svg)
        else:
            # git stash -q --keep-index
            stashed = False
            if check_output(['git', 'status', '-s']).decode('utf-8').strip():
                if input(
                        "There are unstaged files, would you like to stash them? "
                        "(They will be automatically unstashed.) [(y)/n]").lower().startswith('n'):
                    print("Aborting.")
                    return
                print("Stashing...")
                check_output(['git', 'stash', '-u'])
                stashed = True
            try:
                print("Checking out %s" % branch)
                check_output(['git', 'checkout', branch])

                if not os.path.exists(svgdir):
                    os.makedirs(svgdir)
                for equation, start, end, _ in equations:
                    svg, name, dvi, off = equation_map[(start, end)]
                    if dvi:
                        with open(os.path.join(svgdir, name + '.svg'), 'w') as file:
                            file.write(svg)

                status = check_output(['git', 'status', '-s']).decode('utf-8').strip()
                if status:
                    print(status)
                    print("Committing changes...")
                    check_output(['git', 'add', svgdir])
                    check_output(['git', 'commit', '-m', 'readme2latex render'])
                else:
                    print("No changes were made.")

                print("Switching back to the original branch")
                check_output(['git', 'checkout', old_branch])
            except Exception as e:
                print(e)
                try:
                    print("Cleaning up.")
                    check_output(['git', 'checkout', '--', '.'])
                    check_output(['git', 'clean', '-df'])
                    check_output(['git', 'checkout', old_branch])
                except Exception as e_:
                    print("Could not cleanup. %s\n\nMake sure that you cleanup manually." % e_)
                if stashed:
                    print("You have stashed changes on " + old_branch + ", make sure you unstash them there.")
                raise e

            if stashed:
                print("Unstashing...")
                check_output(['git', 'stash', 'pop', '-q'])

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

        needs_inversion = not (equation.count('tikzpicture') and equation.count('fill='))

        scale = 1.65
        height = float(attributes['height'][:-2]) * scale
        width = float(attributes['width'][:-2]) * scale
        url = svg_url.format(user=user, project=project, branch=branch, svgdir=svgdir, name=name)
        tail = []
        if bustcache:
            tail.append('%x' % random.randint(0, 1e12))
        if needs_inversion:
            tail.append('invert_in_darkmode')
        img = '<img src="%s%s" %s width=%spt height=%spt/>' % (
            url,
            '?%s' % ('&'.join(tail)) if tail else '',
            ('valign=%spx'%(-off * scale) if use_valign else 'align=middle'),
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
