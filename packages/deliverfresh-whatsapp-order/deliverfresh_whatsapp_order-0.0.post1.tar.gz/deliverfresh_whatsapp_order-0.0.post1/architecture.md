# 🏗️ Architecture: DeliverFreshWhatsAppOrder

## 📌 Project Objective

To build a reusable, pip-installable Python package that can:
- Clean and normalize WhatsApp order `.txt` exports.
- Be operated by non-developers via Google Colab.
- Be versioned, tested, and documented using industry-standard DevOps practices.
- Be published to PyPI and consumed by any downstream script or application.

---

## 📁 Folder Structure

```
DeliverFreshWhatsAppOrder/
│
├── deliverfresh_whatsapp_order/     # 📦 Main Python package logic
│   └── __init__.py
│   └── cleaner.py                   # All text cleaning logic
│
├── tests/                           # ✅ Unit tests
│   └── test_cleaner.py
│
├── .github/
│   └── workflows/
│       └── ci.yml                   # GitHub Actions: Pytest + Coverage
│
├── docs/                            # 🌐 MkDocs multilingual documentation
│   └── index.md (EN, HI, TA, JA)
│
├── pyproject.toml                   # 📦 Package metadata (PEP 621)
├── README.md                        # 📝 Project overview
├── LICENSE                          # ⚖️ MIT License
├── CONTRIBUTING.md                  # 🙌 Guidelines to contribute
├── CONTRIBUTORS.md                  # 🧑‍💻 Credits
└── .gitignore                       # 🚫 Ignore unnecessary files
```

---

## 🛠️ Toolchain

| Purpose                         | Tool/Framework                  |
|----------------------------------|----------------------------------|
| Package Management               | `pyproject.toml` (PEP 621)       |
| CI/CD Pipeline                   | GitHub Actions (`ci.yml`)        |
| Test Framework                   | `pytest`, `pytest-cov`, `coverage` |
| Docs & Site                      | `mkdocs-material`, `mkdocs-static-i18n` |
| Multilingual Support             | English, Hindi, Tamil, Japanese |
| GitHub Pages Deployment          | `mike` for versioned documentation |
| Google Colab Execution           | Notebook with `pip install` + input/output |
| Python Packaging + Distribution  | `build`, `twine`, `TestPyPI` + `PyPI` |

---

## 📦 Google Colab Usage (Entry Point)

```python
from deliverfresh_whatsapp_order import clean_chat_file

input_file = "/content/drive/MyDrive/DeliveryFresh/WhatsAppInput/sample.txt"
output_file = "/content/drive/MyDrive/DeliveryFresh/WhatsAppOutput/sample_cleaned.txt"

clean_chat_file(input_file, output_file)
```

---

## ⚙️ GitHub Actions (CI/CD)

| Workflow File        | Purpose                            |
|----------------------|-------------------------------------|
| `.github/workflows/ci.yml` | ✅ Run tests + Generate coverage report |

- Automatically runs on every `push` or `pull_request` to `main`.
- HTML report (`htmlcov/index.html`) uploaded as an artifact.

---

## 🌐 Documentation Strategy

- Built with `mkdocs` and deployed via `mike` to `gh-pages`
- Localized using `mkdocs-static-i18n`
- Available at: [https://rperumal3000.github.io/DeliverFreshWhatsAppOrder](https://rperumal3000.github.io/DeliverFreshWhatsAppOrder)

---

## 🚀 Deployment & Distribution

| Step                         | Status                          |
|-----------------------------|----------------------------------|
| GitHub Release              | ✅ Created with version tag `v0.1` |
| PyPI Package                | ✅ Published via `twine`         |
| GitHub Pages Docs           | ✅ Published via `mike deploy`   |

---

## 🔒 Security & Stability

- Pinned action versions in GitHub Actions
- `.gitignore` configured to skip checkpoints, temp files, and coverage
- Source protected: user only updates input/output paths in Colab
- Read-only packaging from PyPI ensures consistency