#!/bin/bash
#/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cbusillo/Shiny_API/main/install_client.sh)"
REQPYTHON="3.11"
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
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/joshalletto/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
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

brew install python@$REQPYTHON tesseract cliclick

python$REQPYTHON -m pip install --upgrade pip
python$REQPYTHON -m pip install virtualenv

if [ ! -d ~/$APPNAME ]; then 
    python$REQPYTHON -m virtualenv $APPNAME
fi

activate

python$REQPYTHON -m pip install --upgrade pip
python$REQPYTHON -m pip install --upgrade $APPNAME

python$REQPYTHON -m pip install --upgrade $APPNAME

python$REQPYTHON -m shiny_api.main