#!/bin/bash
#/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cbusillo/Shiny_API/bulid-system/install_client.sh)"
"""TODO: Update to master"""
activate () { 
    . ./.venv/bin/activate
}
REQPYTHON="3.10"
killall Python &> /dev/null
cd ~
pwd
exit
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

if [ ! -d "Shiny_API" ]; then 
    python$REQPYTHON -m virtualenv Shiny_API
fi

activate

python$REQPYTHON -m pip install -U Shiny_API
