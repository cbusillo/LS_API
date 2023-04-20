```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11 cliclick redis stunnel tesseract postgresql@15
brew services start redis
brew services start postgresql
python3.11 install poetry
```
```
git clone https://github.com/cbusillo/Shiny_App
cd Shiny_App
poetry shell
python shiny_app/modules/django_server.py migrate
pip install seleniumbase #dep conflict poetry refuses to install
```