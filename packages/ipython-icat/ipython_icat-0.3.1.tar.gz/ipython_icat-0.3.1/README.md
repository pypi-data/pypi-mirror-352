# ipython-icat

[![PyPI version](https://img.shields.io/pypi/v/ipython-icat.svg?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/ipython-icat/)

## Installation

You can install `ipython-icat` using pip:

```bash
pip install ipython-icat
```

## Requirements

- Python 3.9+
- IPython
- matplotlib
- Pillow (PIL)
- terminal emulator with support for kitty graphics protocol (KGP) e.g., kitty, ghostty

## Usage

### Loading the Extension

In your IPython session, load the extension:

```python
%load_ext icat
```

### Displaying Matplotlib Plots

To use the kitty backend for matplotlib:

```python
%plt_icat
```

After running this command, any matplotlib plots you create will be displayed directly in your kitty terminal.

### Use as a Default Backend

To set the kitty backend for matplotlib as the default, add the following lines to your IPython configuration file:

1. `c.InteractiveShellApp.extensions = ['icat']`
2. `c.InteractiveShellApp.exec_lines = ['%plt_icat']`

#### Automatic Setup

You can quickly set up IPython to use the icat extension using the setup command:

```bash
python -m icat setup
```

This command will:
1. Create an IPython profile if it doesn't exist (or use an existing one)
2. Configure the profile to load the icat extension automatically
3. Set matplotlib to use the icat backend by default

Additional options:
- `--profile NAME` - Use a specific profile instead of the default
- `--ipython-path PATH` - Specify a custom path to the .ipython directory

Example with custom profile:
```bash
python -m icat setup --profile myprofile
```

### Displaying Images

To display an image file or a PIL Image object:

```python
%icat path/to/your/image.jpg
```

or

```python
from PIL import Image
img = Image.open('path/to/your/image.jpg')
%icat img
```

You can also resize the image when displaying:

```python
%icat path/to/your/image.jpg -w 300 -h 200
```

### Using Ghostty

If you'd like to use this plugin with Ghostty, make sure to install the [static kitten binary](https://github.com/kovidgoyal/kitty/releases) which will allow you to run `kitten icat`.

## Features

- Display matplotlib plots directly in kitty terminal
- Show PIL Image objects or image files
- Resize images on display
- Seamless integration with IPython workflow

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [matplotlib-backend-kitty](https://github.com/jktr/matplotlib-backend-kitty) for the original implementation
- [matplotlib](https://github.com/matplotlib/matplotlib) and [Pillow](https://python-pillow.org/) for their excellent libraries
- [kitty terminal](https://github.com/kovidgoyal/kitty) for developing the graphics protocol

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
