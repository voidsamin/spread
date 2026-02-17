# SPREAD — Setup Guide (Windows)

This guide sets up the SPREAD project on a Windows machine using Python + Pygame.
Python version: 3.11.9
Pygame version: 2.6.1

---

## 1) Install prerequisites

### ✅ Install Python (required)

- Install **Python 3.10+** (3.11 recommended)
- During install, make sure to check:
  - ✅ **Add Python to PATH**

Verify:

```powershell
python --version
pip --version
```

## 2) Create a virtual environment (Not necessary but recommended)

- Inside the Project Folder 'spread':

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python --version
```

- For Linux Distros

```bash
python -m venv .venv
source .venv/bin/activate
python --version
```

- If PowerShell blocks activation, run this once (then try activating again):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

- Confirm venv is active (you should see (.venv) at the left of your terminal):

```powershell
python --version
```

## 3) Install Dependencies

### ✅Install Pygame (required)

```powershell
pip install pygame
```

- Upgrade pip if you see a notice:

```powershell
python -m pip install --upgrade pip
```

## 4) Run the project

- From the project root folder (spread):

```powershell
python src\main.py
```

## To get out of Virtual Environment

- Type in terminal in root folder:

```powershell
deactivate
```

## Fix issues with the python version

### Easy run python pyenv

Run:

```bash
rm -rf .venv
~/.pyenv/versions/3.11.9/bin/python -m venv .venv
source .venv/bin/activate
python --version
```

### Step A — Leave the old venv (so it stops hijacking python)

Run:

```bash
deactivate 2>/dev/null || true
```

Now verify python is system python:

```bash
python --version
```

### Step B — Initialize pyenv for this terminal session (no config changes yet)

Run:

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Now check:

```bash
pyenv versions
pyenv which python
python --version
```

### Step C — Set pyenv to use 3.11.9 in your project folder

```bash
cd "/home/user/project/Simulation_Project/spread"
pyenv local 3.11.9
pyenv rehash
python --version
```

You must see Python 3.11.9 here.

If you still see 3.14, run:

```bash
hash -r
python --version
```

### Step D — Recreate the venv using pyenv’s Python 3.11.9

This is the key fix.

```bash
cd "/home/user/project/Simulation_Project/spread"
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
python --version
```

Now it should say Python 3.11.9.

### Step E — Install pygame and test fonts

```bash
pip install -U pip setuptools wheel
pip install -U pygame
python -c "import pygame; print('py', __import__('sys').version); pygame.init(); pygame.font.init(); print('font ok')"
```

If you still get the “Font partially initialized” error

That usually means shadowing in your project. Check:

```bash
cd "/home/user/project/Simulation_Project/spread"
find . -maxdepth 2 -type f -name "pygame.py" -o -type d -name "pygame"
```

If anything shows up, rename it and retry.
