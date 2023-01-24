#!/bin/bash

killall Python &> /dev/null
cd "$(dirname "$0")"
if ! git diff -- update_build.sh --quiet
then
    echo "Updating files."
    git pull https://github.com/cbusillo/LS_API
    echo "Restart script."
    exit     
else
    git pull https://github.com/cbusillo/LS_API
fi
which -s brew
if [[ $? != 0 ]] ; then
    # Install Homebrew
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    brew update
fi
if [[ $(uname -m) == 'arm64' ]]; then
    arch -arm64 brew install python@3.11
else
    brew install python@3.11
fi
brew upgrade
brew install pkg-config sdl2 sdl2_image sdl2_ttf sdl2_mixer
pip3.11 install virtualenv

if [ ! -d "./.venv" ]; then 
    python3.11 -m virtualenv .venv
fi

source .venv/bin/activate


#pip3.11 install git+https://github.com/SciTools/cartopy.git
pip3.11 install -U -r requirements-manual.txt
pip3.11 install -U -r requirements.txt

if [[ $(uname -m) == 'arm64' ]]; then
    pip3.11 install kivy --pre --no-deps --index-url  https://kivy.org/downloads/simple/
    pip3.11 install "kivy[base]" --pre --extra-index-url https://kivy.org/downloads/simple/
else
    pip3.11 install kivy
    #pip3.11 install -U git+https://github.com/kivy/kivy
    #pip3.11 install "kivy[base]"
fi

#make binary on desktop
#source ~/.bashrc

./gui.py