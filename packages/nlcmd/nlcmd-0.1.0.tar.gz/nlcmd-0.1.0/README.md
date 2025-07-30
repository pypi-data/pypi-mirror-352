# nlcmd

**Offline Natural Language Command Runner**

nlcmd turns simple English‐like instructions into shell commands and executes them. No internet required—just rapidfuzz for fuzzy matching.

## Features

- Fully offline: no API keys or external calls.  
- Fuzzy matching + optional spaCy lemmatization.  
- Built-in command database (JSON) and user overrides via `~/.nlcmd/config.yaml`.  
- Interactive REPL and one‐off “run” subcommand.  
- Plugin support: drop additional JSON files into `nlcmd/commands/`.  
- Unit tests (pytest) for parser and executor.  
- Packaged as a normal Python CLI (`nlcmd`).

## Installation

### 1. From PyPI

```bash
# (Optional) Create a venv
python -m venv ~/.venvs/nlcmd
source ~/.venvs/nlcmd/bin/activate    # Linux/macOS
# OR
# .\venvs\nlcmd\Scripts\activate       # Windows PowerShell

pip install nlcmd
