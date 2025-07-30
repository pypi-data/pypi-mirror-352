<div align="center">
  <h1>yors_pano_ansi_color</h1>
  <p>
    <strong>🤖 A python library to print color text in console for developers in development.</strong>
  </p>
  
  ![PyPI - Version](https://img.shields.io/pypi/v/yors_pano_ansi_color)
  ![PyPI - License](https://img.shields.io/pypi/l/yors_pano_ansi_color)

</div>

to print color text in console for developers.

## Why

- info msg,warn,error color text easily.
- share commom code in each package.

## 1 - install python package

```bash
pip install yors_pano_ansi_color
```

## 2 - use it in your python code

- in some comfyui custom nodes project or module

- code in your `node_xx.py`

```py
from yors_pano_ansi_color import log_msg,log_warn,log_error
log_msg(f"[pano] hi, zero! this is pano.")
log_warn(f"[pano] hi, zero! this is pano.")
log_error(f"[pano] hi, zero! this is pano.")
```

## Author

ymc-github <ymc.github@gmail.com>

## License

MIT
