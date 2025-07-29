


# Easy HTTP Server

This is a simple HTTP server for Raspberry Pi or PC that can:

* ✅ Display custom HTML files
* ✅ Respond to custom POST requests (e.g. save form input to `output.txt`)
* ✅ Enable static file serving using the `webserverautofile` switch

---

## 📦 Usage

```python
from easy_http import EasyHTTPServer

server = EasyHTTPServer(
    ip='auto',
    port=8000,
    webserverautofile=True,
    webdir=None,
    custom_html_path=None
)
server.start()
```

---

## ⚙️ Arguments

| Argument            | Type   | Default       | Description                                                      |
| ------------------- | ------ | ------------- | ---------------------------------------------------------------- |
| `ip`                | `str`  | `'auto'`      | IP address to bind (`'auto'`, `'localhost'`, or a specific IP)   |
| `port`              | `int`  | `8080`        | Port to run the server on                                        |
| `webserverautofile` | `bool` | `False`       | If `True`, serves files from directory like a static file server |
| `webdir`            | `str`  | `os.getcwd()` | Directory to serve when `webserverautofile=True`                 |
| `custom_html_path`  | `str`  | `None`        | Path to custom HTML file (used when `webserverautofile=False`)   |

---

ℹ️ When `webserverautofile` is `False` and `custom_html_path` is not provided, the server shows a simple form and saves input to `output.txt`.

---

🔧 Simple, light, and useful for local web control panels or project dashboards!

