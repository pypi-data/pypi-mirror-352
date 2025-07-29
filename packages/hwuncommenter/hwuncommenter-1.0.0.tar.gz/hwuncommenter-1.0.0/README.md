# HwUncommenter

Universal comment remover for any programming language. Remove ALL comment lines from your source code files with a single command!

## Features

- 🚀 **Universal Support**: Works with ANY programming language
- 🔧 **Smart Detection**: Recognizes different comment styles
- 💯 **Complete Removal**: Removes ALL types of comments
- 🛡️ **Safe Processing**: Preserves string literals and code structure
- ⚡ **Fast & Efficient**: Process files quickly
- 🎯 **Simple Usage**: One command, instant results

## Supported Languages

- **C/C++**: `//` and `/* */`
- **Python**: `#` and `"""` docstrings
- **JavaScript/Java**: `//` and `/* */`
- **HTML/XML**: `<!-- -->`
- **CSS**: `/* */`
- **SQL**: `--` comments
- **Shell/Bash**: `#` comments
- **And many more!**

## Installation

```bash
pip install hwuncommenter
```

## Usage

```bash
HwUncommenter filename.py
HwUncommenter script.js
HwUncommenter style.css
HwUncommenter any_file.any_extension
```

## Examples

**Before:**
```python
# This is a comment
def hello():  # Another comment
    """This docstring will be removed"""
    print("Hello World")  # Inline comment
```

**After:**
```python
def hello():
    print("Hello World")
```

## About

**HwUncommenter** by **MalikHw47** - Making code cleaner, one file at a time!

## License

MIT License - feel free to use and modify!
