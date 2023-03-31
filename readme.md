/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11 cliclick redis stunnel
brew services start redis
python3.11 install poetry

git clone https://github.com/cbusillo/Shiny_API
cd Shiny_API
poetry shell
python shiny_api/modules/django_server.py migrate

