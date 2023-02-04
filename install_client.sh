#!/bin/bash
activate () { 
    . ./.venv/bin/activate
}
REQPYTHON="3.10"
killall Python &> /dev/null
cd "$(dirname "$0")"

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