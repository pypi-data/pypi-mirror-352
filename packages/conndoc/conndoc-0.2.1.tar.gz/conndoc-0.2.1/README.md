# Conndoc

Over the years, troubleshooting the root cause of connection problems has always given me headaches. It often required using multiple different tools and manually interpreting their results.

`conndoc` is a simple yet extensive command-line tool that aims to make connectivity diagnosis easier. It supports checks for ping, DNS, SSL, HTTP, and TCP, and provides a handy summary view.

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

## 🆘 Help
To see all available commands and options:
```bash
conndoc --help
```

You can provide either a domain name or a valid IP address as input to most commands.

---

## 🔍 Commands

### `summary`
Run all applicable checks and show a live summary table.
```bash
conndoc summary google.com
```

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

For IPs, DNS and SSL will be skipped automatically.

---

## 📦 Project Info
- Python 3.9+
- Dependencies: `typer`, `rich`, `httpx`

---

## 🗺 Roadmap

Here are some planned and upcoming features for `conndoc`:

- **ICMP latency graph**  
  Show ping latencies over time as simple terminal plots.

- **Traceroute support**  
  Trace the path packets take through the network and measure latency at each hop.

- **Port scan (safe mode)**  
  Scan a set of common TCP ports to identify open services safely and quickly.

- **Save and export results**  
  Export diagnostics in JSON or Markdown format for easier sharing or CI integration.

- **Cross-platform packaging**  
  Add better support for Windows installers and Linux `.deb` / `.rpm` distributions.

- **Plugin support**  
  Let users extend Conndoc with custom checks that integrate into the summary view.

---

## 🤝 Contributing

Contributions are very welcome! Whether it's fixing a bug, improving the documentation, or suggesting a new feature — every bit helps.

If you're unsure where to start, feel free to open an issue or check out the roadmap for ideas.  

By contributing, you agree that your code will be licensed under the [Apache License 2.0](LICENSE).

### Quick Start
- Fork the repository
- Create a new branch (`git checkout -b my-feature`)
- Make your changes
- Commit and push (`git commit -am 'Add feature' && git push`)
- Open a Pull Request 🚀

If you're adding a new feature, try to include a short demo or usage example.

Looking forward to seeing what you build!

---

## 📄 License
Apache License 2.0
