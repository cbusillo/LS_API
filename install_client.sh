#!/bin/bash
#/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cbusillo/Shiny_API/bulid-system/install_client.sh)"
"""TODO: Update to master"""
REQPYTHON="3.10"
APPNAME="Shiny_API"
activate () { 
    . ./$APPNAME/bin/activate
}

killall Python &> /dev/null
cd ~

which -s brew
if [[ $? != 0 ]] ; then
    # Install Homebrew
    if [[ $(uname -m) == 'arm64' ]]; then
        arch -arm64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    echo "Restart script."
    exec /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cbusillo/Shiny_API/bulid-system/install_client.sh)"

    exit     
else
    brew update
fi
brew upgrade

brew install python@$REQPYTHON

python$REQPYTHON -m pip install --upgrade pip
python$REQPYTHON -m pip install virtualenv


python$REQPYTHON -m virtualenv $APPNAME
if [ ! -d ~/$APPNAME ]; then 
    python$REQPYTHON -m virtualenv $APPNAME
fi
pwd
exit

activate

python$REQPYTHON -m pip install -U $APPNAME
