import os
from subprocess import check_output

from . import render

try:
    input = raw_input
except NameError:
    pass

post_commit_template = r'''#!/bin/bash

bold=$(tput setaf bold)
color=$(tput setaf 2)
reset=$(tput sgr0)

branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$branch" = "svgs" ]; then
    exit
fi

# Check to see if %(readother)s has been updated

changes=$(git diff --name-only HEAD^ | grep "%(readother)s")
readme=$(git diff --name-only HEAD^ | grep "%(readme)s")

if [ -z "$changes" ]; then
    exit
fi

if [ ! -z "$readme" ]; then
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
echo $reset

if [ $? -eq 0 ]; then
    echo "Finished rendering."
    git add %(readme)s
    echo
    read -p "Do you want to amend changes to ${color}%(readme)s$reset now? [Y/n]: " amend
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
    exit 1
fi
'''

if __name__.endswith('__main__'):
    import argparse

    parser = argparse.ArgumentParser(description='Render LaTeX in Github Readmes')
    parser.add_argument('--readme', type=str)
    parser.add_argument('--engine', type=str, default="latex")
    parser.add_argument('--output', type=str, default="README_GH.md")
    parser.add_argument('--packages', type=list, action='append', default=['amsmath', 'amssymb'])
    parser.add_argument('--svgdir', type=str, default='svgs')
    parser.add_argument('--branch', type=str)
    parser.add_argument('--username', type=str)
    parser.add_argument('--project', type=str)
    parser.add_argument('--nocdn', default=False)
    parser.add_argument('--htmlize', default=False, type=bool)
    parser.add_argument('--valign', default=False)
    parser.add_argument('--rerender', default=False)
    parser.add_argument('--bustcache', default=False)
    parser.add_argument('--add-git-hook', default=False)

    args = parser.parse_args()

    if not args.add_git_hook:
        render(
            args.readme,
            args.output,
            args.engine,
            args.packages,
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
            if arg in {'readme', 'output', 'branch', 'engine', 'packages', 'add_git_hook', }: continue
            if not val: continue
            args_strings.append('--' + arg + ' \'' + str(val) + '\'')

        for package in args.packages:
            if package in {'amsmath', 'amssymb'}: continue
            args_strings.append('--packages \'' + str(package) + '\'')

        environment['args'] = ' '.join(args_strings)

        print()
        script = post_commit_template % environment
        try:
            from pygments import highlight
            from pygments.lexers import BashLexer
            from pygments.formatters import TerminalFormatter
            print(highlight(script, BashLexer(), TerminalFormatter()))
        except NameError:
            print(script)

        response = input("Would you like to write this to .git/hooks/post-commit? [y/N] ")
        if response.lower() != 'y':
            exit(1)

        with open('.git/hooks/post-commit', 'w') as f:
            f.write(script)
