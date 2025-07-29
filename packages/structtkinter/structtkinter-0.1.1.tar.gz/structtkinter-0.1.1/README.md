# structtkinter

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green)]()

A CSS-like, HTML-inspired UI framework built on top of Tkinter.

---

## Features

- **Canvas-based rendering** for full control over shapes, shadows, and transforms
- **CSS-style styling** with classes, IDs, and tag selectors
- **External "CSS" & "JS" separation** via Python modules
- **Flexbox-like layout** (vertical stacking by default)
- Support for **`%`**, **`fit-content`**, and **fixed** dimensions
- **Pseudo-states & transitions** (coming soon!)

---

## Prerequisites

- Python **3.7** or newer
- Tkinter (typically included with standard Python installs)

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/structtkinter.git
cd structtkinter
# (Optionally) create a virtualenv:
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.\.venv\Scripts\activate   # Windows

# Run the example:
python examples/example1/stk/index.py
