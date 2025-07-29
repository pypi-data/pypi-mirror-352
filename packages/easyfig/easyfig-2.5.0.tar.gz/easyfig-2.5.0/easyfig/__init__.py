"""
Easyfig is a Python library for researchers to create figures for academic papers!
It depends on SymPy, and other external libraries for things like plotting support.

See the webpage for more information and documentation:

    https://github.com/Jesse-tien/Easyfig

"""

import sys
if sys.version_info < (3, 8):
    raise ImportError("Python version 3.8 or above is required for Easyfig.")
del sys

__docformat__ = "restructuredtext"

# Let users know if they're missing any of our hard dependencies
_hard_dependencies = (
	"numpy",
	"sympy",
	"matplotlib",
	"IPython",
	"notebook",
    "pyperclip",
    "qrcode"
)
_missing_dependencies = []

for _dependency in _hard_dependencies:
    try:
        __import__(_dependency)
    except ImportError as _e:  # pragma: no cover
        _missing_dependencies.append(f"{_dependency}: {_e}")

if _missing_dependencies:  # pragma: no cover
    raise ImportError(
        "Unable to import required dependencies:\n" + "\n".join(_missing_dependencies)
    )
del _hard_dependencies, _dependency, _missing_dependencies

from .main import (
    gen_letters,
    gen_romans,
    mathshow,
    showlatex,
    mathprint,
    exist_file,
    save_var,
    get_var,
    data_lines,
    draw_lines,
    draw_3D,
    draw_max_area,
    draw_detail_area,
    makefig,
    make_example
)

from sympy import (
    symbols,
    Symbol,
)

from sympy.printing import latex

__version__ = '2.5.0'

# module level doc-string
__doc__ = """
### 主要功能：
- 1. data_lines: 给定数据点画线图；
- 2. draw_lines: 给定Symbol函数，和一个参数，画数值仿真图；
- 3. draw_3D: 给定Symbol函数，和两个参数，画三维数值仿真图；
- 4. draw_max_area: 给定Symbol函数，和两个参数，画各函数最大区域图；
- 5. draw_detail_area: 给定Symbol函数，和两个参数，画不同函数关系所在区域。
- 6. gen_letters: 生成N个连续大写字母；
- 7. gen_romans: 生成N个连续罗马数字；
- 8. mathshow: 给定latex代码，在Jupyter中显示公式；
- 9. showlatex: 显示symbol表达式的latex代码；
- 10. mathprint: 在Jupyter中规范地输出symbol公式；
- 11. exist_file: 判断文件是否存在；
- 12. save_var/get_var: 保存/获取Python变量（基于pickle）。
- 13. makefig: 启动向导界面，无需编写代码完成快速绘图，并自动生成python代码。

### Main Functions:
1. **data_lines**: Draw a line graph for given data points.
2. **draw_lines**: Given a symbolic function and one parameter, draw a numerical simulation graph.
3. **draw_3D**: Given a symbolic function and two parameters, draw a 3D numerical simulation graph.
4. **draw_max_area**: Given a symbolic function and two parameters, draw a graph of the maximum area for each function.
5. **draw_detail_area**: Given a symbolic function and two parameters, draw a graph showing the areas where different function relationships exist.
6. **gen_letters**: Generate N consecutive uppercase letters.
7. **gen_romans**: Generate N consecutive Roman numerals.
8. **mathshow**: Display a formula in Jupyter given LaTeX code.
9. **showlatex**: Display the LaTeX code for a symbolic expression.
10. **mathprint**: Properly output a symbolic formula in Jupyter.
11. **exist_file**: Check if a file exists.
12. **save_var/get_var**: Save/retrieve Python variables (based on pickle).
13. **makefig**: Launch the wizard interface, complete rapid plotting without writing code, and automatically generate Python code.


See the webpage for more information and documentation:

    https://github.com/Jesse-tien/Easyfig
    
"""

# Use __all__ to let type checkers know what is part of the public API.
__all__ = [
    "gen_letters",
    "gen_romans",
    "mathshow",
    "showlatex",
    "mathprint",
    "exist_file",
    "save_var",
    "get_var",
    "data_lines",
    "draw_lines",
    "draw_3D",
    "draw_max_area",
    "draw_detail_area",
    "symbols",
    "Symbol",
    "latex",
    "makefig",
    "make_example"
]
