
A beautiful ASCII candle timer that burns in your terminal for the exact number of minutes you specify!

## ✨ Features

- 🔥 **Animated flame** that flickers and dances
- 📏 **Melting candle** that gradually shrinks as time passes
- ⚡ **Performance options** - choose between simple or animated flames
- 🔧 **Customizable** - set any duration and verbosity level
- 🎨 **Beautiful ASCII Art** - enjoy the ambiance while you work

## 🚀 Installation

Install from PyPI:

```bash
pip install burning-candle
```

## 📖 Usage

### Basic Usage
```bash
# Light a 5-minute candle (default)
burning-candle

# Light a 25-minute candle
burning-candle -c 25

# Light a 10-minute candle with animation
burning-candle -c 10 -a 1

# Quiet mode (no startup messages)
burning-candle -c 15 -v 0
```

### Command Line Options

- `-c, --create`: Set candle burn time in minutes (default: 5)
- `-a, --animation`: Enable flame animation (0=simple, 1=animated, default: 0)
- `-v, --verbosity`: Control output verbosity (0=quiet, 1=verbose, default: 1)
- `--version`: Show version information
- `-h, --help`: Show help message

### Examples

```bash
# Perfect for Pomodoro technique (25 minutes)
burning-candle -c 25 -a 1

# Quick 2-minute break
burning-candle -c 2 -v 0

# Long meditation session (60 minutes)
burning-candle -c 60 -a 1
```

## 🎯 Use Cases

- **Pomodoro Technique**: Time your work sessions
- **Meditation**: Set a peaceful timer for mindfulness
- **Study Sessions**: Visual timer for focused work
- **Cooking**: Beautiful timer for kitchen tasks
- **Ambiance**: Just enjoy the cozy candle animation

## 🛠️ Development

To set up for development:

```bash
git clone https://github.com/yourusername/burning-candle.git
cd burning-candle
pip install -e .
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

---

*Enjoy your cozy terminal candle! 🕯️*

# =============================================================================
# LICENSE (MIT License)
# =============================================================================
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.