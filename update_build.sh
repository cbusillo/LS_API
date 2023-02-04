#!/bin/bash
activate () { 
    . ./.venv/bin/activate
}
REQPYTHON="3.10"
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
    if [[ $(uname -m) == 'arm64' ]]; then
        arch -arm64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    echo "Restart script."
    exec $0
    exit     
else
    brew update
fi
brew upgrade

brew install python@$REQPYTHON pkg-config sdl2 sdl2_image sdl2_ttf sdl2_mixer tesseract 
python$REQPYTHON -m pip install virtualenv

if [ ! -d "./.venv" ]; then 
    python$REQPYTHON -m virtualenv .venv
fi

activate

python$REQPYTHON -m pip install -U -r requirements.txt

#make binary on desktop
./main.py