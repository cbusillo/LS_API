#!/bin/bash
killall Python &> /dev/null
if git diff -- update_build.py --quiet
then
    echo "test"
    exit
    git pull https://github.com/cbusillo/LS_API
    $(basename $0) && exit     
fi
exit
brew install python-tk@3.11
pip3.11 install -r requirements.txt
#make binary on desktop
./gui.py