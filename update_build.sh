#!/bin/bash
activate () { 
    . ./.venv/bin/activate
}
REQPYTHON="3.11"
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
    echo "Restart script."
    exec $0
    exit     
else
    brew update
fi

brew install python@$REQPYTHON
brew upgrade
brew install pkg-config sdl2 sdl2_image sdl2_ttf sdl2_mixer
pip3.11 install virtualenv

if [ ! -d "./.venv" ]; then 
    python$REQPYTHON -m virtualenv .venv
fi

activate

pip$REQPYTHON install -U -r requirements.txt
brew install tesseract
if [[ $(uname -m) == 'arm64' ]]; then
    pip$REQPYTHON install kivy --pre --no-deps --index-url  https://kivy.org/downloads/simple/
else
    USE_OSX_FRAMEWORKS=0 pip$REQPYTHON install https://github.com/kivy/kivy/zipball/master
fi

#make binary on desktop
./gui.py