# Porsline SDK

A lightweight, Pythonic SDK for integrating with the [Porsline](https://www.porsline.ir) survey API.  
Ideal for ETL pipelines, analytics, and survey automation.

## 📦 Features

- Fetch survey columns and responses
- Incremental sync via timestamp
- SOLID-compliant structure for extensibility

---

## 🚀 Installation

```bash
pip install porsline-sdk
``` 

## 🔧 Usage
```python
from porsline import Porsline

instance = Porsline(API_KEY)

all_forms = instance.get_forms()
form = instance.get_form(all_forms[0].id)
print(form.cols)
print(form.responses()) # To get all responses
print(form.responses('2025-05-19T10:32:16')) # to get from one point

```

## 📄 License
This project is licensed under the MIT License.

## ✨ Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss your proposal.
