#!/bin/bash

bold=$(tput setaf bold)
color=$(tput setaf 2)
reset=$(tput sgr0)

branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$branch" = "svgs" ]; then
    exit
fi

# Check to see if READOTHER.md has been updated

changes=$(git diff --name-only HEAD^ | grep "READOTHER.md")
readme=$(git diff --name-only HEAD^ | grep "README.md")

if [ -z "$changes" ]; then
    exit
fi

if [ ! -z "$readme" ]; then
    exit
fi

exec < /dev/tty

read -p "[readme2tex] ${color}READOTHER.md$reset has changed; would you like to update ${color}README.md$reset as well? This will run

  > python -m readme2tex --output ${color}README.md$reset --readme ${color}READOTHER.md$reset --branch ${color}svgs$reset --svgdir 'svgs' --usepackage 'tikz' --usepackage 'xcolor'

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
python -m readme2tex --output README.md --readme READOTHER.md --branch svgs --svgdir 'svgs' --usepackage 'tikz' --usepackage 'xcolor'
echo $reset

if [ $? -eq 0 ]; then
    echo "Finished rendering."
    git add README.md
    echo
    read -p "Do you want to amend changes to ${color}README.md$reset now? [Y/n]: " amend
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
    echo "$(tput setaf 1)Encountered error while translating READOTHER.md${reset}"
    exit 1
fi
