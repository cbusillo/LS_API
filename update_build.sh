#!/bin/bash
killall Python &> /dev/null
cd "$(dirname "$0")"
if ! git diff -- update_build.sh --quiet
then
    echo "Updating files."
    git pull https://github.com/cbusillo/LS_API
    echo "Restarting script."
    $(basename $0) && exit     
else
    git pull https://github.com/cbusillo/LS_API
fi
which -s brew
if [[ $? != 0 ]] ; then
    # Install Homebrew
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
else
    brew update
fi
if [[ $(uname -m) == 'arm64' ]]; then
    arch -arm64 brew install python@3.11
else
    brew install python@3.11
fi

pip3.11 install kivy --pre --no-deps --index-url  https://kivy.org/downloads/simple/
pip3.11 install "kivy[base]" --pre --extra-index-url https://kivy.org/downloads/simple/

pip3.11 install pyinstaller
pip3.11 install opencv
pip3.11 install pipreqs
pip3.11 install -U -r requirements.txt
#make binary on desktop
./gui.py