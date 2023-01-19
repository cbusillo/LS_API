#!/bin/bash
killall Python &> /dev/null
if ! git diff -- update_build.py --quiet
then
    echo "Updating files."
    git pull https://github.com/cbusillo/LS_API
    echo "Restarting script."
    $(basename $0) && exit     
fi

if [[ $(uname -m) == 'arm64' ]]; then
    arch -arm64 brew upgrade python-tk@3.11
else
    brew upgrade python-tk@3.11
fi

pip3.11 install -r requirements.txt
#make binary on desktop
./gui.py