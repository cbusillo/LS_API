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
if [[ $(uname -m) == 'arm64' ]]; then
    arch -arm64 brew install python-tk@3.11
else
    brew install python-tk@3.11
fi
brew install pip3.11

pip3.11 install -U -r requirements.txt
#make binary on desktop
./gui.py