#!/bin/bash
activate () { 
    . ./.venv/bin/activate
}
killall Python &> /dev/null
cd "$(dirname "$0")"
git remote update
if ! git diff origin/main --quiet update_build.sh
then
    echo "Updating files."
    git pull https://github.com/cbusillo/LS_API
    echo "Restart script."
    exec $0
    exit     
else
    git pull https://github.com/cbusillo/LS_API
fi
which -s brew
if [[ $? != 0 ]] ; then
    # Install Homebrew
    arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    brew update
fi

brew install python@3.11
brew upgrade
brew install pkg-config sdl2 sdl2_image sdl2_ttf sdl2_mixer
pip3.11 install virtualenv

if [ ! -d "./.venv" ]; then 
    python3.11 -m virtualenv .venv
fi

activate


#pip3.11 install git+https://github.com/SciTools/cartopy.git test
pip3.11 install -U -r requirements-manual.txt
pip3.11 install -U -r requirements.txt
brew install tesseract
if [[ $(uname -m) == 'arm64' ]]; then
    pip3.11 install kivy --pre --no-deps --index-url  https://kivy.org/downloads/simple/
    #pip3.11 install "kivy[base]" --pre --extra-index-url https://kivy.org/downloads/simple/
else
    USE_OSX_FRAMEWORKS=0 pip3.11 install https://github.com/kivy/kivy/zipball/master
    #pip3.11 install -U git+https://github.com/kivy/kivy
    #pip3.11 install "kivy[base]"
fi

#make binary on desktop
./gui.py