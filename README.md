# ⚡ CalcPro Ultra

> A beautiful, feature-rich desktop calculator built with Python — faster and more capable than the Windows built-in Calculator.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.x-blueviolet?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📸 Preview

```
┌─────────────────────────────────┐
│  Normal │ Scientific │ Currency │ Units │ History │
├─────────────────────────────────┤
│                                 │
│                          1,234  │
│                                 │
├──────┬──────┬──────┬────────────┤
│  MC  │  MR  │  M+  │     M-     │
├──────┼──────┼──────┼────────────┤
│  AC  │  +/- │   %  │     ÷      │
├──────┼──────┼──────┼────────────┤
│   7  │   8  │   9  │     ×      │
├──────┼──────┼──────┼────────────┤
│   4  │   5  │   6  │     -      │
├──────┼──────┼──────┼────────────┤
│   1  │   2  │   3  │     +      │
├────────────┬──────┼────────────┤
│     0      │   .  │     =      │
└────────────┴──────┴────────────┘
```

---

## ✨ Features

### 🔢 Normal Mode
Standard calculator with the same familiar layout as Windows Calculator.

- Basic arithmetic: `+` `−` `×` `÷`
- Percentage calculations with context awareness (e.g. `200 + 5%` = `210`)
- Toggle sign (`+/−`)
- Full memory bank: **MC, MR, M+, M−**
- Live expression shown above the display
- **AC** clears everything · **CE** clears current entry only

### 🔬 Scientific Mode
Everything in Normal mode, plus a full row of scientific functions.

| Function | Description |
|----------|-------------|
| `sin` `cos` `tan` | Trigonometry (DEG or RAD) |
| `sin⁻¹` `cos⁻¹` `tan⁻¹` | Inverse trig |
| `log` `ln` | Base-10 and natural log |
| `√` `∛` | Square root & cube root |
| `x²` `x³` `xⁿ` | Powers |
| `1/x` | Reciprocal |
| `n!` | Factorial (up to 170) |
| `eˣ` `10ˣ` | Exponentials |
| `π` `e` | Constants |
| **DEG / RAD** | Toggle angle mode |
| **MS** | Memory store (5th memory key) |

### 💱 Currency Converter
Live exchange rates fetched automatically on startup.

- **22 currencies** supported: USD, EUR, GBP, JPY, BDT, CAD, AUD, CHF, CNY, INR, SGD, AED, SAR, MYR, THB, KRW, BRL, MXN, ZAR, HKD, TRY, NZD
- Fetches real-time rates from `exchangerate-api.com`
- Falls back to built-in offline rates if no internet
- **Swap button** to instantly reverse conversion direction
- Built-in numpad — no need to type

### 📐 Unit Converter
6 categories, all with a swap button and dedicated numpad.

| Category | Units |
|----------|-------|
| **Length** | mm, cm, m, km, inch, ft, yard, mile |
| **Weight** | mg, g, kg, oz, lb |
| **Temperature** | °C, °F, K |
| **Area** | cm², m², km², ft², acre |
| **Speed** | m/s, km/h, mph, knot |
| **Data** | byte, KB, MB, GB, TB |

### 🕐 History
Full log of all calculations with timestamps.

- Stores up to **80 recent calculations**
- Shows expression and result for each entry
- **Click any entry** to restore that result to the calculator
- One-click **Clear All**

---

## 🚀 Getting Started

### Prerequisites

- Python **3.8 or newer**
- pip

### Installation

**1. Clone or download the file**

```bash
git clone https://github.com/yourname/calcpro-ultra.git
cd calcpro-ultra
```

Or simply download `calculator.py`.

**2. Install the dependency**

```bash
pip install customtkinter
```

**3. Run it**

```bash
python calculator.py
```

On Windows you can also double-click `calculator.py` if Python is associated with `.py` files.

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `0` – `9` | Enter digits |
| `+` `-` `*` `/` | Operators |
| `.` | Decimal point |
| `Enter` or `=` | Calculate result |
| `Backspace` | Delete last digit |
| `Escape` | Clear (AC) |
| `%` | Percent |

> Keyboard input works in **Normal** and **Scientific** modes.

---

## 🏗️ Project Structure

```
calculator.py        ← Single-file app, no extra files needed
README.md            ← This file
```

All logic, UI, and data are contained in one file for easy portability.

---

## 🛠️ Tech Stack

| Library | Purpose |
|---------|---------|
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Modern dark-themed UI widgets |
| `tkinter` | Underlying GUI framework (built into Python) |
| `math` | Scientific calculations |
| `threading` | Non-blocking live rate fetch |
| `urllib.request` | Fetching exchange rates |
| `json` | Parsing API response |

---

## 🎨 Design

- **Size:** 322 × 502 px (matches Windows Calculator default)
- **Theme:** Dark mode with accent blue (`#4a9eff`)
- **Font:** Segoe UI (Windows native)
- **Resizable:** Yes — scales up to 600 × 900 px
- Inspired by the clean, minimal layout of the Windows 11 Calculator

---

## 🔧 Customization

You can easily tweak colors at the top of `calculator.py`:

```python
BG    = "#1c1c1c"   # window background
S1    = "#2d2d2d"   # number button color
S2    = "#333333"   # operator button color
S3    = "#666666"   # utility button color (AC, %)
EQ    = "#4a9eff"   # equals button color
ACC   = "#4a9eff"   # accent / operator text color
```

To add more currencies, append to the `CURRENCIES` list and add a fallback rate to `FALLBACK`.

To add more unit categories, add a new entry to the `UNITS` dictionary following the existing format.

---

## 📋 Requirements

```
customtkinter>=5.0.0
```

Python's standard library handles everything else (`tkinter`, `math`, `json`, `threading`, `urllib`).

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute it.

---

## 🙏 Acknowledgements

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) by Tom Schimansky
- Exchange rates powered by [ExchangeRate-API](https://www.exchangerate-api.com)
- Inspired by Windows Calculator

---

<p align="center">Made with ❤️ and Python</p>
