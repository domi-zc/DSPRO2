# macOS Installation

## Prerequisites
- Homebrew installed
- pyenv and pyenv-virtualenv installed and initialized in your shell

## Setup

```bash
git clone git@github.com:domi-zc/DSPRO2.git
cd DSPRO2

pyenv install -s 3.11.11
pyenv virtualenv 3.11.11 dspro2_env
pyenv local dspro2_env

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
````

## Verify

```bash
python --version
```

Should report Python 3.11.11.
