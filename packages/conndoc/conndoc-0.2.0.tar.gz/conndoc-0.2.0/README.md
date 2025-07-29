# Conndoc

**Conndoc** is a simple and extensive command-line tool for diagnosing network connectivity. It supports checks for ping, DNS, SSL, HTTP, TCP, and provides a summary view.

---

## 🚀 Installation

### 📦 pip
```bash
pip install conndoc
```

### 🍺 Homebrew (macOS)
```bash
brew tap hmerac/conndoc
brew install conndoc
```

---

## 🔍 Commands

### `ping`
Ping a host.
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
conndoc checkhttp https://google.com
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

## 🆘 Help
To see all available commands and options:
```bash
conndoc --help
```

You can provide either a domain name or a valid IP address as input to most commands.

---

## 📦 Project Info
- Python 3.9+
- Dependencies: `typer`, `rich`, `httpx`

---

## 📄 License
Apache License 2.0

---

Contributions welcome!
