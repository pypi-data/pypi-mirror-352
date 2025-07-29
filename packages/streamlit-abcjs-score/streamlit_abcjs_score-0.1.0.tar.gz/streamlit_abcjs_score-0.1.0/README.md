# Streamlit ABC.js Score Renderer

A Streamlit component for rendering ABC notation as beautiful sheet music using the abc.js library.

## Features

- 🎵 **Real-time rendering** of ABC notation as sheet music
- 📱 **Responsive design** that adapts to container size
- 🎛️ **Customizable options** (scale, dimensions, styling)
- 🔧 **Error handling** with helpful error messages
- 📚 **Built-in examples** for quick testing
- 🎨 **Theme support** matching Streamlit's active theme

## Installation

```bash
pip install streamlit-abcjs-score
```

## Quick Start

```python
import streamlit as st
from streamlit_abcjs_score import abc_score

# Simple example
notation = """T: Twinkle, Twinkle, Little Star
M: 4/4
L: 1/4
K: C
|: C C G G | A A G2 | F F E E | D D C2 :|"""

abc_score(notation=notation)
```

## Usage

### Basic Usage

```python
from streamlit_abcjs_score import abc_score

# Render ABC notation
abc_score(
    notation="T: My Song\nM: 4/4\nL: 1/4\nK: C\nC D E F | G A B c |",
    height=400,
    scale=1.0
)
```

### Advanced Usage

```python
from streamlit_abcjs_score import abc_score, get_example_notation

# Use built-in examples
cooley_reel = get_example_notation("cooley_reel")
abc_score(
    notation=cooley_reel,
    height=500,
    scale=1.2,
    responsive=True,
    key="my_score"
)
```

### Available Examples

```python
from streamlit_abcjs_score import list_examples, get_example_notation

# List all available examples
examples = list_examples()
print(examples)  # ['twinkle_star', 'cooley_reel', 'mary_had_lamb']

# Get specific example
notation = get_example_notation("twinkle_star")
```

## API Reference

### `abc_score(notation, height=400, width=None, scale=1.0, responsive=True, key=None)`

Render ABC notation as sheet music.

**Parameters:**

- `notation` (str): The ABC notation string to render
- `height` (int, optional): Height of the container in pixels (default: 400)
- `width` (int, optional): Width of the container in pixels (default: auto)
- `scale` (float, optional): Scale factor for the rendered score (default: 1.0)
- `responsive` (bool, optional): Whether to make the score responsive (default: True)
- `key` (str, optional): Unique key for the component

### `get_example_notation(name)`

Get example ABC notation by name.

**Parameters:**
- `name` (str): Name of the example ("twinkle_star", "cooley_reel", "mary_had_lamb")

**Returns:**
- `str`: The ABC notation string

### `list_examples()`

List all available example names.

**Returns:**
- `list`: List of available example names

## ABC Notation Primer

ABC notation is a shorthand form of musical notation. Here are the basics:

- `T:` Title
- `M:` Meter (time signature, e.g., 4/4, 3/4)
- `L:` Default note length (e.g., 1/4, 1/8)
- `K:` Key signature (e.g., C, G, Am)
- `|` Bar lines
- Notes: `A`, `B`, `C`, `D`, `E`, `F`, `G` (lowercase for higher octave)
- Rests: `z`
- Accidentals: `^` (sharp), `_` (flat), `=` (natural)

### Example:

```
T: Mary Had a Little Lamb
M: 4/4
L: 1/4
K: C
E D C D | E E E2 | D D D2 | E G G2 |
E D C D | E E E2 | D D E D | C4 |
```

## Development

### Setup

1. Clone the repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Install Node.js dependencies: `cd streamlit_abcjs_score/frontend && npm install`

### Building

1. Build the frontend: `cd streamlit_abcjs_score/frontend && npm run build`
2. Install the package: `pip install -e .`

### Testing

Run the example app:
```bash
streamlit run example.py
```

## Next Steps

To complete the setup:

1. **Install frontend dependencies**:
   ```bash
   cd streamlit_abcjs_score/frontend
   npm install
   ```

2. **Build the frontend**:
   ```bash
   npm run build
   ```

3. **Install the package locally**:
   ```bash
   pip install -e .
   ```

4. **Run the example**:
   ```bash
   streamlit run example.py
   ```

## Resources

- [ABC Notation Standard](http://abcnotation.com/)
- [ABC.js Documentation](https://abcjs.net/)
- [Streamlit Components Documentation](https://docs.streamlit.io/library/components)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
