# SPREAD — Setup Guide (Windows)

This guide sets up the SPREAD project on a Windows machine using Python + Pygame.

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
