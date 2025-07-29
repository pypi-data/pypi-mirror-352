# 📦 DeliverFreshWhatsAppOrder

Clean and normalize WhatsApp chat orders (in `.txt` format) into structured product lists.

## 🚀 Features

- ✅ Clean WhatsApp chat exports
- 🧹 Remove quantities, duplicates, punctuation
- 📦 Standardize product names (e.g. "tomatoes" → "tomato")
- 🧑‍💻 Built as a `pip`-installable Python package
- 🟢 Works in Google Colab with only file path changes
- 🌐 Documentation in English, Hindi, Tamil, Japanese

## 📦 Installation

```bash
pip install deliverfresh-whatsapp-order
```

# 📄 Usage Example (in Google Colab)

```bash
# 📌 Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# 📌 Import and use the package
from deliverfresh_whatsapp_order import clean_chat_file

# ✅ Set paths (editable by user)
input_path = "/content/drive/MyDrive/DeliveryFresh/WhatsAppInput/inputfile.txt"
output_path = "/content/drive/MyDrive/DeliveryFresh/WhatsAppOutput/inputfile_Cleaned.txt"

# 🚀 Run the cleaning
clean_chat_file(input_path, output_path)

print("✅ Cleaning complete. Check your output file.")
```

# 📚 Documentation

Full documentation is available at:

🔗 https://rperumal3000.github.io/DeliverFreshWhatsAppOrder

# 🛠 Contributing

See https://github.com/rperumal3000/DeliverFreshWhatsAppOrder/blob/main/CONTRIBUTING.md for guidelines on how to contribute.

# 🐛 Issues / Feedback

Please open a GitHub Issue at https://github.com/rperumal3000/DeliverFreshWhatsAppOrder/issues
