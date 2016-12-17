import os
from glob import glob
from subprocess import check_output

from . import render

try:
    input = raw_input
except NameError:
    pass

post_commit_template = r'''#!/bin/bash

if [ ! -z "$postcommit" ]; then
    exit
fi

export postcommit=true

bold=$(tput bold)
color=$(tput setaf 2)
reset=$(tput sgr0)

branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$branch" = "svgs" ]; then
    exit
fi

# Check to see if %(readother)s has been updated

changes=$(git diff --name-only HEAD^ | grep "%(readother)s")

if [ -z "$changes" ]; then
    exit
fi

exec < /dev/tty

read -p "[readme2tex] ${color}%(readother)s$reset has changed; would you like to update ${color}%(readme)s$reset as well? This will run

  > python -m readme2tex --output ${color}%(readme)s$reset --readme ${color}%(readother)s$reset --branch ${color}%(branch)s$reset %(args)s

Would you like to run this now? [Y/n]: " meh

if [ "$meh" = "" ]; then
    meh='Y'
fi

case $meh in
    [Yy] ) ;;
    [Nn] ) exit;;
    * ) exit;;
esac

tput setaf 3
echo
echo "Running readme2tex..."
python -m readme2tex --output %(readme)s --readme %(readother)s --branch %(branch)s %(args)s
result=$?
echo $reset

if [ $result -eq 0 ]; then
    echo "Finished rendering."
    git add %(readme)s
    echo
    read -p "Do you want to amend changes to ${color}%(readme)s$reset now? [Y/n]: " meh
    if [ "$meh" = "" ]; then
        meh='Y'
    fi

    case $meh in
        [Yy] ) ;;
        [Nn] ) exit;;
        * ) exit;;
    esac

    echo
    echo "Amending commit...$color"
    git commit --amend --no-edit
    echo $reset
    echo "You should run '${bold}git push origin :${reset}' to push all branches simultaneously."
    echo
else
    echo "$(tput setaf 1)Encountered error while translating %(readother)s${reset}"
    echo "  Your environment may have changed; please make sure that you go back to a clean state."
    exit 1
fi
'''

if __name__.endswith('__main__'):
    import argparse

    epilog = r'''

To render Foo.md into Bar.md, run

> python -m readme2tex --output Bar.md Foo.md

To save the output images in a dedicated `svgs` branch, run

> python -m readme2tex --output Bar.md Foo.md --branch svgs

To add the tikz package, run

> python -m readme2tex --output Bar.md Foo.md --branch svgs --usepackage tikz

To save a script that runs this in the future, run

> python -m readme2tex --output Bar.md Foo.md --branch svgs --usepackage tikz --generate-script texify.sh

To save this script as your post-commit git hook, run

> python -m readme2tex --output Bar.md Foo.md --branch svgs --usepackage tikz --add-git-hook

    '''
    parser = argparse.ArgumentParser(prog='python -m readme2tex', description='Render LaTeX in Github Readmes', epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--readme', nargs='?', type=str, help="The Markdown input file to render.")
    parser.add_argument('--engine', type=str, default="latex")
    parser.add_argument('--output', type=str, default="README_GH.md", help="The output file. Defaults to README_GH.md")
    parser.add_argument('--usepackage', type=str, action='append', default=['amsmath', 'amssymb'], help="Include a LaTeX package. Comes with amsmath and amssymb.")
    parser.add_argument('--svgdir', type=str, default='svgs', help="Name of the folder to save the output svgs into. Defaults to svgs.")
    parser.add_argument('--branch', type=str, help="[EXPERIMENTAL] Which branch to save the svgs into. Used by the git-hook system. Defaults to the current branch.")
    parser.add_argument('--username', type=str, help="Github username. Can be inferred.")
    parser.add_argument('--project', type=str, help="Github project. Can be inferred.")
    parser.add_argument('--nocdn', action='store_true', help="Use local relative path rather than rawgit's CDN. Useful for debugging.")
    parser.add_argument('--htmlize', action='store_true', help="Output a md.html file for you to preview. Useful for debugging.")
    parser.add_argument('--valign', action='store_true', help="Use the valign attribute instead of the align=middle trick. Only works on Chrome.")
    parser.add_argument('--rerender', action='store_true', help="Even if equations have already been compiled, recompile them anyways.")
    parser.add_argument('--bustcache', action='store_true', help="Github has a latency before it will serve up the new asset. This option allows us to circumvent its caching.")
    parser.add_argument('--add-git-hook', action='store_true', help="Automatically generates a post-commit git hook with the rest of the arguments. In the future, git commit will automatically trigger readme2tex if the input file is changed.")
    parser.add_argument('input', nargs='?', type=str, help="Same as --readme")

    args = parser.parse_args()
    if args.input:
        args.readme = args.input

    if not args.add_git_hook:
        readme = args.readme or args
        if not readme:
            md_files = [file for file in glob("*.md") if file.lower() == 'readother.md']
            if md_files:
                readme = md_files[0]
        if not readme or not os.path.exists(readme):
            parser.error("Cannot find a valid Markdown file to process. "
                         "Either pass it into --readme or create a READOTHER.md file.")
        render(
            readme,
            args.output,
            args.engine,
            args.usepackage,
            args.svgdir,
            args.branch,
            args.username,
            args.project,
            args.nocdn,
            args.htmlize,
            args.valign,
            args.rerender,
            args.bustcache)
    else:
        # Make sure we're in a git top-level
        assert os.path.exists(".git")

        if args.add_git_hook:
            if os.path.exists(".git/hooks/post-commit"):
                response = input(".git/hooks/post-commit already exists. Do you want to replace it? [y/N] ")
                if response.lower() != 'y':
                    exit(1)

        environment = {
            'readother' : args.readme if args.readme else 'READOTHER.md',
            'readme'    : args.output if args.output != 'README_GH.md' else 'README.md',
            'branch'    : args.branch if args.branch else 'svgs',
        }

        if not args.readme:
            response = input("No input file (--readme) is given, defaulting to 'READOTHER.md'. Is this okay? [Y/n]: ")
            if response and response.lower() != 'y':
                exit(1)

        if args.output == 'README_GH.md':
            response = input("No output file (--output) is given, defaulting to 'README.md'. Is this okay? [Y/n]: ")
            if response and response.lower() != 'y':
                exit(1)

        if not args.branch:
            response = input("No svg branch (--branch) is given, defaulting to 'svgs'. Is this okay? [Y/n]: ")
            if response and response.lower() != 'y':
                exit(1)

        try:
            check_output(['git', 'rev-parse', '--verify', environment['branch']])
        except:
            print("The branch %s does not exist. Make sure that you create it before continuing." % environment['branch'])
            exit(1)

        args_strings = []
        for arg, val in args.__dict__.items():
            if arg in {'readme', 'output', 'branch', 'engine', 'usepackage', 'add_git_hook', 'generate_script', 'input'}: continue
            if not val: continue
            if isinstance(val, bool):
                args_strings.append('--' + arg)
            else:
                args_strings.append('--' + arg + ' \'' + str(val) + '\'')

        for package in args.usepackage:
            if package in {'amsmath', 'amssymb'}: continue
            args_strings.append('--usepackage \'' + str(package) + '\'')

        environment['args'] = ' '.join(args_strings)

        print('')
        script = post_commit_template % environment
        try:
            from pygments import highlight
            from pygments.lexers import BashLexer
            from pygments.formatters import TerminalFormatter
            print(highlight(script, BashLexer(), TerminalFormatter()))
        except NameError:
            print(script)

        response = input("Would you like to write this to %s? [y/N] " % '.git/hooks/post-commit')
        if response.lower() != 'y':
            exit(1)

        if args.add_git_hook:
            with open('.git/hooks/post-commit', 'w') as f:
                f.write(script)
