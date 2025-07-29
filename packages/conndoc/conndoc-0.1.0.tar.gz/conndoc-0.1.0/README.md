# conndoc

**conndoc** is a simple and elegant command-line tool for diagnosing network connectivity and infrastructure issues. It supports checks for ping, DNS, SSL, HTTP, TCP, and provides a summary view.

---

## 🚀 Installation

Install via [Poetry](https://python-poetry.org/):

```bash
poetry install
```

Or, if packaged and published to PyPI:

```bash
pip install conndoc
```

Run it using Poetry:

```bash
poetry run conndoc --help
```

---

## 🔍 Commands

### `ping`
Ping a host 3 times.
```bash
conndoc ping google.com
```

### `checkdns`
Resolve a domain's DNS to IP addresses.
```bash
conndoc checkdns google.com
```

### `checkssl`
Inspect SSL certificate details (only for domains).
```bash
conndoc checkssl google.com
```

### `checkhttp`
Send an HTTP GET request and show basic diagnostics.
```bash
conndoc checkhttp https://example.com
```

### `checktcp`
Check if a TCP port is open.
```bash
conndoc checktcp google.com 443
```

### `summary`
Run all applicable checks and show a live summary table.
```bash
conndoc summary google.com
```

For IPs, DNS and SSL will be skipped automatically.

---

## 📄 License
To be defined by the author.

---

## 👨‍💻 Author
**Mert Acikportali**  
📧 mertacikportali@gmail.com

Contributions welcome after license is defined!