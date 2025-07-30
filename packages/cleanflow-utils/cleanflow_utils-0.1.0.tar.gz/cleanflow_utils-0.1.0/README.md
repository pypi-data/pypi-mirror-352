# cleanflow-utils

A minimalist toolkit for cleaning up LLM token streams and normalizing batch input threads.

Includes:
- `cleanup.py` – Removes HTML tags, stray symbols
- `token_optimizer.py` – Token compression and basic filter tools

## Installation

```bash
pip install cleanflow-utils


> 🔁 You had **"Author: Sel Wynn"** duplicated and floating **above** the project title. I moved it to the end — that’s the standard convention for PyPI `README.md`.

✅ Now save it like this:
- `Ctrl + O` → **Save**
- `Enter`
- `Ctrl + X` → **Exit**

---

### 📦 THE YAML PART YOU ASKED ABOUT

That "YAML" reference **wasn’t literal code** you needed to save — it was just part of a formatting label. You **do not** need to save any file called `yaml`. It was Markdown syntax from a docstring example (ignore that part).

You only need:

1. `README.md` → Fixed ✅
2. `setup.py` → Already good ✅
3. `LICENSE.txt` → Already good ✅
4. `cleanup.py` and `token_optimizer.py` → Already exist ✅
5. **Create your PyPI token at:**  
   [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)

Once you copy your token:

---

### 🛡 HOW TO UPLOAD

Now you're ready to publish.

📍 Run from inside: `~/pypi/cleanflow-utils/`

```bash
python3 setup.py sdist bdist_wheel
twine upload dist/*
