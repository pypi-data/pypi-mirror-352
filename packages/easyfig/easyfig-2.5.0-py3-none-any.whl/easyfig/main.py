# Author: Yu-Xin Tian, 2025-06-01 Version 3.0.0

sympy_names = ['Abs', 'exp', 'oo', 'sqrt', 'root', 'log', 'ln', 'integrate', 'diff', 'limit', 'summation', 'product', 'sin', 'cos', 'tan',
'csc', 'sec', 'cot', 'sinh', 'cosh', 'tanh', 'coth', 'acos', 'acosh', 'acot', 'acoth', 'acsc', 'acsch',  'asec', 'asech', 'asin', 'asinh', 'atan', 'atan2', 'atanh',
 'csch', 'cse', 'Mod',  'pi', 'sech',  'sinc', 'floor', 'ceiling', 'Piecewise', 'Rational', 'Number']
greek_letters =['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu',
          'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
          'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda', 'Mu',
          'Nu', 'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega']
from sympy import *
import qrcode
from itertools import permutations, product
from matplotlib.font_manager import FontProperties
import matplotlib.colors as mcolors
import numpy as np
import os, pickle
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import copy
import matplotlib.ticker as ticker
from matplotlib import rcParams

from IPython.display import display
from IPython.display import Math
from sympy.printing import latex

from sympy.parsing.latex import parse_latex
import pyperclip
import importlib.util
import subprocess

import string
import re
import platform
import ast

# 设置 matplotlib 字体为支持中英文的字体
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

config = {
    "font.family":'serif',
    "font.size": 12,
    "mathtext.fontset":'stix',
    "font.serif": ['SimSun'],
}
rcParams.update(config)
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'

c_list = ['blue', 'gold', 'green', 'red', 'darkgoldenrod', 'darkcyan', 'indigo',
          'chocolate', 'olivedrab', 'teal', 'navy', 'firebrick','darkgreen', 'purple', 'cadetblue']
m_list = ['o','s', '*', 'P', 'X', 'D', 'p', 'x', '8', '2', 'H', '+', '|', '<', '>', '^', 'v', ',']
ls_list = ['-', (0, (1, 10)), (0, (5, 10)),'-.','--', ':', (0, (3, 10, 1, 10, 1, 10)), (5, (10, 3)), (0, (5, 5)), (0, (5, 1))]
locations = {
    'best': 0,
    'northeast': 1,
    'northwest': 2,
    'southwest':3,
    'southeast':4,
    'east':7,
    'west':6,
    'south':8,
    'north':9,
    'center':10
}


def check_hex_color(color):
    # 正则表达式检查是否为十六进制颜色（# 开头，后面跟 3 或 6 个十六进制字符）
    pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    return bool(pattern.match(color))

def make_example(fun_name):
    welcome = "Welcome to use the tools for thesis simulation drawing. The available functions include `data_lines`, `draw_lines`, `draw_3D`, `draw_max_area`, `draw_detail_area`, etc." + \
              "\nIf you want to display high-definition pictures in Jupyter, please use `%config InlineBackend.figure_format = " + "'retina'`." + \
              "\nIf you want to generate example code, please run the function`make_example(<data_lines/draw_lines/draw_3D/draw_max_area/draw_detail_area>)`." + \
              "\n欢迎使用论文模拟绘图工具。可用功能包括 `data_lines`(由数据点画线), `draw_lines`(符号函数仿真画线), `draw_3D`(符号函数仿真画3维图), `draw_max_area`(符号函数俩参数分析-“最大区域图”), `draw_detail_area`(符号函数俩参数分析-“不同关系区域图”) 等。" + \
              "\n如果您想在 Jupyter 中显示高清图片，请使用 `% config InlineBackend.figure_format = 'retina'`。" + \
              "\n如果你想生成实例代码，请运行函数`make_example(<data_lines/draw_lines/draw_3D/draw_max_area/draw_detail_area>)`。"

    data_lines_code = r"""
# 以方括号（列表、numpy数组均可）形式给出数据，并给这组数据起个名字：
data = {
    '景区1旅游人次': [1230, 45789, 2600, 320, 991480, 65780, 89990, 70001, 6423, 415000, 340, 102],
    '景区2旅游人次': [800, 34000, 1690, 139, 76788, 453565, 87898, 64302, 3423, 325001, 127, 13],
    '景区3旅游人次': [5230, 65789, 7600, 820, 1091480, 85780, 99995, 90001, 9423, 705000, 640, 707],
}

# 给横轴添加刻度标签，注意要和data长度一致！
label_x = ['2020-1', '2020-2', '2020-3', '2020-4',  '2020-5', '2020-6',  '2020-7',  '2020-8',  '2020-9',  
           '2020-10',  '2020-11',  '2020-12']

# 自定义xy轴名称：
x_name = '月总旅游人次'
y_name = '月份'

# 保存路径
save_dir = 'data_sigle.tiff'

# 图例的方位，可以选填的内容有'best','northeast','northwest','southwest','southeast','east','west','south','north','center'。
# 默认值为'best'，表示自动安排至合适的位置。
location = 'best'
# 图例的列数，默认为1列，即竖着排布。
ncol = 1

fsize = 14 # 图片中字号的大小，默认值为14。
figsize = [7, 5] # 图片的大小，写成`[宽, 高]`的形式。

# 横轴刻度标签旋转角度。用于刻度为年份，横着挤不下的情况，可以设成45度，错开排布。默认不旋转，即0度。
xt_rotation = 45

# 横轴名字标签旋转角度，默认值0，基本不需要动。
xrotation = 0
# 纵轴名字标签旋转角度，默认值90，字是正的。如果y轴的名字较长，不好看，可以设成0，字是竖倒着写的，紧贴y轴。
yrotation = 90 

# 一组线的形状，如实线'-'，点横线'-.'，虚线'--'，点线':'。
linestyles = ['-', '-.','--'] 
linewidth = 1.2 # 线粗。

markers = ['o','s', '*'] # 线上的标记符号,关于标记符号的详细说明 https://matplotlib.org/stable/api/markers_api.html#module-matplotlib.markers
markersize = 3.5 # 标记符号的大小，默认3.5。
# 四条线的颜色
colors = ['blue','red','green']

isgrid = False # 是否要网格。要就填True，不要就是False，默认不要。
# x/y轴刻度值距离横轴的距离
xpad = 3
ypad = 3
# x/y轴名字标签距离横轴刻度的距离。
xlabelpad = 3
ylabelpad = 3

# 传给data_lines函数 (不要改！)
# Passed to the data_lines function (Don't change!).
data_lines(data, label_x=label_x, x_name=x_name, y_name=y_name, save_dir=save_dir, location=location, ncol=ncol,
           fsize=fsize, figsize=figsize, xt_rotation=xt_rotation, xrotation=xrotation, yrotation=yrotation, 
           linestyles=linestyles, linewidth=linewidth, markers=markers, markersize=markersize, colors=colors,
          isgrid=isgrid, xpad=xpad, ypad=ypad, xlabelpad=xlabelpad, ylabelpad=ylabelpad)
    """

    draw_lines_code = r"""
# 定义符号
alpha, b, c_n, c_r, delta, e, e_n, e_r, k, p_e = symbols('alpha, b, c_n, c_r, delta, e, e_n, e_r, k, p_e')

# 表达式
expressions = {
	r'$\pi_r^{NW}$': e*p_e+(k*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2)/(8*(k+alpha*delta*(1-alpha*delta))**2),
	r'$\pi_r^{BW}$': e*p_e + ( k*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/( 8*(k+delta-delta**2)**2),
	r'$\pi_r^{NS}$': e*p_e + ((k+2*alpha*delta)*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2 )/( 8*(k+alpha*delta*(2-alpha*delta))**2),
	r'$\pi_r^{BS}$': e*p_e + ( (k+2*delta)*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/( 8*(k+2*delta-delta**2)**2),
}

# 参数赋值
assigns = {alpha : 0.9, c_n : 0.2, c_r : 0.1, delta : 0.8, e : 2.0, e_n : 1.0, e_r : 0.6, k : 1.1, p_e : 0.1}

# 要分析的参数，及其取值范围
the_var = b
ranges = [0, 0.08, 0.01]

# xy轴的名字
x_name = r'(a) Parameter $b$'
y_name = r'$\pi_r$'

# 图片保存路径、文件名
save_dir = None

# 图例的方位
location = 'best'

# 图例的列数
ncol = 1

# 图片中字号的大小
fsize = 14

# 图片大小
figsize = [6, 5]

# x轴刻度及轴标签旋转
xt_rotation = 0
xrotation = 0
yrotation = 0

# 线的风格
linestyles = ['-', (0, (5, 5)), '--', '-.', None]

# 线粗，默认均1.0
linewidth = [1.5, 1.5, 1.5, 1.5] 

# 线上的标记符号
markers = ['o', 's', '*', 'P']

# 标记符号的大小，默认均3.5。
markersize = [4.0, 4.0, 4.0, 4.0]

# 线的颜色
colors = ['red', 'blue', 'black', 'chocolate']

# 去除网格
isgrid = False

# 分别为x/y轴刻度值距离横轴的距离。
xpad = 3
ypad = 3

# 分别为x/y轴名字标签距离纵轴刻度的距离。
xlabelpad = 9
ylabelpad = 9

# 坐标轴字体大小
xlabelsize = 'auto'
ylabelsize = 'auto'
legendsize = 'auto'

# 传给draw_lines函数
the_plt = draw_lines(expressions=expressions, assigns=assigns, the_var=the_var, ranges=ranges, x_name=x_name, y_name=y_name, 
    save_dir=save_dir, location=location, ncol=ncol, fsize=fsize, figsize=figsize, xt_rotation=xt_rotation,
    xrotation=xrotation, yrotation=yrotation, linestyles=linestyles, linewidth=linewidth, markers=markers,
    markersize=markersize, colors=colors, isgrid=isgrid, xpad=xpad, ypad=ypad, xlabelpad=xlabelpad, ylabelpad=ylabelpad,
    xlabelsize=xlabelsize, ylabelsize=ylabelsize, legendsize=legendsize)
the_plt.show()
    """

    draw_3D_code = r"""
# 定义符号
alpha, b, c_n, c_r, delta, e, e_n, e_r, k, p_e = symbols('alpha, b, c_n, c_r, delta, e, e_n, e_r, k, p_e')

# 表达式
expressions = {
	r'$\pi_r^{NW}$': e*p_e+(k*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2)/(8*(k+alpha*delta*(1-alpha*delta))**2),
	r'$\pi_r^{BW}$': e*p_e + ( k*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/( 8*(k+delta-delta**2)**2),
	r'$\pi_r^{NS}$': e*p_e + ((k+2*alpha*delta)*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2 )/( 8*(k+alpha*delta*(2-alpha*delta))**2),
	r'$\pi_r^{BS}$': e*p_e + ( (k+2*delta)*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/( 8*(k+2*delta-delta**2)**2),
}

# 参数赋值
assigns = {c_n:0.2, c_r:0.1, delta:0.8, e:2.0, e_n:1.0, e_r:0.6, k:1.1, p_e:0.1}

# 要分析的参数，及其取值范围
the_var_x = alpha
start_end_x = [0.7, 0.8] 
the_var_y = b
start_end_y = [0, 0.08] 

# xy轴的名字
x_name = r'$\alpha$' 
y_name = r'$b$'  
z_name = r'$\pi_r$'

# 图片保存路径、文件名
save_dir = None 

# 曲面的透明度。取值范围0到1，浮点数。0表示全透明，1表示完全不透明。
color_alpha = [0.8, 0.8, 0.8, 0.8] 

# 图例的方位，可以选填的内容有'best','northeast','northwest','southwest','southeast','east','west','south','north','center'。
location = 'north' 

# 图例的列数，默认为1列，即竖着排布。
ncol = 4

# 图片中字号的大小
fsize = 14

# 图片的大小，写成`[宽, 高]`的形式。默认为`[7, 5]`。
figsize = [7, 5]

# xrotation/yrotation: x/y轴名字标签旋转角度，默认值0，基本不需要动。
xrotation = 0
yrotation = 0

# Z轴名字标签旋转角度，默认值90，字是正的。如果Z轴的名字较长，不好看，可以设成0，字是竖倒着写的，紧贴Z轴
zrotation = 90

# 是否要网格。要就填True，不要就是False
isgrid = True

# 在多面图中用于按顺序制定每个面的颜色（包含标记符号的颜色）。
colors = ['red', 'blue', 'darkgoldenrod', 'green']

# 曲面上线框的颜色。若为None，则曲面上不画线。当该参数不为None时，参数`linestyles`，`linewidth`和`density`才起作用。
edgecolor = 'black'
linestyles = ['-', '--', '-.', ':', None, (0, (1, 10)), (0, (5, 10)), (0, (3, 10, 1, 10, 1, 10)), (5, (10, 3)), (0, (5, 5)), (0, (5, 1))]
# 线粗
linewidth = 0.5 
# 曲面上画线的密度，也就是曲面横纵方向各画多少根线。
density = 50 

# 仰角 (elevation)。定义了观察者与 xy 平面之间的夹角，也就是观察者与 xy 平面之间的旋转角度。
elevation = 15

# 方位角 (azimuth)。定义了观察者绕 z 轴旋转的角度。它决定了观察者在 xy 平面上的位置。
azimuth = 45

# 左、下、右、上的图片留白，默认分别为0,0,1,1。不需要动，除非不好看。
left_margin = 0
bottom_margin = 0
right_margin = 1
top_margin = 1

# 分别为/y/z轴刻度值距离横轴的距离。
xpad = 3
ypad = 3
zpad = 3

# 分别为/y/z轴名字标签距离纵轴刻度的距离。
xlabelpad = 10
ylabelpad = 10
zlabelpad = 10

# 自定义坐标轴字体大小，默认'auto'，自动和fsize一样大
xlabelsize = 'auto'
ylabelsize = 'auto'
zlabelsize = 'auto'
legendsize = 'auto'

# 传给draw_3D函数 (不要改！)
# Passed to the draw_3D function (Don't change!)
the_plt = draw_3D(expressions=expressions, assigns=assigns, the_var_x=the_var_x, start_end_x=start_end_x, the_var_y=the_var_y, 
        start_end_y=start_end_y, x_name=x_name, y_name=y_name, z_name=z_name, 
        save_dir=save_dir, color_alpha=color_alpha, location=location, ncol=ncol, fsize=fsize, figsize=figsize, 
        xrotation=xrotation, yrotation=yrotation, zrotation=zrotation, isgrid=isgrid, colors=colors, 
        edgecolor=edgecolor, linestyles=linestyles, linewidth=linewidth, density=density, elevation=elevation, azimuth=azimuth, 
        left_margin=left_margin, bottom_margin=bottom_margin, right_margin=right_margin, top_margin=top_margin,
        xpad=xpad, ypad=ypad, zpad=zpad, xlabelpad=xlabelpad, ylabelpad=ylabelpad, zlabelpad=zlabelpad,
       xlabelsize=xlabelsize, ylabelsize=ylabelsize, zlabelsize=zlabelsize, legendsize=legendsize)
the_plt.show()
"""
    draw_max_area_code = r"""
# 定义符号
alpha, b, c_n, c_r, delta, e, e_n, e_r, k, p_e = symbols('alpha, b, c_n, c_r, delta, e, e_n, e_r, k, p_e')

# 表达式
expressions = {
	r'$\pi_r^{NW}$': e*p_e+(k*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2)/(8*(k+alpha*delta*(1-alpha*delta))**2),
	r'$\pi_r^{BW}$': e*p_e + ( k*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/( 8*(k+delta-delta**2)**2),
	r'$\pi_r^{NS}$': e*p_e + ((k+2*alpha*delta)*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2 )/( 8*(k+alpha*delta*(2-alpha*delta))**2),
	r'$\pi_r^{BS}$': e*p_e + ( (k+2*delta)*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/( 8*(k+2*delta-delta**2)**2),
}

# 参数赋值
assigns = {c_n: 0.2, c_r: 0.1, delta: 0.8, e: 2.0, e_n: 1.0, e_r: 0.6, k: 1.1, p_e: 0.1}

# 要分析的参数，及其取值范围
the_var_x = alpha
start_end_x = [0.7, 0.8] 
the_var_y = b
start_end_y = [0, 0.08] 

# xy轴的名字
x_name = r'(b) With blockchain' 
y_name = r'$b$'  

# 图片保存路径、文件名
save_dir = None 

# 四个表达式分别达到最大时显示的标签、区域背景颜色和区域图案。
texts = ['NW', 'BW', 'NS', 'BS']
colors = ['beige', 'wheat', 'olivedrab', 'silver', 'darkgrey', 'grey', 'dimgrey', 'wheat', 'beige', 'slategrey', 'plum', 'cadetblue', 'gold', 'darkgoldenrod', 'darkcyan', 'indigo', 'chocolate', 'olivedrab', 'teal', 'navy', 'firebrick', 'darkgreen']
patterns = ['xx', '--', '..', '||', '..', 'oo', '++', '**', '\\\\\\\\', '////', '-', 'x', '|', '.', 'o', '+', '*', '\\\\', '//', '---', 'xxx', '|||', '...', 'ooo', '+++', '***', '\\\\\\\\\\\\', '//////']

# 全局字号
fsize = 14

# 区域标签字号增量
text_fsize_add = 1 

# 图片大小
figsize = [6, 5] 

# x轴标签名旋转角度（0为不旋转）
xrotation = 0    

# y轴标签名旋转角度（0为不旋转）。
yrotation = 0  

# 线粗
linewidths = 0.2 

# x/y轴名字标签距离横轴刻度的距离
xlabelpad = 10
ylabelpad = 10

# 自定义坐标轴字体大小，默认'auto'，自动和fsize一样大
xlabelsize = 'auto'
ylabelsize = 'auto' 

# 标签背景色和位置偏移自定义设置，默认'auto'自动
pattern_colors = 'auto'

# 区域标签较原来的偏移量，(x方向，y方向) 例如 [(0, 0), (0, 0), (0, 0), (0, 0)]
pattern_moves = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)] 

# 传给draw_max_area函数
the_plt = draw_max_area(expressions=expressions, assigns=assigns, 
              the_var_x=the_var_x, start_end_x=start_end_x, 
              the_var_y=the_var_y, start_end_y=start_end_y, x_name=x_name, y_name=y_name, 
              fsize=fsize, texts=texts, text_fsize_add=text_fsize_add,
              save_dir=save_dir, figsize=figsize, colors=colors, patterns=patterns,
              xrotation=xrotation, yrotation=yrotation, linewidths=linewidths,
             xlabelsize=xlabelsize, ylabelsize=ylabelsize, pattern_colors=pattern_colors, 
              pattern_moves=pattern_moves, xlabelpad=xlabelpad, ylabelpad=ylabelpad)
the_plt.show()
    """
    draw_detail_area_code = r"""
# 定义符号
alpha, b, c_n, c_r, delta, e, e_n, e_r, k, p_e = symbols('alpha, b, c_n, c_r, delta, e, e_n, e_r, k, p_e')

# 表达式
expressions = {
	r'$\pi_r^{NW}$': e*p_e+(k*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2)/(8*(k+alpha*delta*(1-alpha*delta))**2),
	r'$\pi_r^{BW}$': e*p_e + ( k*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/( 8*(k+delta-delta**2)**2),
	r'$\pi_r^{NS}$': e*p_e + ((k+2*alpha*delta)*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2 )/( 8*(k+alpha*delta*(2-alpha*delta))**2),
	r'$\pi_r^{BS}$': e*p_e + ( (k+2*delta)*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/( 8*(k+2*delta-delta**2)**2),
}

# 参数赋值
assigns = {c_n:0.2, c_r:0.1, delta:0.8, e:2.0, e_n:1.0, e_r:0.6, k:1.1, p_e:0.1}

# 要分析的参数，及其取值范围
the_var_x = alpha
start_end_x = [0.7, 0.8] 
the_var_y = b
start_end_y = [0, 0.08] 

# xy轴的名字
x_name = r'(b) With blockchain' 
y_name = r'$b$'  

# 图片保存路径、文件名
save_dir = None 

# 每个关系区域的标签前缀、编号样式、背景颜色和图案。
# 前缀。可以是"区域"也可以是"Region"，默认"Region"。
prefix = 'Region'

# 序号标记风格。有三种可选："roman", "letter" 和"number"，分别表示罗马数字、大写英文字母和阿拉伯数字。
numbers = 'roman' 

# 区域颜色
colors = ['beige', 'green', 'red', 'plum', 'wheat', 'dimgrey', 'dimgrey', 'wheat', 'beige', 'slategrey', 'plum', 'cadetblue', 'gold', 'darkgoldenrod', 'darkcyan', 'indigo', 'chocolate', 'olivedrab', 'teal', 'navy', 'firebrick', 'darkgreen']
patterns = ['..', '--', 'xx', '+', '**', None, '++', '**', '\\\\\\\\', '////', '-', 'x', '|', '.', 'o', '+', '*', '\\\\', '//', '---', 'xxx', '|||', '...', 'ooo', '+++', '***', '\\\\\\\\\\\\', '//////']

# 全局字号
fsize = 14

# 区域标签字号增量
text_fsize_add = -2
 
# 图片大小。
figsize = [9, 5] 

# x轴标签名旋转角度（0为不旋转）
xrotation = 0  
 
# y轴标签名旋转角度（0为不旋转）
yrotation = 0  

# 线粗
linewidths = 0.1

# x/y轴名字标签距离横轴刻度的距离
xlabelpad = 10
ylabelpad = 10

# 自定义坐标轴字体大小，默认'auto'，自动和fsize一样大
xlabelsize = 'auto'
ylabelsize = 'auto'
legendsize = 'auto'

# 标签背景色和位置偏移自定义设置，默认'auto'自动
pattern_colors = 'auto'
pattern_moves =  [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]    

# 传给draw_detail_area函数
the_plt = draw_detail_area(expressions=expressions, assigns=assigns, 
        the_var_x=the_var_x, start_end_x=start_end_x, the_var_y=the_var_y, start_end_y=start_end_y, 
        x_name=x_name, y_name=y_name, fsize=fsize, text_fsize_add=text_fsize_add,
        save_dir=save_dir, figsize=figsize, colors=colors, patterns=patterns,
        xrotation=xrotation, yrotation=yrotation, linewidths=linewidths,
        prefix=prefix, numbers=numbers, xlabelsize=xlabelsize, ylabelsize=ylabelsize, legendsize=legendsize, 
      pattern_colors=pattern_colors, pattern_moves=pattern_moves, xlabelpad=xlabelpad, ylabelpad=ylabelpad)
the_plt.show()
"""

    example_codes = {
        'data_lines': data_lines_code,
        'draw_lines': draw_lines_code,
        'draw_3D': draw_3D_code,
        'draw_max_area': draw_max_area_code,
        'draw_detail_area': draw_detail_area_code
    }
    print(example_codes.get(fun_name, welcome))

def set_font(label):
    """根据标签内容判断使用合适的字体，不影响 LaTeX 解析"""
    system = platform.system()
    if re.search(r'[\u4e00-\u9fff]', label):
        return 'SimSun'  # Windows 系统使用SimSun
    else:
        return 'Times New Roman'

def gen_letters(nums):
    # 生成大写字母
    uppercase_letters = string.ascii_uppercase

    # 列出36个大写字母
    letters = []
    for i in range(nums):
        if i < 26:
            letters.append(uppercase_letters[i])
        else:
            div, mod = divmod(i - 26, 26)
            letters.append(uppercase_letters[div] + uppercase_letters[mod])
    return letters

def gen_romans(nums):
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
        ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
        ]
    roman_lists = []
    for num in range(1, nums+1):
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syb[i]
                num -= val[i]
            i += 1
        roman_lists.append(roman_num)
    return roman_lists

def mathshow(latex_code):
    display(Math(latex_code) )

def showlatex(sym):
    print(latex(sym, mode='inline'))

def mathprint(sym):
    mathshow(latex(sym))

def exist_file(file_dir):
    return os.path.exists(file_dir)

def save_var(the_var, file_dir):
    with open(file_dir, 'wb') as f:
        pickle.dump(the_var, f)


def get_var(file_dir):
    if not exist_file(file_dir):
        print('文件不存在！')
        return
    else:
        with open(file_dir, 'rb') as f:
            loaded_var = pickle.load(f)
        return loaded_var


def list_equivalent_relations(expr):
    """
    解析关系式并生成所有等价的关系式。

    参数:
        equation (str): 输入的关系式，格式类似 '${\Pi}_M={\Pi}_N>{\Pi}_P>{\Pi}_B={\Pi}_D={\Pi}_E$'

    返回:
        list[str]: 所有等价的关系式
    """
    # 去除开头和结尾的符号（如 $）
    equation = expr.strip('$')

    # 分离各部分
    parts = []
    temp = []
    for char in equation:
        if char in {'=', '>'}:
            if temp:
                parts.append(''.join(temp))
                temp = []
            parts.append(char)
        else:
            temp.append(char)
    if temp:
        parts.append(''.join(temp))

    # 组合相等的部分
    groups = []
    current_group = []
    for part in parts:
        if part == '=':
            continue
        elif part == '>':
            if current_group:
                groups.append(current_group)
                current_group = []
        else:
            current_group.append(part)
    if current_group:
        groups.append(current_group)

    # 生成等价关系式
    all_relations = []
    perms = [list(permutations(group)) for group in groups]
    for perm in product(*perms):
        result = []
        for i, group in enumerate(perm):
            result.append('='.join(group))
            if i < len(perm) - 1:
                result.append('>')
        all_relations.append('$' + ''.join(result) + '$')

    all_relations.remove(expr)
    return all_relations


def join_with_symbols(perm, symbols):
    # 确保排列和符号组合的长度匹配
    if len(perm) - 1 != len(symbols):
        raise ValueError("排列的长度减1应等于符号组合的长度")

    # 使用符号组合连接排列中的元素
    result = []
    for i in range(len(perm) - 1):
        result.append(perm[i])
        result.append(symbols[i])
    result.append(perm[-1])  # 添加最后一个元素

    return ''.join(result)


def get_max_names(expr):
    s = expr.replace('$', '')
    parts = s.split('>')
    if len(parts) > 1:
        return parts[0].split('=')
    else:
        return s.split('=')

def remove_duplicates(lst):
    seen = []
    result = []
    for sublist in lst:
        if sublist not in seen:
            seen.append(sublist)
            result.append(sublist)
    return result


def data_lines(data,
               label_x=None,
               x_name=None,
               y_name=None,
               save_dir=None,
               location='best',
               ncol=1,
               fsize=14,
               figsize=[5, 4],
               xt_rotation=0,
               xrotation=0,
               yrotation=90,
               linestyles=None,
               linewidth=1,
               markers=m_list,
               markersize=3.5,
               colors=c_list,
               isgrid=False,
               xpad=3,
               ypad=3,
               xlabelpad=3,
               ylabelpad=3,

               xlabelsize='auto',
               ylabelsize = 'auto',
               legendsize = 'auto'
               ):
    """
    - data: 传入的数据，列表或np.array均可。（必须）
    - label_x: 横轴刻度标签，默认连续数字。
    - x_name: 横轴名称标签，默认'$x$'。
    - y_name: 纵轴名称标签，默认'$y$'。
    - save_dir=None: 图片保存路径，字符串。默认None，不保存。
    - location: 图例的方位，可以选填的内容有'best','northeast','northwest','southwest','southeast','east','west','south','north','center'。默认值为'best'，表示自动安排至合适的位置。
    - ncol: 图例的列数，默认为1列，即竖着排布。
    - fsize: 图片中字号的大小，默认值为14。
    - figsize: 图片的大小，写成`[宽, 高]`的形式。默认为`[5, 4]`。
    - xt_rotation: 横轴刻度标签旋转角度。用于刻度为年份，横着挤不下的情况，可以设成45度，错开排布。默认不旋转，即0度。
    - xrotation: 横轴名字标签旋转角度，默认值0，基本不需要动。
    - yrotation: 纵轴名字标签旋转角度，默认值90，字是正的。如果y轴的名字较长，不好看，可以设成0，字是竖倒着写的，紧贴y轴，但看的话需要歪脖子，专治脊椎不好使哈。
    - linestyles: 一组线的形状，`[]`列表形式去写，在多线图中用于按顺序制定每个线的形状。如实线'-'，点横线'-.'，虚线'--'，点线':'。默认值为None，表示取工具内的线型列表`ls_list`得第一个，即实线'-'。
      本工具中提供的线型列表如下：
      ``ls_list = ['-', (0, (1, 10)), (0, (5, 10)),'-.','--', ':', (0, (3, 10, 1, 10, 1, 10)), (5, (10, 3)), (0, (5, 5)), (0, (5, 1))]``
      关于线型的详细说明：
         https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html#linestyles

    - linewidth: 线粗。字面意思，没啥好说的，默认值为1。
    - markers: 一组标记符号，`[]`列表形式去写，在多线图中用于按顺序制定每个线的标记符号。工具内的标记符号列表`m_list`。如果只有一条线，就取`m_list`中的第一个，即圆点'o'。
      本工具中提供的标记符号列表如下：
      ``m_list = ['o','s', '*', 'P', 'X', 'D', 'p', 'x', '8', '2', 'H', '+', '|', '<', '>', '^', 'v', ',']``
      关于标记符号的详细说明：
          https://matplotlib.org/stable/api/markers_api.html#module-matplotlib.markers

    - markersize: 标记符号的大小，默认3.5。
    - colors: 一组颜色，`[]`列表形式去写，在多线图中用于按顺序制定每个线的颜色（包含标记符号的颜色）。工具内的颜色列表`c_list`。如果只有一条线，就取`c_list`中的第一个，即蓝色'blue'。
      本工具中提供的颜色列表如下：
      ``c_list = ['blue', 'gold', 'green', 'red', 'darkgoldenrod', 'darkcyan', 'indigo',
              'chocolate', 'olivedrab', 'teal', 'navy', 'firebrick','darkgreen', 'purple', 'cadetblue']``
      关于颜色的详细说明：
        https://matplotlib.org/stable/gallery/color/named_colors.html#base-colors
    - isgrid: 是否要网格。要就填True，不要就是False，默认不要。
    - xpad=3, ypad=3, xlabelpad=3, ylabelpad=3: 分别为横轴刻度值距离横轴的距离、纵轴刻度值距离纵轴的距离、横轴名字标签距离横轴刻度的距离、纵轴名字标签距离纵轴刻度的距离。默认值3,3,3,3。如果挤了不好看了，再微调此参数，一般不用动。
    """
    fig, ax = plt.subplots(figsize=figsize)
    plt.xticks(fontsize=fsize, fontname='times new roman', rotation = xt_rotation)
    plt.yticks(fontsize=fsize, fontname='times new roman')

    data_names = list(data.keys())
    data_num = len(data_names)

    the_x = [i+1 for i in range(len(data[data_names[0]]))]

    plt.xlim(the_x[0], the_x[1])

    if len(the_x) > 10:
        labelevery = int(len(the_x)/10)
    else:
        labelevery = 1

    if label_x is None:
        label_x = []

        for i_, x_ in enumerate(the_x):
            if i_ % labelevery == 0:
                label_x.append(str(x_))
            else:
                label_x.append('')
    else:
        for i_, _ in enumerate(the_x):
            if i_ % labelevery != 0:
                label_x[i_] = ''
            else:
                label_x[i_] = str(label_x[i_])

    ax.set_xticks(the_x)
    ax.set_xticklabels(label_x, fontsize=fsize, fontname = 'times new roman')

    if data_num == 1:
        if y_name is None:
            y_name = data_names[0]
        ys = data[data_names[0]]
        ax.plot(the_x, ys, linestyle='-', c='k', linewidth=linewidth, marker='o', markersize=markersize)
        y_min = np.min(ys)
        y_max = np.max(ys)
    else:
        for j, em in enumerate(data_names):
            if linestyles is None:
                the_ls = '-'
            else:
                the_ls = linestyles[j]

            ys = data[em]

            if len(the_x) > 10:
                markevery = int(len(the_x)/10)
                ax.plot(the_x, ys, linestyle=the_ls, c=colors[j], linewidth=linewidth, marker=markers[j], markersize=markersize, markevery = markevery, label=em)
            else:
                ax.plot(the_x, ys, linestyle=the_ls, c=colors[j], linewidth=linewidth, marker=markers[j], markersize=markersize,label=em)

            y_min_now = np.min(ys)
            y_max_now = np.max(ys)
            if j ==0:
                y_max = y_max_now
                y_min = y_min_now
            else:
                if y_max_now > y_max:
                    y_max = y_max_now
                if y_min_now < y_min:
                    y_min = y_min_now

    judge_y = max(abs(y_max),abs(y_min))
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    if judge_y >= 5000:
        plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0),useMathText=True)

    if legendsize == 'auto':
        legendsize = fsize

    if data_num >1:
        ax.legend(loc=locations[location], fontsize=legendsize, ncol=ncol)

    # 设置 x 和 y 标签字体
    x_font = set_font(x_name)
    y_font = set_font(y_name)

    if xlabelsize == 'auto':
        xlabelsize = fsize
    if ylabelsize == 'auto':
        ylabelsize = fsize

    ax.set_ylabel(y_name, fontsize=ylabelsize, fontweight='bold', rotation=yrotation, labelpad=ylabelpad, fontname=y_font)
    ax.set_xlabel(x_name, fontsize=xlabelsize, fontweight='bold', rotation=xrotation, labelpad=xlabelpad, fontname=x_font)

    # 设置刻度
    ax.tick_params(axis='x', direction='in', pad=xpad)
    ax.tick_params(axis='y', direction='in', pad=ypad)

    ax.grid(isgrid)

    fig.tight_layout()
    if save_dir is not None:
        if save_dir[-4:] == '.svg':
            plt.savefig(save_dir)
        else:
            plt.savefig(save_dir, dpi=600)
    return plt


def draw_lines(expressions,
               assigns,
               the_var,
               ranges,
               x_name='x',
               y_name='y',
               save_dir=None,
               location='best',
               ncol=1,
               fsize=14,
               figsize=[5, 4],
               xt_rotation=0,
               xrotation=0,
               yrotation=90,
               linestyles=None,
               linewidth=1,
               markers=m_list,
               markersize=3.5,
               colors=c_list,
               isgrid=False,
               x_lim=None,
               y_lim=None,
               xpad=3,
               ypad=3,
               xlabelpad=3,
               ylabelpad=3,
               xlabelsize='auto',
               ylabelsize='auto',
               legendsize='auto'
               ):
    """
    - expressions: Symbol表达式，字典形式传入。（必须）
    - assigns: 表达式参数赋值，字典形式。
    - the_var: 要分析的参数；
    - ranges: 要分析的参数的取值。[初始,结束,间隔]
    - x_name: 横轴名称标签，默认'x'。
    - y_name: 纵轴名称标签，默认'y'。
    - save_dir=None: 图片保存路径，字符串。默认None，不保存。
    - location: 图例的方位，可以选填的内容有'best','northeast','northwest','southwest','southeast','east','west','south','north','center'。默认值为'best'，表示自动安排至合适的位置。
    - ncol: 图例的列数，默认为1列，即竖着排布。
    - fsize: 图片中字号的大小，默认值为14。
    - figsize: 图片的大小，写成`[宽, 高]`的形式。默认为`[5, 4]`。
    - xt_rotation: 横轴刻度标签旋转角度。用于刻度为年份，横着挤不下的情况，可以设成45度，错开排布。默认不旋转，即0度。
    - xrotation: 横轴名字标签旋转角度，默认值0，基本不需要动。
    - yrotation: 纵轴名字标签旋转角度，默认值90，字是正的。如果y轴的名字较长，不好看，可以设成0，字是竖倒着写的，紧贴y轴，但看的话需要歪脖子，专治脊椎不好使哈。
    - linestyles: 一组线的形状，`[]`列表形式去写，在多线图中用于按顺序制定每个线的形状。如实线'-'，点横线'-.'，虚线'--'，点线':'。默认值为None，表示取工具内的线型列表`ls_list`得第一个，即实线'-'。
      本工具中提供的线型列表如下：
      ``ls_list = ['-', (0, (1, 10)), (0, (5, 10)),'-.','--', ':', (0, (3, 10, 1, 10, 1, 10)), (5, (10, 3)), (0, (5, 5)), (0, (5, 1))]``
      关于线型的详细说明：
         https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html#linestyles
    - linewidth: 线粗。字面意思，没啥好说的，默认值为1。可以传入列表，分别为每条线设置。
    - markers: 一组标记符号，`[]`列表形式去写，在多线图中用于按顺序制定每个线的标记符号。工具内的标记符号列表`m_list`。如果只有一条线，就取`m_list`中的第一个，即圆点'o'。
      本工具中提供的标记符号列表如下：
      ``m_list = ['o','s', '*', 'P', 'X', 'D', 'p', 'x', '8', '2', 'H', '+', '|', '<', '>', '^', 'v', ',']``
      关于标记符号的详细说明
           https://matplotlib.org/stable/api/markers_api.html#module-matplotlib.markers

    - markersize: 标记符号的大小，默认3.5。可以传入列表，分别为每条线设置。
    - colors: 一组颜色，`[]`列表形式去写，在多线图中用于按顺序制定每个线的颜色（包含标记符号的颜色）。工具内的颜色列表`c_list`。如果只有一条线，就取`c_list`中的第一个，即蓝色'blue'。
      本工具中提供的颜色列表如下：
      ``c_list = ['blue', 'gold', 'green', 'red', 'darkgoldenrod', 'darkcyan', 'indigo',
              'chocolate', 'olivedrab', 'teal', 'navy', 'firebrick','darkgreen', 'purple', 'cadetblue']``
      关于颜色的详细说明：
         https://matplotlib.org/stable/gallery/color/named_colors.html#base-colors

    - isgrid: 是否要网格。要就填True，不要就是False，默认不要。
    - x_lim: 横轴显示的范围，以`[起始值,结束值]`的形式去写。默认None，根据数据自动安排。除非不好看再调，一般不动该参数。
    - y_lim: 纵轴显示的范围，以`[起始值,结束值]`的形式去写。默认None，根据数据自动安排。除非不好看再调，一般不动该参数。举个例子，“2.2 画单条曲线图”部分不太好看.
    - xpad=3, ypad=3, xlabelpad=3, ylabelpad=3: 分别为横轴刻度值距离横轴的距离、纵轴刻度值距离纵轴的距离、横轴名字标签距离横轴刻度的距离、纵轴名字标签距离纵轴刻度的距离。默认值3,3,3,3。如果挤了不好看了，再微调此参数，一般不用动。
    """

    if expressions is None:
        print('注意：请输入表达式！ Note: Please enter expressions!')
        return None

    if the_var is None or ranges is None:
        print(
            '注意：请输入要分析的变量及范围！Note: Please enter the variable(s) to be analyzed and its (their) range(s)!')
        return None

    fig, ax = plt.subplots(figsize=figsize)
    # 设置 x 和 y 标签字体
    x_font = set_font(x_name)
    y_font = set_font(y_name)

    if xlabelsize == 'auto':
        xlabelsize = fsize
    if ylabelsize == 'auto':
        ylabelsize = fsize

    ax.set_ylabel(y_name, fontsize=ylabelsize, fontweight='bold', rotation=yrotation, labelpad=ylabelpad, fontname=y_font)
    ax.set_xlabel(x_name, fontsize=xlabelsize, fontweight='bold', rotation=xrotation, labelpad=xlabelpad, fontname=x_font)

    plt.xticks(fontsize=fsize, fontname='times new roman', rotation = xt_rotation)
    plt.yticks(fontsize=fsize, fontname='times new roman')

    exp_names = list(expressions.keys())
    exp_num = len(exp_names)

    ranges_ = [ranges[0], ranges[1]+ranges[2], ranges[2]]
    if x_lim is None:
        plt.xlim(ranges[0], ranges[1])
    else:
        plt.xlim(x_lim[0], x_lim[1])

    if y_lim is not None:
        plt.ylim(y_lim[0], y_lim[1])

    # linewidth 和 markersize 列表化：
    if isinstance(linewidth, list):
        linewidth_ = linewidth
    else:
        linewidth_ = [linewidth]*exp_num

    if isinstance(markersize, list):
        markersize_ = markersize
    else:
        markersize_ = [markersize]*exp_num

    if exp_num == 1:
        xs = []
        ys = []
        the_exp = expressions[exp_names[0]]
        if assigns is None:
            assigned_exp = the_exp
        else:
            assigned_exp = the_exp.subs(assigns)
        for i in np.arange(*ranges_):
            xs.append(i)
            ys.append(assigned_exp.subs({the_var:i}).evalf())
        ax.plot(xs, ys, linestyle='-', c='k', linewidth=linewidth_[0], marker=None)
        y_min = np.min(ys)
        y_max = np.max(ys)
    else:
        for j, em in enumerate(exp_names):
            xs = []
            ys = []
            the_exp = expressions[exp_names[j]]
            if assigns is None:
                assigned_exp = the_exp
            else:
                assigned_exp = the_exp.subs(assigns)
            for i in np.arange(*ranges_):
                xs.append(i)
                ys.append(assigned_exp.subs({the_var: i}).evalf())

            if linestyles is None:
                the_ls = '-'
            else:
                the_ls = linestyles[j]

            if len(xs) > 10:
                markevery = int(len(xs)/10)
                ax.plot(xs, ys, linestyle=the_ls, c=colors[j], linewidth=linewidth_[j], marker=markers[j], markersize=markersize_[j], markevery = markevery, label=em)
            else:
                ax.plot(xs, ys, linestyle=the_ls, c=colors[j], linewidth=linewidth_[j], marker=markers[j], markersize=markersize_[j],label=em)


            y_min_now = np.min(ys)
            y_max_now = np.max(ys)
            if j ==0:
                y_max = y_max_now
                y_min = y_min_now
            else:
                if y_max_now > y_max:
                    y_max = y_max_now
                if y_min_now < y_min:
                    y_min = y_min_now

    judge_y = max(abs(y_max),abs(y_min))
    judge_x = max(abs(np.max(xs)),abs(np.min(xs)))
    if judge_y >= 5000:
        plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
    if judge_x >= 5000:
        plt.ticklabel_format(axis="x", style="sci", scilimits=(0,0), useMathText=True)

    # 设置刻度
    ax.tick_params(axis='x', direction='in', pad=xpad)
    ax.tick_params(axis='y', direction='in', pad=ypad)

    if legendsize == 'auto':
        legendsize = fsize

    if exp_num >1:
        ax.legend(loc=locations[location], fontsize=legendsize, ncol=ncol)
    ax.grid(isgrid)

    fig.tight_layout()
    if save_dir is not None:
        if save_dir[-4:] == '.svg':
            plt.savefig(save_dir)
        else:
            plt.savefig(save_dir, dpi=600)
    return plt

def order_types(exp_names, values, reverse=True):
    return_val = ""
    # 获取排序后元素的索引 reverse=True默认降序
    sorted_indices = sorted(range(len(values)), key=lambda x: values[x], reverse=reverse)
    for _i, em in enumerate(sorted_indices):
        if reverse:
            if _i == 0:
                last_value = values[em]
                return_val += r"$" + exp_names[em][1:-1]
            else:
                cur_value = values[em]
                if cur_value == last_value:
                    return_val += r" = " + exp_names[em][1:-1]
                else:
                    return_val += r" > " + exp_names[em][1:-1]
                last_value = cur_value
        else:
            if _i == 0:
                last_value = values[em]
                return_val += r"$" + exp_names[em][1:-1]
            else:
                cur_value = values[em]
                if cur_value == last_value:
                    return_val += r" = " + exp_names[em][1:-1]
                else:
                    return_val += r" < " + exp_names[em][1:-1]
                last_value = cur_value
    return return_val + r"$", sorted_indices

def covert_orders(expressions, assigns, the_var1, the_var2, X, Y, reverse=True):
    exp_names = list(expressions.keys())
    exp_num = len(exp_names)
    map_dict = {}  # value: relationship
    map_order = {}  # value: order

    res_list = []
    for i in range(exp_num):
        the_exp = expressions[exp_names[i]]
        assigned_exp = the_exp.subs(assigns)
        the_func = lambdify((the_var1, the_var2), assigned_exp, 'numpy')
        exp_value = the_func(X, Y)
        if isinstance(exp_value, float):
            exp_value = np.ones(X.shape, dtype=float) * exp_value
        res_list.append(exp_value)

    value_ldata = []
    index_point = 0
    for ii in range(len(res_list[0])):
        tmp = []
        for jj in range(len(res_list[0][0])):
            compare_list = [em[ii][jj] for em in res_list]
            latex_res, the_order = order_types(exp_names, compare_list, reverse=reverse)
            if latex_res not in map_dict.values():
                map_dict[index_point] = latex_res
                map_order[index_point] = the_order
                tmp.append(index_point)
                index_point += 1
            else:
                reversed_dict = {v: k for k, v in map_dict.items()}
                tmp.append(reversed_dict[latex_res])
        value_ldata.append(tmp)

    return np.array(value_ldata), map_dict, map_order  # value: relationship


def draw_3D(expressions,
            assigns,
            the_var_x,
            start_end_x,
            the_var_y,
            start_end_y,
            x_name='x',
            y_name='y',
            z_name='z',
            save_dir=None,
            color_alpha=0.8,
            linestyles=ls_list,
            linewidth=0.2,
            location='best',
            ncol=1,
            fsize=14,
            figsize=[7, 5],
            precision=1000,
            xrotation=0,
            yrotation=0,
            zrotation=90,
            isgrid=True,
            density=100,
            colors=c_list,
            edgecolor=None,
            x_lim=None,
            y_lim=None,
            z_lim=None,
            elevation=15,
            azimuth=45,
            roll=0,
            left_margin=0,
            bottom_margin=0,
            right_margin=1,
            top_margin=1,
            xpad=1,
            ypad=1,
            zpad=5,
            xlabelpad=2,
            ylabelpad=2,
            zlabelpad=12,
            xlabelsize='auto',
            ylabelsize='auto',
            zlabelsize='auto',
            legendsize='auto'
            ):
    """
    - expressions: Symbol表达式，字典形式传入。（必须）
    - assigns: 表达式参数赋值，字典形式。
    - the_var_x/the_var_y: 要分析的参数1/2；
    - start_end_x/start_end_y: 要分析的参数1/2的取值。[初始,结束]
    - x_name: x轴名称标签，默认'x'。
    - y_name: y轴名称标签，默认'y'。
    - z_name: z轴名称标签，默认'z'。
    - save_dir=None: 图片保存路径，字符串。默认None，不保存。
    - color_alpha: 曲面的透明度。取值范围0到1，浮点数。0表示全透明，1表示完全不透明。默认取0.8。可以是列表。
    - linestyles: 一组线的形状，`[]`列表形式去写，在多线图中用于按顺序制定每个线的形状。如实线'-'，点横线'-.'，虚线'--'，点线':'。默认值为None，表示取工具内的线型列表`ls_list`得第一个，即实线'-'。
      本工具中提供的线型列表如下：
      ``ls_list = ['-', (0, (1, 10)), (0, (5, 10)),'-.','--', ':', (0, (3, 10, 1, 10, 1, 10)), (5, (10, 3)), (0, (5, 5)), (0, (5, 1))]``
      关于线型的详细说明：
          https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html#linestyles

    - linewidth: 线粗。字面意思，没啥好说的，默认值为0.2。
    - location: 图例的方位，可以选填的内容有'best','northeast','northwest','southwest','southeast','east','west','south','north','center'。默认值为'best'，表示自动安排至合适的位置。
    - ncol: 图例的列数，默认为1列，即竖着排布。
    - fsize: 图片中字号的大小，默认值为14。
    - figsize: 图片的大小，写成`[宽, 高]`的形式。默认为`[7, 5]`。
    - precision: 绘画的精细程度。默认取1000，表示画 $1000 \times 1000$ 个点。该值越大，运行速度越慢，太大没必要，根据个人情况权衡。
    - xrotation/yrotation: x/y轴名字标签旋转角度，默认值0，基本不需要动。
    - zrotation: Z轴名字标签旋转角度，默认值90，字是正的。如果Z轴的名字较长，不好看，可以设成0，字是竖倒着写的，紧贴Z轴，但看的话需要歪脖子，专治脊椎不好使哈。
    - isgrid: 是否要网格。要就填True，不要就是False，默认不要。
    - density: 曲面上画线的密度，也就是曲面横纵方向各画多少根线。默认100。
    - colors: 一组颜色，`[]`列表形式去写，在多面图中用于按顺序制定每个面的颜色（包含标记符号的颜色）。工具内的颜色列表`c_list`。如果只有一张面，就取`c_list`中的第一个，即蓝色'blue'。
      本工具中提供的颜色列表如下：
      ``c_list = ['blue', 'gold', 'green', 'red', 'darkgoldenrod', 'darkcyan', 'indigo',
              'chocolate', 'olivedrab', 'teal', 'navy', 'firebrick','darkgreen', 'purple', 'cadetblue']``
      关于颜色的详细说明：
          https://matplotlib.org/stable/gallery/color/named_colors.html#base-colors

    - edgecolor: 曲面上线框的颜色。若为None，则曲面上不画线。当该参数不为None时，参数`linestyles`，`linewidth`和`density`才起作用。
    - x_lim,y_lim,z_lim: x/y/z轴显示的范围，以`[起始值,结束值]`的形式去写。默认None，根据数据自动安排。除非不好看再调，一般不动该参数。
    - elevation: 仰角 (elevation)。定义了观察者与 xy 平面之间的夹角，也就是观察者与 xy 平面之间的旋转角度。当elevation为正值时，观察者向上倾斜，负值则表示向下倾斜。默认15度。可根据美观与否微调。
    - azimuth: 方位角 (azimuth)。定义了观察者绕 z 轴旋转的角度。它决定了观察者在 xy 平面上的位置。azim 的角度范围是 −180 到 180 度，其中正值表示逆时针旋转，负值表示顺时针。默认45度。可根据美观与否微调。
    - roll: 滚动角 (roll)。 定义了绕观察者视线方向旋转的角度。它决定了观察者的头部倾斜程。默认0度，不需要动。
    - left_margin=0, bottom_margin=0, right_margin=1, top_margin=1: 左、下、右、上的图片留白，默认分别为0,0,1,1。不需要动，除非不好看。
    - xpad=1, ypad=1, zpad=5, xlabelpad=2, ylabelpad=2, ylabelpad=12: 分别为横轴刻度值距离横轴的距离、纵轴刻度值距离纵轴的距离、横轴名字标签距离横轴刻度的距离、纵轴名字标签距离纵轴刻度的距离。如果挤了不好看了，再微调此参数，一般不用动。
    """

    if expressions is None:
        print('注意：请输入表达式！ Note: Please enter expressions!')
        return None
    if assigns is None:
        print('注意：请输入参数及赋值！ Note: Please input parameters and assign values!')
        return None
    if the_var_x is None or the_var_y is None or start_end_x is None or start_end_y is None:
        print(
            '注意：请输入要分析的变量及范围！Note: Please enter the variable(s) to be analyzed and its (their) range(s)!')
        return None

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    plt.subplots_adjust(left=left_margin, bottom=bottom_margin, right=right_margin, top=top_margin)
    plt.xticks(fontsize=fsize, fontname='times new roman')
    plt.yticks(fontsize=fsize, fontname='times new roman')

    ax.yaxis.set_rotate_label(False)
    ax.xaxis.set_rotate_label(False)
    ax.zaxis.set_rotate_label(False)

    # 设置 x 和 y 标签字体
    x_font = set_font(x_name)
    y_font = set_font(y_name)
    z_font = set_font(z_name)

    if xlabelsize == 'auto':
        xlabelsize = fsize
    if ylabelsize == 'auto':
        ylabelsize = fsize
    if zlabelsize == 'auto':
        zlabelsize = fsize

    ax.set_ylabel(y_name, fontsize=ylabelsize, fontweight='bold', rotation=yrotation, labelpad=ylabelpad, fontname=y_font)
    ax.set_xlabel(x_name, fontsize=xlabelsize, fontweight='bold', rotation=xrotation, labelpad=xlabelpad, fontname=x_font)
    ax.set_zlabel(z_name, fontsize=zlabelsize, fontweight='bold', rotation=zrotation, labelpad=zlabelpad, fontname=z_font)

    # 设置刻度
    ax.tick_params(axis='x', direction='in', pad=xpad)
    ax.tick_params(axis='y', direction='in', pad=ypad)
    ax.tick_params(axis='z', direction='in', pad=zpad)

    # Define the range for x and y
    x_ = np.linspace(start_end_x[0], start_end_x[1], precision)
    y_ = np.linspace(start_end_y[0], start_end_y[1], precision)
    x, y = np.meshgrid(x_, y_)

    exp_names = list(expressions.keys())
    exp_num = len(exp_names)

    if len(x_) > density:
        rstride = int(len(x_) / density)
    else:
        rstride = 1

    if len(y_) > density:
        cstride = int(len(y_) / density)
    else:
        cstride = 1

    # color_alpha 列表化：
    if isinstance(color_alpha, list):
        color_alpha_ = color_alpha
    else:
        color_alpha_ = [color_alpha] * exp_num


    if exp_num == 1:
        the_exp = expressions[exp_names[0]]
        assigned_exp = the_exp.subs(assigns)
        the_func = lambdify((the_var_x, the_var_y), assigned_exp, 'numpy')
        z = the_func(x, y)
        if isinstance(z, float):
            z = np.ones(x.shape, dtype=float) * z
        ax.plot_surface(x, y, z, color=colors[0], edgecolor=None, alpha=color_alpha_[0])
        z_min = np.min(z)
        z_max = np.max(z)
    else:
        legend_elements = []
        his_zs = []

        get_order_func = lambda x_, y_: covert_orders(expressions=expressions, assigns=assigns,
                                              the_var1=the_var_x, the_var2=the_var_y,
                                              X=x_, Y=y_, reverse=False) # 越来越大
        Z_judge, _, map_order = get_order_func(x, y)  # value: relationship

        remove_values = []
        use_values = []
        dropout = 0.01
        for em in map_order.keys():
            count = np.count_nonzero(Z_judge == em)
            if count / (precision ** 2) <= dropout:
                remove_values.append(em)
            else:
                use_values.append(em)

        for em in remove_values:
            indices = np.where(Z_judge == em)
            rows, cols = indices
            for row, col in zip(rows, cols):
                if (col < precision - 1) and (Z_judge[row, col] in remove_values):
                    for c_add in range(1, precision - col):
                        try_value = Z_judge[row, col + c_add]
                        if try_value not in remove_values:
                            Z_judge[row, col] = try_value
                            break
                if (col >= precision - 1) and (Z_judge[row, col] in remove_values):
                    for c_add in range(1, col):
                        try_value = Z_judge[row, col - c_add]
                        if try_value not in remove_values:
                            Z_judge[row, col] = try_value
                            break
                if (row < precision - 1) and (Z_judge[row, col] in remove_values):
                    for r_add in range(1, precision - row):
                        try_value = Z_judge[row + r_add, col]
                        if try_value not in remove_values:
                            Z_judge[row, col] = try_value
                            break
                if (row >= precision - 1) and (Z_judge[row, col] in remove_values):
                    for r_add in range(1, row):
                        try_value = Z_judge[row - r_add, col]
                        if try_value not in remove_values:
                            Z_judge[row, col] = try_value
                            break


        for j, em in enumerate(exp_names):
            the_exp = expressions[exp_names[j]]
            assigned_exp = the_exp.subs(assigns)
            the_func = lambdify((the_var_x, the_var_y), assigned_exp, 'numpy')
            z = the_func(x, y)
            if isinstance(z, float):
                z = np.ones(x.shape, dtype=float) * z

            legend_elements.append(Patch(facecolor=colors[j], edgecolor=edgecolor, alpha=color_alpha_[j],
                                         label=em, linestyle=linestyles[j], linewidth = linewidth))
            his_zs.append(z)

            z_min_now = np.min(z)
            z_max_now = np.max(z)
            if j == 0:
                z_max = z_max_now
                z_min = z_min_now
            else:
                if z_max_now > z_max:
                    z_max = z_max_now
                if z_min_now < z_min:
                    z_min = z_min_now

        for key_ in use_values:
            value_ = map_order[key_]
            #print(key_, value_)
            # 画图区域
            mask = (Z_judge==key_)
            for the_order in value_:
                # 按顺序画
                the_z = copy.deepcopy(his_zs[the_order])
                the_z = the_z.astype(float)
                the_z[~mask] = np.nan

                ax.plot_surface(x, y, the_z, color=colors[the_order], alpha=color_alpha_[the_order], edgecolor=edgecolor,
                                linestyle=ls_list[the_order], linewidth=linewidth, rstride=rstride, cstride=cstride)
                del the_z

    ax.view_init(elev=elevation, azim=azimuth, roll=roll)

    ax.set_zticks(np.linspace(z_min, z_max, 10))
    for label in ax.get_zticklabels():
        label.set_fontname('Times New Roman')
        label.set_fontsize(fsize)

    judge = abs(z_max - z_min)
    if judge < 0.0001:
        ax.zaxis.set_major_formatter(plt.FormatStrFormatter('%.5f'))
    elif judge < 0.001:
        ax.zaxis.set_major_formatter(plt.FormatStrFormatter('%.4f'))
    elif judge < 0.01:
        ax.zaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
    elif judge < 1:
        ax.zaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))
    elif judge >= 1 and judge < 10:
        ax.zaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))
    else:
        ax.zaxis.set_major_formatter(plt.FormatStrFormatter('%.0f'))

    if exp_num > 1:
        if legendsize == 'auto':
            legendsize = fsize
        ax.legend(handles=legend_elements, loc=locations[location], fontsize=legendsize, ncol=ncol)

    ax.grid(isgrid)

    if x_lim is None:
        ax.set_xlim(start_end_x[1], start_end_x[0])
    else:
        ax.set_xlim(x_lim[0], x_lim[1])

    if y_lim is None:
        ax.set_ylim(start_end_y[0], start_end_y[1])
    else:
        ax.set_ylim(y_lim[0], y_lim[1])

    if z_lim is not None:
        ax.set_zlim(z_lim[0], z_lim[1])

    # fig.tight_layout()
    if save_dir is not None:
        if save_dir[-4:] == '.svg':
            plt.savefig(save_dir)
        else:
            plt.savefig(save_dir, dpi=600)
    return plt


def draw_area(expressions=None, assigns=None, the_var_x=None, start_end_x=None, the_var_y=None, start_end_y=None,
              x_name='x', y_name='y', fsize=14, text_fsize_add=0, save_dir=None, precision=1000, figsize=[9, 5],
              colors='sci', patterns='sci', xrotation=0, yrotation=90, linewidths=0.1, xpad=3, ypad=3, xlabelpad=3,
              ylabelpad=5,
              prefix='Region', numbers='roman', xlabelsize='auto', ylabelsize='auto',
              legendsize='auto', pattern_colors='auto', pattern_moves='auto',
              mode='max', texts=None, dropout=0.01, switchcolor=112):
    if expressions is None:
        print('注意：请输入表达式！ Note: Please enter expressions!')
        return None
    if assigns is None:
        print('注意：请输入参数及赋值！ Note: Please input parameters and assign values!')
        return None
    if the_var_x is None or the_var_y is None or start_end_x is None or start_end_y is None:
        print(
            '注意：请输入要分析的变量及范围！Note: Please enter the variable(s) to be analyzed and its (their) range(s)!')
        return None

    # 定义区域的颜色和填充花纹
    if colors == 'sci':
        colors = ['#ffffff', '#E6E6E6', '#DCDCDC', '#D2D2D2', '#C8C8C8', '#C3C3C3', '#BEBEBE', '#B9B9B9',
                  '#B4B4B4', '#AFAFAF', '#AAAAAA', '#A5A5A5', '#A0A0A0', '#9B9B9B', '#969696', '#919191', '#8C8C8C',
                  '#878787', '#828282', '#7D7D7D', '#787878', '#6E6E6E', '#646464', '#646464', '#5F5F5F', '#5A5A5A',
                  '#5A5A5A', '#565656', '#525252', '#4E4E4E', '#4A4A4A', '#464646', '#424242', '#3E3E3E', '#3A3A64']
    if patterns == 'sci':
        hatches = [None, '--', 'xx', '||', '..', 'oo', '++', '**', '\\\\\\\\', '////',
                   '-', 'x', '|', '.', 'o', '+', '*', '\\\\', '//',
                   '---', 'xxx', '|||', '...', 'ooo', '+++', '***', '\\\\\\\\\\\\', '//////']
    else:
        hatches = patterns

    if numbers == 'roman':
        # 列出前40个罗马数字
        numerals = gen_romans(40)
    elif numbers == 'letter':
        numerals = gen_letters(40)
    else:
        numerals = [str(i + 1) for i in range(40)]

    exp_num = len(expressions.keys())
    if exp_num <= 1:
        print('表达式个数必须大于2！ The number of expressions must be greater than 2!')
        return None

    # 替换表达式中的参数
    exprs = {}
    for name, expr in expressions.items():
        if assigns is None:
            assigned_exp = expr
        else:
            assigned_exp = expr.subs(assigns)
        exprs[name] = assigned_exp

    # 生成变量的取值网格
    vals_x = np.linspace(start_end_x[0], start_end_x[1], precision)
    vals_y = np.linspace(start_end_y[0], start_end_y[1], precision)
    X, Y = np.meshgrid(vals_x, vals_y)

    # 将 SymPy 表达式转换为数值函数
    funcs = {name: lambdify((the_var_x, the_var_y), expr, 'numpy') for name, expr in exprs.items()}

    # 计算每个点对应的表达式值
    vals = {name: func(X, Y) for name, func in funcs.items()}

    # 获取函数名称的自定义映射
    expressions_keys = expressions.keys()

    if mode == 'max':
        the_texts = {}
        if texts is None:
            for em in expressions_keys:
                the_texts[em.replace('$', '')] = em
        else:
            for i, em in enumerate(expressions_keys):
                the_texts[em.replace('$', '')] = texts[i]

    # 定义区域的条件和对应的表达式顺序（含等于）
    all_relas = product(['>', '='], repeat=exp_num - 1)
    relas = [em for em in all_relas]

    conditions = []
    bad_his = []
    for perm in permutations(expressions_keys):  # 表达式位置关系
        for _rela in relas:  # 连接符号列表
            condition = True
            for i in range(len(perm) - 1):
                if _rela[i] == '>':
                    condition &= (vals[perm[i]] > vals[perm[i + 1]])
                else:
                    condition &= (vals[perm[i]] == vals[perm[i + 1]])

            joined_string = join_with_symbols(perm, _rela)
            the_label = '$' + joined_string.replace('$', '') + '$'

            if (not np.all(condition == False)) and (the_label not in bad_his) and (np.sum(condition)/(precision**2) >= dropout):
                conditions.append((condition, the_label))
                if '=' in the_label:
                    bad_label = list_equivalent_relations(the_label)  # '${\\Pi}_N>{\\Pi}_P>{\\Pi}_B={\\Pi}_D$'
                    # 等式去重
                    bad_his += bad_label

    case_num = len(conditions)

    if mode == 'max':
        max_cases = []
        for en in conditions:
            who_max = get_max_names(en[1])
            max_cases.append(who_max)
        unique_max_cases = remove_duplicates(max_cases)

        max_conditions = []
        for em in unique_max_cases:
            sum_condition = False
            for en in conditions:
                if get_max_names(en[1]) == em:
                    # 累或数组
                    sum_condition |= en[0]
            max_conditions.append((sum_condition, ', '.join([the_texts[enn] for enn in em])))
        conditions = max_conditions
        case_num = len(conditions)

    # 确保颜色和图案的数量足够
    if len(colors) < case_num:
        colors = colors * ((case_num // len(colors)) + 1)
    if len(patterns) < case_num:
        hatches = hatches * ((case_num // len(patterns)) + 1)

    # 创建图形
    fig, ax = plt.subplots(figsize=figsize)

    # 设置 x 和 y 标签字体
    x_font = set_font(x_name)
    y_font = set_font(y_name)

    if xlabelsize == 'auto':
        xlabelsize = fsize
    if ylabelsize == 'auto':
        ylabelsize = fsize

    ax.set_ylabel(y_name, fontsize=ylabelsize, fontweight='bold', rotation=yrotation, labelpad=ylabelpad,
                  fontname=y_font)
    ax.set_xlabel(x_name, fontsize=xlabelsize, fontweight='bold', rotation=xrotation, labelpad=xlabelpad,
                  fontname=x_font)

    plt.xticks(fontsize=fsize, fontname='times new roman')
    plt.yticks(fontsize=fsize, fontname='times new roman')

    # 绘制区域、添加文本标记
    if mode != 'max':
        legend_elements = []

    for i, (condition, label) in enumerate(conditions):
        the_color = colors[i]
        the_pattern = hatches[i]
        ax.contourf(X, Y, condition, levels=[0.5, 1.5], colors=[the_color], alpha=1, hatches=[the_pattern])
        ax.contour(X, Y, condition, colors='k', linewidths=linewidths, alpha=1)

        x_center = np.mean(X[condition])
        y_center = np.mean(Y[condition])

        if mode != 'max':
            the_text = prefix + r' $\rm{' + numerals[i] + r'}$'
            legend_text = prefix + r' $\rm{' + numerals[i] + r'}$: ' + label
        else:
            the_text = label

        # 设置文本字体
        text_font = set_font(the_text)

        if pattern_colors != 'auto':
            if pattern_colors[i] != 'auto':
                the_color = pattern_colors[i]

        try:
            # 尝试将十六进制颜色代码转换为RGB元组
            rgb = mcolors.hex2color(the_color)
        except ValueError:
            # 如果转换失败，则说明the_color是一个颜色单词
            rgb = mcolors.to_rgb(the_color)

        # 计算亮度
        brightness = rgb[0] * 255 * 0.299 + rgb[1] * 255 * 0.587 + rgb[2] * 255 * 0.114


        if pattern_moves != 'auto':
            ax.text(x_center + pattern_moves[i][0], y_center + pattern_moves[i][1], the_text, ha='center', va='center',
                    fontsize=fsize + text_fsize_add, color='white' if brightness < switchcolor else 'k',
                    backgroundcolor=the_color, fontname=text_font)
        else:
            ax.text(x_center, y_center, the_text, ha='center', va='center', fontsize=fsize + text_fsize_add,
                    color='white' if brightness < switchcolor else 'k',
                    backgroundcolor=the_color, fontname=text_font)

        if mode != 'max':
            legend_text_font = set_font(legend_text)

            legend_elements.append(
                Patch(facecolor=the_color, linewidth=linewidths, edgecolor='k',
                      label=legend_text, hatch=the_pattern)
            )

    if mode != 'max':
        # 添加图例到图形
        if legendsize == 'auto':
            legendsize = fsize
        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5),
                  fontsize=legendsize, prop=FontProperties(family=legend_text_font))

    ax.grid(False)

    # 设置刻度
    ax.tick_params(axis='x', direction='out', pad=xpad)
    ax.tick_params(axis='y', direction='out', pad=ypad)

    judge_y = max(abs(np.max(vals_y)), abs(np.min(vals_y)))
    judge_x = max(abs(np.max(vals_x)), abs(np.min(vals_x)))
    if judge_y >= 5000:
        plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0), useMathText=True)
    if judge_x >= 5000:
        plt.ticklabel_format(axis="x", style="sci", scilimits=(0, 0), useMathText=True)

    fig.tight_layout()
    if save_dir is not None:
        if save_dir[-4:] == '.svg':
            plt.savefig(save_dir)
        else:
            plt.savefig(save_dir, dpi=600)
    return plt


def draw_max_area(expressions=None,
                  assigns=None,
                  the_var_x=None,
                  start_end_x=None,
                  the_var_y=None,
                  start_end_y=None,
                  x_name='x',
                  y_name='y',
                  fsize=14,
                  texts=None,
                  text_fsize_add=0,
                  save_dir=None,
                  precision=1000,
                  figsize=[5, 4],
                  colors='sci',
                  patterns='sci',
                  xrotation=0,
                  yrotation=90,
                  linewidths=0.1,
                  xpad=3,
                  ypad=3,
                  xlabelpad=3,
                  ylabelpad=5,

                  xlabelsize='auto',
                  ylabelsize='auto',
                  pattern_colors = 'auto',
                  pattern_moves = 'auto',
                  switchcolor=112
                  ):
    """
        - expressions: Symbol表达式，字典形式传入。
        - assigns: 表达式参数赋值，字典形式。
        - the_var_x/the_var_y: 要分析的参数1/2；
        - start_end_x/start_end_y: 要分析的参数1/2的取值。[初始,结束]
        - x_name: x轴名称标签，默认'x。
        - y_name: y轴名称标签，默认'y'。
        - fsize: 图片中字号的大小，默认值为14。
        - texts: 表达式expressions中的函数值若分别达到最大，则相应区域应分别标记的文本，以`[]`形式写。默认None，按照expressions提供的名字标记。注意：标签个数和expressions中的函数顺序要对应。
        - text_fsize_add: 区域标记文本字体大小相对于其他部分字体字号增加量，默认0，范围[-fsize+1, oo]。
        - save_dir=None: 图片保存路径，字符串。默认None，不保存。
        - precision: 绘画的精细程度。默认取1000，表示画 $1000 \times 1000$ 个点。该值越大，运行速度越慢，太大没必要，根据个人情况权衡。
        - figsize: 图片的大小，写成`[宽, 高]`的形式。默认为`[5, 4]`。
        - colors: 各区域的配色。一般sci论文要保证黑白打印出来能看清，因此，默认值为'sci'，表示符合学术论文美感的灰度配色方案。若``colors=None``，则表示全白色。
        - patterns: 为每个区域设置填充图案（例如斜线、网格等），以列表形式提供，例如['/', '\\', 'x', 'o']，默认[None, '-', 'x', '|', '.', 'o', '+', '*', '\\\\', '//']。
          这样可以设置不同的密度，使用更多的斜线或交叉线条使得填充更密集：
            patterns = ['/', '//', '///', '\\', '\\\\', '\\\\\\', 'x', 'xx', 'xxx']
        - xrotation/yrotation: x/y轴名字标签旋转角度，基本不需要动。
        - linewidth: 线粗。字面意思，没啥好说的，默认值为1。
        - xpad=3, ypad=3, xlabelpad=3, ylabelpad=3: 分别为横轴刻度值距离横轴的距离、纵轴刻度值距离纵轴的距离、横轴名字标签距离横轴刻度的距离、纵轴名字标签距离纵轴刻度的距离。默认值3,3,3,3。如果挤了不好看了，再微调此参数，一般不用动。
        - switchcolor=112, 根据背景颜色的亮度，自动切换字体黑白色。默认：如果背景亮度低于112，字体用白色。
    """

    return draw_area(expressions=expressions, assigns=assigns, the_var_x=the_var_x, start_end_x=start_end_x, the_var_y=the_var_y,
            start_end_y=start_end_y, x_name=x_name, y_name=y_name, fsize=fsize, text_fsize_add=text_fsize_add,
            save_dir=save_dir, precision=precision, figsize=figsize, colors=colors, patterns=patterns, xrotation=xrotation, yrotation=yrotation,
            linewidths=linewidths, xpad=xpad, ypad=ypad, xlabelpad=xlabelpad, ylabelpad=ylabelpad,
            prefix='Region', numbers='roman', xlabelsize=xlabelsize, ylabelsize=ylabelsize,
            legendsize='auto', pattern_colors=pattern_colors, pattern_moves=pattern_moves, mode='max', texts=texts, dropout=0, switchcolor=switchcolor)


def draw_detail_area(expressions=None,
                    assigns=None,
                    the_var_x=None,
                    start_end_x=None,
                    the_var_y=None,
                    start_end_y=None,
                    x_name='x',
                    y_name='y',
                    fsize=14,
                    text_fsize_add=0,
                    save_dir=None,
                    precision=1000,
                    figsize=[9, 5],
                    colors='sci',
                    patterns='sci',
                    xrotation=0,
                    yrotation=90,
                    linewidths=0.1,
                    xpad=3,
                    ypad=3,
                    xlabelpad=3,
                    ylabelpad=5,
                    prefix='Region',
                    numbers='roman',
                    dropout=0.001,
                    xlabelsize='auto',
                    ylabelsize = 'auto',
                    legendsize = 'auto',
                    pattern_colors = 'auto',
                    pattern_moves = 'auto',
                    switchcolor=112
                     ):
    """
        - expressions: Symbol表达式，字典形式传入。
        - assigns: 表达式参数赋值，字典形式。
        - the_var_x/the_var_y: 要分析的参数1/2；
        - start_end_x/start_end_y: 要分析的参数1/2的取值。[初始,结束]
        - x_name: x轴名称标签。
        - y_name: y轴名称标签。

        - fsize: 图片中字号的大小，默认值为14。
        - text_fsize_add: 区域标记文本字体大小相对于其他部分字体字号增加量，默认0，范围[-fsize+1, oo]。

        - save_dir=None: 图片保存路径，字符串。默认None，不保存。
        - precision: 绘画的精细程度。默认取1000，表示画 $1000 \times 1000$ 个点。该值越大，运行速度越慢，太大没必要，根据个人情况权衡。
        - figsize: 图片的大小，写成`[宽, 高]`的形式。默认为`[7, 4]`。

        - colors: 各区域的配色。一般sci论文要保证黑白打印出来能看清，因此，默认值为'sci'，表示符合学术论文美感的灰度配色方案。若``colors=None``，则表示全白色。
        - patterns: 为每个区域设置填充图案（例如斜线、网格等），以列表形式提供，例如['/', '\\', 'x', 'o']，默认[None, '-', 'x', '|', '.', 'o', '+', '*', '\\\\', '//']。
          这样可以设置不同的密度，使用更多的斜线或交叉线条使得填充更密集：
            patterns = ['/', '//', '///', '\\', '\\\\', '\\\\\\', 'x', 'xx', 'xxx']

        - xrotation/yrotation: x/y轴名字标签旋转角度，基本不需要动。
        - linewidth: 线粗。字面意思，没啥好说的，默认值为1。
        - xpad=3, ypad=3, xlabelpad=3, ylabelpad=3: 分别为横轴刻度值距离横轴的距离、纵轴刻度值距离纵轴的距离、横轴名字标签距离横轴刻度的距离、纵轴名字标签距离纵轴刻度的距离。默认值3,3,3,3。如果挤了不好看了，再微调此参数，一般不用动。

        - prefix: 前缀。可以是"区域"也可以是"Region"，默认"Region"。
        - numbers: 序号标记风格。有三种可选："roman", "letter" 和"number"，分别表示罗马数字、大写英文字母和阿拉伯数字。默认"roman"。
        - switchcolor=112, 根据背景颜色的亮度，自动切换字体黑白色。默认：如果背景亮度低于112，字体用白色。
    """

    return draw_area(expressions=expressions, assigns=assigns, the_var_x=the_var_x, start_end_x=start_end_x, the_var_y=the_var_y,
            start_end_y=start_end_y, x_name=x_name, y_name=y_name, fsize=fsize, text_fsize_add=text_fsize_add,
            save_dir=save_dir, precision=precision, figsize=figsize, colors=colors, patterns=patterns, xrotation=xrotation, yrotation=yrotation,
            linewidths=linewidths, xpad=xpad, ypad=ypad, xlabelpad=xlabelpad, ylabelpad=ylabelpad,
            prefix=prefix, numbers=numbers, xlabelsize=xlabelsize, ylabelsize=ylabelsize,
            legendsize=legendsize, pattern_colors=pattern_colors, pattern_moves=pattern_moves, mode='detail', texts=None, dropout=0.002,
                     switchcolor=switchcolor)


def is_number(s):
    # 尝试将字符串转换为浮点数
    try:
        float(s)
        return True
    except ValueError:
        pass

    # 检查是否是数学运算式
    # 正则表达式匹配数字、运算符、括号和空格
    pattern = r'^[0-9\+\-\*\/\(\)\.\s]+$'
    if re.match(pattern, s):
        try:
            # 尝试计算表达式
            eval(s)
            return True
        except (SyntaxError, NameError, ZeroDivisionError):
            pass

    return False


def convert_pycode(str_exps, sym_name=True):
    # 将=...,之间的^替换成**
    pattern = r"(?<==).*?(?=\n|$)"
    new_str_exps = re.sub(pattern, lambda x: x.group(0).replace('^', '**'), str_exps)

    # 写成python代码形式
    # 按换行符分割表达式字符串为列表
    expressions_list_raw = new_str_exps.split('\n')
    expressions_list = [expr.strip() for expr in expressions_list_raw if expr.strip()]

    # 用于存储所有出现的变量（去重）
    all_variables = set()

    # 遍历每个表达式字符串
    for expression_str in expressions_list:
        # 提取等号左边的部分（去除两端空白字符）
        #left_side = re.search(r"^.*?(?==)", expression_str).group(0).strip()
        # 提取等号右边的部分（去除两端空白字符）
        right_side = re.search(r"(?<==).*?(?=\n|$)", expression_str).group(0).strip()
        # 使用正则表达式找出等号右边表达式中所有符合变量命名规则的内容（纯数字不算，前面有#的不算）
        variables_in_expression = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", right_side)
        all_variables.update(variables_in_expression)

    if len(all_variables) == 0:
        all_variables = ['x']

    # 按照要求的格式生成最终字符串
    code_str = f"""from easyfig import *\n\n"""

    if sym_name:
        var_list = list(all_variables)
        for em in var_list:
            if em in sympy_names:
                all_variables.remove(em)

    # 将变量集合转换为以逗号分隔的字符串，用于symbols函数和后续格式化
    if len(all_variables)>=1:
        variables_str = ", ".join(sorted(all_variables))
        code_str += f"""# 定义符号\n{variables_str} = symbols('{variables_str}')\n\n# 表达式\nexpressions = {{\n"""
    else:
        variables_str = ''
        code_str += f"""# 表达式\nexpressions = {{\n"""


    expression_indexs = {}
    i = 0
    for expression_str in expressions_list:
        left_side = re.search(r"^.*?(?==)", expression_str).group(0).strip()
        right_side = re.search(r"(?<==).*$", expression_str).group(0).strip()
        if is_number(right_side):
            right_side = 'Number(' + right_side + ')'
        code_str += f"\t'{left_side}': {right_side},\n"
        expression_indexs[left_side] = i
        i += 1
    code_str += "}"

    try:
        ast.parse("from easyfig import *\n" + code_str.replace(r"lambda", r"lamda"))
        # print("语法正确")
        return code_str, variables_str, expression_indexs
    except SyntaxError as e:
        print(f"语法错误: {e}\n\n{code_str}")
        return None, f"语法错误: {e}\n\n{code_str}", None


def convert_latex_escape(latex_string):
    def replacer(match):
        return match.group(0).replace('\\', '\\\\')
    # 使用正则表达式找到 $...$ 内的内容
    result = re.sub(r'\$(.*?)\$', replacer, latex_string)
    return result


def makefig():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, colorchooser
    from tkinter.scrolledtext import ScrolledText
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

    colors_dict = {
        'red': '#ff0000',
        'blue': '#0000ff',
        'green': '#008000',
        'chocolate': '#d2691e',
        'cyan': '#00ffff',
        'yellow': '#ffff00',
        'magenta': '#ff00ff',
        'purple': '#800080',
        'orange': '#ffa500',
        'gold': '#ffd700',
        'brown': '#a52a2a',
        'pink': '#ffc0cb',
        'darkgoldenrod': '#b8860b',
        'darkcyan': '#008b8b',
        'indigo': '#4b0082',
        'olivedrab': '#6b8e23',
        'teal': '#008080',
        'navy': '#000080',
        'firebrick': '#b22222',
        'darkgreen': '#006400',
        'cadetblue': '#5f9ea0',
        'black': '#000000',
        'aliceblue': '#f0f8ff',
        'aquamarine': '#7fffd4',
        'azure': '#f0ffff',
        'coral': '#ff7f50',
        'white': '#ffffff',
        'gainsboro': '#dcdcdc',
        'lightgrey': '#d3d3d3',
        'silver': '#c0c0c0',
        'darkgrey': '#a9a9a9',
        'grey': '#808080',
        'dimgrey': '#696969',
        'wheat': '#f5deb3',
        'beige': '#f5f5dc',
        'slategrey': '#708090',
        'plum': '#dda0dd'
    }


    global_colors = ['red', 'blue', 'green', 'chocolate', 'cyan', 'yellow', 'magenta', 'purple', 'orange', 'gold' , 'brown', 'pink',
                     'darkgoldenrod', 'darkcyan', 'indigo', 'olivedrab', 'teal', 'navy', 'firebrick', 'darkgreen', 'cadetblue', 'black',
                     'aliceblue', 'aquamarine', 'azure', 'coral']
    global_colors2 = ['white', 'gainsboro', 'lightgrey', 'silver', 'darkgrey', 'grey', 'dimgrey', 'wheat', 'beige', 'slategrey', 'plum',
                      'cadetblue', 'gold', 'darkgoldenrod', 'darkcyan', 'indigo', 'chocolate', 'olivedrab', 'teal', 'navy', 'firebrick', 'darkgreen',
                      'red', 'blue', 'green', 'yellow']
    global_lsy = ['solid', 'dashed', 'dotted', 'dashdot', 'None', '-', '--', '-.', ':',
                  '(0, (5, 10))', '(0, (10, 10))', '(0, (5, 10, 15, 10))', '(0, (5, 10, 1, 10))', '(0, (20, 20, 5, 20))',
                  '(0, (1, 1))', '(0, (20, 10))', '(5, (10, 10))', '(0, (5, 10, 1, 10, 1, 10))', '(0, (10, 10, 5, 10, 1, 10))']
    global_mark = m_list + ['None']
    global_width = ['0.1', '0.2', '0.5', '0.7', '1.0', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0']
    global_location = ['best', 'northeast', 'northwest', 'southwest', 'southeast', 'east', 'west', 'south', 'north', 'center']
    global_patterns = ['None', '--', 'xx', '||', '..', 'oo', '++', '**', '/o', '\\|', '|*', '-\\', '+o', 'x*', 'o-', 'O|', 'O.', '*-',
                       '\\\\\\\\', '////', '-', 'x', '|', '.', 'o', '+', '*', '\\\\', '//',
                   '---', 'xxx', '|||', '...', 'ooo', '+++', '***', '\\\\\\\\\\\\', '//////']
    name2prefix = {'罗马数字':'roman', '字母':'letter', '阿拉伯数字':'number'}
    prefix2name = {'roman': '罗马数字', 'letter':'字母', 'number':'阿拉伯数字'}
    hint_text = ("请按照 `表达式名称(支持LaTex, 要由$包裹) = 表达式` 的格式书写，一行是一个表达式，例如：$\\pi_r^{NS}$ = alpha+2*c^2-(b+lambda)/2。\n\n"
                 "特别注意：在右侧表达式中，`λ`可写作`lambda`或`lamda`，次方可写作`^`或`**`。\n\n填写完表达式后，点击“公式识别”。如果第一次用，请点击“加载案例”，在已有例子的基础上改写，更方便快捷。"
                "\n\n支持数学常数和函数，例如：pi, exp(x), log(x), sqrt(x), Abs(x), sin(x)等，可打开符号面板“Ω...”键入。"
                 "\n\n LaTeX转表达式工具，可以免抄写公式，方便快捷！具体请点击“打开 LaTeX 转换器...”。")

    setting_dict = {
        0: {
            'fn_name': [],
            'lw_list': [],
            'lsy_list': [],
            'lcor_list': [],
            'mark_list': [],
            'marksize_list': [],
        },
        1: {
            'fn_name': [],
            'the_marker': [],
            'region_name': [str(i+1) for i in range(20)],
            'lcor_list': global_colors2.copy(),
            'pattern_list': global_patterns.copy(),
            'the_marker_posx': [0] * 20,
            'the_marker_posy': [0] * 20,
        },
        2: {
            'region_name': [str(i+1) for i in range(20)],
            'lcor_list': global_colors2.copy(),
            'pattern_list': global_patterns.copy(),
            'the_marker_posx': [0] * 20,
            'the_marker_posy': [0] * 20,
        },
        3: {
            'fn_name': [],
            'lcor_list': [],
            'alpha_3d': [],
        }
    }

    def draw_qrcode(data, size=10, border=0):
        # 创建二维码对象
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr.get_matrix()

    def replace_frac_sqrt(expr):
        # 递归替换 \frac
        frac_pattern = r'\\frac\s*\{((?:[^{}]+|\{.*?\})+)\}\s*\{((?:[^{}]+|\{.*?\})+)\}'
        while re.search(frac_pattern, expr):
            expr = re.sub(frac_pattern, r'(\1)/(\2)', expr)

        # 递归替换 \sqrt
        sqrt_pattern = r'\\sqrt\s*\{((?:[^{}]+|\{.*?\})+)\}'
        while re.search(sqrt_pattern, expr):
            expr = re.sub(sqrt_pattern, r'(\1)^(1/2)', expr)

        return expr

    def mathematica_latex(latex_str):
        cleaned_expr = latex_str.replace('\\left', '').replace('\\right', '')
        cleaned_expr = re.sub(r'\s{2,}', ' ', cleaned_expr)
        #cleaned_expr = re.sub(r'\\frac{(.*?)}{(.*?)}', r'(\1)/(\2)', cleaned_expr)
        cleaned_expr = replace_frac_sqrt(cleaned_expr)
        cleaned_expr = cleaned_expr.replace('\\', '').replace(r'{', '').replace(r'}', '')
        cleaned_expr = cleaned_expr.replace('+ ', '+').replace(r' +', '+').replace('- ', '-').replace(r' -', '-')
        cleaned_expr = cleaned_expr.replace('^ ', '^').replace(r' ^', '^').replace('/ ', '/').replace(r' /', '/')
        cleaned_expr = cleaned_expr.replace(' ', '*')
        cleaned_expr = cleaned_expr.replace('*)', ')')
        return cleaned_expr

    def replace_sqrt_nthroot(expr):
        def find_matching_paren(s, start):
            depth = 1
            for i in range(start + 1, len(s)):
                if s[i] == '(':
                    depth += 1
                elif s[i] == ')':
                    depth -= 1
                    if depth == 0:
                        return i
            raise ValueError("No matching parenthesis found")

        def process(expr):
            i = 0
            while i < len(expr):
                if expr.startswith('sqrt(', i):
                    start = i + 5
                    end = find_matching_paren(expr, start - 1)
                    inner = process(expr[start:end])
                    expr = expr[:i] + f'({inner})^(1/2)' + expr[end + 1:]
                    i += len(f'({inner})^(1/2)')
                elif expr.startswith('nthroot(', i):
                    start = i + 8
                    end = find_matching_paren(expr, start - 1)
                    args = expr[start:end]
                    comma_index = find_top_level_comma(args)
                    if comma_index == -1:
                        raise ValueError("Invalid nthroot format")
                    base = process(args[:comma_index].strip())
                    root = process(args[comma_index + 1:].strip())
                    expr = expr[:i] + f'({base})^(1/({root}))' + expr[end + 1:]
                    i += len(f'({base})^(1/({root}))')
                else:
                    i += 1
            return expr

        def find_top_level_comma(s):
            depth = 0
            for i, ch in enumerate(s):
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                elif ch == ',' and depth == 0:
                    return i
            return -1

        return process(expr)

    def matlab_sp(latex_str):
        cleaned_expr = latex_str.replace('.*', '*').replace('./', '/').replace('.^', '^')
        cleaned_expr = cleaned_expr.replace('...', '').replace(' ', '').replace('\n', '').replace('\r', '')
        cleaned_expr = cleaned_expr.replace(';', '')
        cleaned_expr = replace_sqrt_nthroot(cleaned_expr)
        return cleaned_expr

    def check_and_install_package(package_name, required_version):
        """
        此函数用于检查指定的包是否已安装且为所需版本，如果未安装或版本不符，则自动安装
        :param package_name: 要检查的包名
        :param required_version: 所需的版本号
        """
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            # 包未安装，使用 pip 安装
            try:
                subprocess.check_call(['pip', 'install', f'{package_name}=={required_version}'])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to install {package_name}: {str(e)}")
                return False
        else:
            # 包已安装，检查版本
            import pkg_resources
            try:
                installed_version = pkg_resources.get_distribution(package_name).version
                if installed_version != required_version:
                    # 版本不符，重新安装
                    try:
                        subprocess.check_call(['pip', 'install', '--upgrade', f'{package_name}=={required_version}'])
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to upgrade {package_name}: {str(e)}")
                        return False
            except pkg_resources.DistributionNotFound:
                messagebox.showerror("Error",
                                     f"{package_name} is listed as installed but version cannot be determined.")
                return False
        return True

    def create_dszz(parent):
        ds_panel = tk.Toplevel(parent)
        ds_panel.grab_set()
        ds_panel.title("打赏作者")
        ds_panel.resizable(False, False)
        #ds_panel.attributes("-topmost", True)  # 设置窗口为顶层窗口，独占效果
        ds_panel.protocol("WM_DELETE_WINDOW", lambda: ds_panel.destroy())  # 允许关闭窗口
        # 获取屏幕宽度和高度，将窗口放在屏幕右侧
        screen_width = ds_panel.winfo_screenwidth()
        screen_height = ds_panel.winfo_screenheight()
        window_width = 700
        window_height = 500

        x_position = (screen_width - window_width) // 2  # 距屏幕右侧 10 像素
        y_position = (screen_height - window_height) // 2  # 垂直居上
        ds_panel.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # 设置窗口内容
        tk.Label(ds_panel, text="感谢使用！", font=("SimSun", 35)).pack(pady=10)
        tk.Label(ds_panel, text="您的支持是我持续更新的动力！",font=("SimSun", 27)).pack(pady=10)

        frame1 = ttk.Frame(ds_panel)
        frame1.pack(fill='x', expand=True, padx=3, pady=3)
        frame1.grid_columnconfigure(0, weight=1)
        frame1.grid_columnconfigure(1, weight=1)
        _left_frame = ttk.Frame(frame1)
        _right_frame = ttk.Frame(frame1)
        _left_frame.pack(side='left', fill='both', expand=True, pady=5)
        _right_frame.pack(side='right', fill='both', expand=True, pady=5)

        tk.Label(_left_frame, text="支付宝扫码打赏", font=("SimSun", 13)).pack(side="top", pady=2)
        # 创建Canvas并绘制二维码-支付宝
        canvas1 = tk.Canvas(_left_frame, width=240, height=240)
        canvas1.pack(side="top", pady=2)
        matrix = draw_qrcode(data="https://qr.alipay.com/tsx14667z29wnfs2njla635", size=2, border=0)
        matrix_widthx = len(matrix)
        # 计算每个模块的大小
        module_size = 240 // (matrix_widthx)
        # 绘制二维码的每个模块
        for y in range(matrix_widthx):
            for x in range(matrix_widthx):
                if matrix[x][y]:
                    # 绘制黑色模块
                    canvas1.create_rectangle(x * module_size, y * module_size, (x + 1) * module_size, (y + 1) * module_size,
                                            fill="black", outline="black")

        tk.Label(_right_frame, text="微信扫码打赏",font=("SimSun", 13)).pack(side="top", pady=2)
        # 创建Canvas并绘制二维码-微信
        canvas2 = tk.Canvas(_right_frame, width=240, height=240)
        canvas2.pack(side="top", pady=2)
        matrix = draw_qrcode(data="wxp://f2f0EnZwbDBoLdN0qe9nv7upxRriYehwjAqO3JLedo8yTtIQprf_NJEiPvfKNyKIwvxC", size=2, border=0)
        matrix_widthx = len(matrix)
        # 计算每个模块的大小
        module_size = 240 // (matrix_widthx)
        # 绘制二维码的每个模块
        for y in range(matrix_widthx):
            for x in range(matrix_widthx):
                if matrix[x][y]:
                    # 绘制黑色模块
                    canvas2.create_rectangle(x * module_size, y * module_size, (x + 1) * module_size,
                                             (y + 1) * module_size,
                                             fill="black", outline="black")

        # 底部文本
        tk.Label(ds_panel,text="如果有任何建议，欢迎邮箱反馈：374294497@qq.com\n作者：东北大学 田雨鑫\n2025-06-01",font=("宋体", 13)).pack(side="top", pady=5)

    def create_greek_letter_panel(parent, exp_input):
        if greek_window_tracker["window"] is not None:  # 如果窗口已存在，则不重复创建
            greek_panel = greek_window_tracker["window"]
            greek_panel.lift(parent)
            # 检查窗口是否最小化，如果是，则将其恢复
            if greek_panel.state() == 'iconic':
                greek_panel.deiconify()
            return

        if exp_input.get('1.0', tk.END).strip() == hint_text.strip():
            exp_input.delete('1.0', tk.END)
            exp_input.tag_remove("hint", "1.0", tk.END)

        # 创建悬浮窗口
        greek_panel = tk.Toplevel(parent)
        greek_panel.title("符号选择器")
        greek_panel.resizable(False, False)

        # 定义符号和插入内容的映射表
        symbols = [
            ('+','+'), ('-','-'), ('×','*'), ('÷','/'), ('_','_'), ('^','^'), ('(','('), (')',')'), ('=','='),

            ('α', 'alpha'), ('β', 'beta'), ('γ', 'gamma'), ('δ', 'delta'), ('ε', 'epsilon'),
            ('ζ', 'zeta'), ('η', 'eta'), ('θ', 'theta'), ('ι', 'iota'), ('κ', 'kappa'),
            ('λ', 'lambda'), ('μ', 'mu'), ('ν', 'nu'), ('ξ', 'xi'), ('ο', 'omicron'),
            ('π', 'pi'), ('ρ', 'rho'), ('σ', 'sigma'), ('τ', 'tau'), ('υ', 'upsilon'),
            ('φ', 'phi'), ('χ', 'chi'), ('ψ', 'psi'), ('ω', 'omega'),

            ('Α', 'Alpha'), ('Β', 'Beta'), ('Γ', 'Gamma'), ('Δ', 'Delta'), ('Ε', 'Epsilon'),
            ('Ζ', 'Zeta'), ('Η', 'Eta'), ('Θ', 'Theta'), ('Ι', 'Iota'), ('Κ', 'Kappa'),
            ('Λ', 'Lambda'), ('Μ', 'Mu'), ('Ν', 'Nu'), ('Ξ', 'Xi'), ('Ο', 'Omicron'),
            ('Π', 'Pi'), ('Ρ', 'Rho'), ('Σ', 'Sigma'), ('Τ', 'Tau'), ('Υ', 'Upsilon'),
            ('Φ', 'Phi'), ('Χ', 'Chi'), ('Ψ', 'Psi'), ('Ω', 'Omega'),

            ('e', 'exp(1)'), ('e^x', 'exp(x)'), ('|x|', 'Abs(x)'), ('∞', 'oo'), ('√', 'sqrt(x)'), ('n√', 'root(x,n)'),
            ('ln', 'log(x)'), ('log','log(x, b)'), ('lg','log(x, 10)'),

            ('∫', 'integrate(f, (x, a, b))'), ('∂', 'diff(f, x)'), ('lim', 'limit(f, x, x0)'),
            ('∑', 'summation(f, (i, a, b))'), ('∏', 'product(f, (i, a, b))'), ('sin', 'sin(x)'),
            ('cos', 'cos(x)'), ('tan', 'tan(x)'), ('csc', 'csc(x)'), ('sec', 'sec(x)'), ('cot', 'cot(x)'),
            ('sinh', 'sinh(x)'), ('cosh', 'cosh(x)'), ('tanh', 'tanh(x)'), ('coth', 'coth(x)'),

            ('分段', 'Piecewise((f1, con1), (f2, cons), ...)'), ('x/y','Rational(x,y)'), ('⌊x⌋', 'floor(x)'),
            ('⌈x⌉', 'ceiling(x)'), ('取模', 'Mod(x, n)'),
        ]

        # 滚动条框架
        canvas = tk.Canvas(greek_panel)
        scrollable_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # 添加按钮 (网格布局)
        num_columns = 9  # 每行的按钮数量
        for index, (symbol, code) in enumerate(symbols):
            row = index // num_columns  # 行号
            col = index % num_columns  # 列号
            btn = ttk.Button(
                scrollable_frame,
                text=symbol,
                command=lambda c=code: insert_greek_letter(exp_input, c),
                width=4
            )
            btn.grid(row=row, column=col, padx=2.2, pady=2, sticky="nsew")

        # 使每列等宽
        for col in range(num_columns):
            scrollable_frame.columnconfigure(col, weight=1)

        canvas.pack(side="left", fill="both", expand=True)

        # 让窗口完成布局计算，更新空闲任务
        greek_panel.update_idletasks()

        # 获取屏幕宽度和高度，将窗口放在屏幕右侧
        screen_width = greek_panel.winfo_screenwidth()
        screen_height = greek_panel.winfo_screenheight()
        window_width = 432
        window_height = 370

        x_position = screen_width - window_width - 20  # 距屏幕右侧 10 像素
        y_position = (screen_height - window_height) // 5  # 垂直居上
        greek_panel.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # 绑定窗口关闭事件
        parent.bind("<FocusIn>", lambda event: greek_panel.lift())
        greek_panel.protocol("WM_DELETE_WINDOW", lambda: on_close(greek_panel))
        greek_window_tracker["window"] = greek_panel

        def on_close(window):
            greek_window_tracker["window"] = None
            parent.unbind("<FocusIn>")
            window.destroy()

    def insert_greek_letter(exp_input, content):
        # 插入符号的英文名称或表达式
        exp_input.insert('insert', content + " ")
        exp_input.focus_set()  # NEW

    # 打开公式转换器.py 的窗口
    def open_formula_converter(parent):
        var = tk.IntVar()
        var.set(1)

        def convert_latex():
            """
            此函数用于将输入框中的 LaTeX 表达式转换为 SymPy 表达式，并将结果显示在输出框中
            """
            latex_str = input_text.get("1.0", tk.END).strip()
            if not latex_str:
                output_text.config(state=tk.NORMAL)
                output_text.delete("1.0", tk.END)
                output_text.insert(tk.END, "请输入 LaTeX 表达式")
                output_text.config(state=tk.DISABLED)
                return

            def replace_letter_parentheses(match):
                return match.group(0)[0] + '*('

            try:
                latex_str = latex_str.replace(f'\\[', '').replace(f'\\]', '')
                latex_str = latex_str.replace(f'\\(', '').replace(f'\\)', '')
                latex_str = latex_str.replace(f'$', '')
                if var.get() == 1:
                    cleaned_expr = mathematica_latex(latex_str)
                elif var.get() == 2:
                    cleaned_expr = matlab_sp(latex_str)
                else:
                    latex_str = latex_str.replace('{}', '').replace('{ }', '')
                    # 循环给希腊字母加{}
                    for em in greek_letters:
                        if em in latex_str:
                            latex_str = latex_str.replace(f'\\{em}', f'{{\\{em}}}')

                    sympy_expr = parse_latex(latex_str)
                    # 使用正则表达式将 "字母(" 改为 "字母*("
                    cleaned_expr = str(sympy_expr).replace('{', '').replace('}', '')
                    cleaned_expr = re.sub(r'([a-zA-Z]+\()', replace_letter_parentheses, cleaned_expr)

                cleaned_expr = cleaned_expr.replace('lambda', 'lamda')

                output_text.config(state=tk.NORMAL)
                output_text.delete("1.0", tk.END)
                output_text.insert(tk.END, cleaned_expr)
                output_text.config(state=tk.DISABLED)
            except Exception as e:
                e_string = str(e)
                if "version" in e_string:
                    # 取出版本号
                    pattern = r'version\s+([\d.]+)'
                    match = re.search(pattern, e_string)
                    if match:
                        the_version = match.group(1)
                        if not check_and_install_package('antlr4-python3-runtime', the_version):
                            output_text.config(state=tk.NORMAL)
                            output_text.delete("1.0", tk.END)
                            output_text.insert(tk.END, "`antlr4-python3-runtime`包自动安装失败，请手动安装：\n\n pip install antlr4-python3-runtime==<指定版本号>")
                            output_text.config(state=tk.DISABLED)
                            return 
                        else:
                            output_text.config(state=tk.NORMAL)
                            output_text.delete("1.0", tk.END)
                            output_text.insert(tk.END, f"安装`antlr4-python3-runtime=={the_version}`成功，请重新启动easyfig即可!")
                            output_text.config(state=tk.DISABLED)
                            return
                    else:
                        output_text.config(state=tk.NORMAL)
                        output_text.delete("1.0", tk.END)
                        output_text.insert(tk.END, "`antlr4-python3-runtime`包自动安装失败，请手动安装：\n\n pip install antlr4-python3-runtime==<指定版本号>")
                        output_text.config(state=tk.DISABLED)
                        return
                else:
                    output_text.config(state=tk.NORMAL)
                    output_text.delete("1.0", tk.END)
                    output_text.insert(tk.END, str(e))
                    output_text.config(state=tk.DISABLED)
                    return

        def copy_to_clipboard():
            """
            此函数将输出框中的内容复制到剪贴板
            """
            result = output_text.get("1.0", tk.END).strip()
            if result:
                pyperclip.copy(result)

        # 创建一个新的窗口
        if converter_window_tracker["window"] is not None:  # 如果窗口已存在，则不重复创建
            converter_window = converter_window_tracker["window"]
            converter_window.lift(parent)
            # 检查窗口是否最小化，如果是，则将其恢复
            if converter_window.state() == 'iconic':
                converter_window.deiconify()
            return

        converter_window = tk.Toplevel(parent)
        converter_window.title("LaTeX 到 SymPy 的转换器")

        converter_window.resizable(False, False)

        # 获取屏幕宽度和高度，将窗口放在屏幕右侧
        screen_width = converter_window.winfo_screenwidth()
        screen_height = converter_window.winfo_screenheight()
        window_width = 700
        window_height = 520

        x_position = (screen_width - window_width)//2  # 距屏幕右侧 10 像素
        y_position = (screen_height - window_height) // 2  # 垂直居上
        converter_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # 创建输入文本框的说明标签
        tk.Label(converter_window, text="请输入 LaTeX 表达式（对Mathematica，选定右键，复制为LaTeX即可）:",font=("Helvetica", 12)).pack(side=tk.TOP, anchor=tk.W)

        # 创建输入文本框
        input_text = tk.Text(converter_window, height=7, font=("Helvetica", 14), undo=True)
        input_text.pack(side=tk.TOP, fill='both', expand=True, pady=5)

        def create_context_menu(event):
            context_menu = tk.Menu(input_text, tearoff=0)
            context_menu.add_command(label="撤回(Undo)[Ctrl+Z]", command=lambda: input_text.event_generate("<<Undo>>"))
            context_menu.add_command(label="恢复(Redo)[Ctrl+Y]", command=lambda: input_text.event_generate("<<Redo>>"))
            context_menu.add_command(label="复制(Copy)[Ctrl+C]", command=lambda: input_text.event_generate("<<Copy>>"))
            context_menu.add_command(label="粘贴(Paste)[Ctrl+V]", command=lambda: input_text.event_generate("<<Paste>>"))
            context_menu.add_command(label="剪切(Cut)[Ctrl+X]", command=lambda: input_text.event_generate("<<Cut>>"))
            context_menu.add_command(label="全选(Select All)[Ctrl+A]", command=lambda: input_text.tag_add(tk.SEL, "1.0", tk.END))
            context_menu.post(event.x_root, event.y_root)
        # 绑定右键菜单
        input_text.bind("<Button-3>", create_context_menu)

        # 创建转换按钮
        radio_frame = tk.Frame(converter_window)
        radio_frame.pack(side=tk.TOP)
        mathe_radio = tk.Radiobutton(radio_frame, text="Mathematica LaTex", variable=var, value=1)
        mathe_radio.pack(side=tk.LEFT, padx=5, pady=(0, 10))
        lab_radio = tk.Radiobutton(radio_frame, text="Matlab 代码", variable=var, value=2)
        lab_radio.pack(side=tk.LEFT, padx=5, pady=(0, 10))
        general_radio = tk.Radiobutton(radio_frame, text="通用LaTex", variable=var, value=3)
        general_radio.pack(side=tk.LEFT, padx=5, pady=(0, 10))
        convert_button = tk.Button(radio_frame, text="转换", command=convert_latex, width=20)
        convert_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

        # 创建输出文本框的说明标签
        tk.Label(converter_window, text="转换后的 SymPy 表达式:", font=("Helvetica", 12)).pack(side=tk.TOP, anchor=tk.W)

        # 创建输出文本框
        output_text = tk.Text(converter_window, height=7, state=tk.DISABLED, font=("Helvetica", 14))
        output_text.pack(side=tk.TOP, fill='both', expand=True, pady=5)

        # 创建复制按钮
        copy_button = tk.Button(converter_window, text="复制", command=copy_to_clipboard, width=20)
        copy_button.pack(side=tk.TOP, pady=(0, 10))

        tk.Label(converter_window, text="请注意：转换工具准确率在99.9%以上，但这不意味着100%准确，\n请务必认真核对转换后的公式！",
                 font=("Helvetica", 15),fg="red").pack(side=tk.TOP, anchor=tk.W)

        # 绑定窗口关闭事件
        converter_window.protocol("WM_DELETE_WINDOW", lambda: on_close(converter_window))
        converter_window_tracker["window"] = converter_window

        def on_close(window):
            converter_window_tracker["window"] = None
            window.destroy()


    def show_plot(fig, parent):
        # 创建一个 Toplevel 窗口
        top = tk.Toplevel(parent)
        top.title("Plot Window")
        #top.geometry("800x600")  # 设置窗口大小
        # 绑定窗口关闭事件
        top.protocol("WM_DELETE_WINDOW", lambda: top.destroy())
        top.grab_set()  # 使 Toplevel 窗口独占
        # 将 matplotlib 图形嵌入到 Toplevel 窗口
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # 添加matplotlib工具栏
        toolbar = NavigationToolbar2Tk(canvas, top)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def on_main_closing(root):
        # 确保所有子窗口都已关闭
        for widget in root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        # 退出主程序
        root.quit()

    # **Main**
    # 初始化主窗口
    root = tk.Tk()
    root.title("EasyFig仿真绘图向导 V2.5.0 - 作者：东北大学 田雨鑫博士 - 让天下没有难用的工具！")
    root.state('zoomed')  # 最大化
    root.protocol("WM_DELETE_WINDOW", lambda: on_main_closing(root))

    # 用于跟踪符号选择窗口
    greek_window_tracker = {"window": None}
    # 用于跟踪工具窗口
    converter_window_tracker = {"window": None}

    # 设置全局字体
    default_font = ("Times New Roman", 15)
    bold_font = ('宋体', 15, 'bold')

    # 创建样式对象
    style = ttk.Style(root)

    # 设置标签页字体大小
    style.theme_use('clam')  # 使用 'clam' 主题以支持背景色修改
    style.configure("Custom.TButton",font=("宋体", 15),background="#cceeff")
    style.configure("Custom2.TButton",font=("宋体", 15))
    style.configure("Custom3.TButton",font=("宋体", 15),background="#ffee00")
    style.configure("Custom4.TButton",font=("Arial", 13, "italic"),background="#82c91e")
    style.configure("Custom5.TButton",font=("宋体", 11),background="#ffc543")
    style.configure('TNotebook.Tab', font=('宋体', 16))
    style.configure('Custom.TCheckbutton', font=('宋体', 15))

    # 创建Notebook（标签页）
    notebook = ttk.Notebook(root, style='TNotebook')
    notebook.pack(expand=True, fill='both')

    # 创建四个标签页
    tabs = []
    for i in range(1, 5):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=f"Tab {i}")  # 临时名称，后面会替换
        tabs.append(tab)

    # 设置Tab名称
    notebook.tab(0, text="绘制仿真折线图")
    notebook.tab(1, text="绘制模式比较图")
    notebook.tab(2, text="绘制关系区域图")
    notebook.tab(3, text="绘制仿真三维图")

    # 定义一个函数来创建每个Tab的内容，减少重复代码
    def create_tab(tab, tab_type):
        # 左右分割，比例8:2
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True, padx=3, pady=3)

        # 左半部分，上中下分割，比例2:3:1
        main_frame.grid_rowconfigure(0, weight=2)
        main_frame.grid_rowconfigure(1, weight=3)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        _top = ttk.Frame(main_frame)
        _middle = ttk.Frame(main_frame)
        _bottom = ttk.Frame(main_frame)
        _top.pack(side='top', fill='both', expand=True, pady=(0, 5))
        _middle.pack(fill='both', expand=True, pady=5)
        _bottom.pack(side='bottom', fill='both', expand=True, pady=(5, 0))

        # 1.1 上部分
        ttk.Label(_top, text="表达式输入：", font=default_font).pack(anchor='w')
        exp_input = ScrolledText(_top, font=("Times New Roman", 16), wrap='word', height=10, undo=True)
        exp_input.pack(fill='both', expand=True)

        exp_input.insert('1.0', hint_text)
        exp_input.tag_configure("hint", foreground="gray")
        exp_input.tag_add("hint", "1.0", tk.END)
        def exp_on_click(event):
            if exp_input.get('1.0', tk.END).strip() == hint_text.strip():
                exp_input.delete('1.0', tk.END)
                exp_input.tag_remove("hint", "1.0", tk.END)
        def exp_on_focusout(event):
            if exp_input.get('1.0', tk.END).strip() == "":
                exp_input.insert('1.0', hint_text)
                exp_input.tag_configure("hint", foreground="gray")
                exp_input.tag_add("hint", "1.0", tk.END)
        exp_input.bind('<Button-1>', exp_on_click)
        exp_input.bind('<FocusOut>', exp_on_focusout)


        def create_context_menu(event):
            exp_on_click(event)
            context_menu = tk.Menu(exp_input, tearoff=0)
            context_menu.add_command(label="撤回(Undo)[Ctrl+Z]", command=lambda: exp_input.event_generate("<<Undo>>"))
            context_menu.add_command(label="恢复(Redo)[Ctrl+Y]", command=lambda: exp_input.event_generate("<<Redo>>"))
            context_menu.add_command(label="复制(Copy)[Ctrl+C]", command=lambda: exp_input.event_generate("<<Copy>>"))
            context_menu.add_command(label="粘贴(Paste)[Ctrl+V]", command=lambda: exp_input.event_generate("<<Paste>>"))
            context_menu.add_command(label="剪切(Cut)[Ctrl+X]", command=lambda: exp_input.event_generate("<<Cut>>"))
            context_menu.add_command(label="全选(Select All)[Ctrl+A]", command=lambda: exp_input.tag_add(tk.SEL, "1.0", tk.END))
            context_menu.post(event.x_root, event.y_root)
        # 绑定右键菜单
        exp_input.bind("<Button-3>", create_context_menu)

        # 1.2 中部分
        middle_rows = []
        for _ in range(7):
            frame = ttk.Frame(_middle)
            frame.pack(fill='x', pady=4)
            middle_rows.append(frame)

        # 第1行：“公式识别”按钮
        btn_convert = ttk.Button(middle_rows[0], text="公式识别", command=lambda: on_convert(), width=27, style="Custom3.TButton")
        btn_convert.pack(side='left',padx=2)
        btn_char = ttk.Button(middle_rows[0], text="Ω...", command=lambda: create_greek_letter_panel(root, exp_input), width=3, style="Custom4.TButton")
        btn_char.pack(side='left',padx=2)

        # 在 main.py 的主窗口中添加一个按钮来打开公式转换器
        open_converter_button = ttk.Button(middle_rows[0], text="打开 LaTeX 转换器...", command=lambda: open_formula_converter(root), width=22, style="Custom.TButton")
        open_converter_button.pack(side='left')

        btn_clear = ttk.Button(middle_rows[0], text="清空", command=lambda: on_clear(), width=5,style="Custom2.TButton")
        btn_clear.pack(side='right', padx=2)
        btn_ds = ttk.Button(middle_rows[0], text="打赏作者", command=lambda: create_dszz(root), width=9, style="Custom5.TButton")
        btn_ds.pack(side='right', padx=2)

        # 第2行：分析参数选择（x轴参数 + y轴参数）、x轴和y轴变化范围
        if tab_type == "绘制仿真折线图":
            ttk.Label(middle_rows[1], text="分析参数选取：", font=bold_font).pack(side='left', padx=(0, 0))
            ttk.Label(middle_rows[1], text="x轴", font=bold_font).pack(side='left', padx=(5, 0))
            x_list = ttk.Combobox(middle_rows[1], state='readonly', font=default_font, width=10)
            x_list.pack(side='left', padx=(2, 5))
            x_list.bind("<<ComboboxSelected>>", lambda event: update_var_list())

            ttk.Label(middle_rows[1], text=" x轴范围：", font=bold_font).pack(side='left', padx=(10, 2))
            ttk.Label(middle_rows[1], text="起始", font=default_font).pack(side='left', padx=(2, 0))
            x_start = ttk.Entry(middle_rows[1], font=default_font, width=9, validate="key")
            x_start.delete(0, 'end')
            x_start.insert(0, "0")
            x_start.pack(side='left', padx=(2, 5))
            ttk.Label(middle_rows[1], text="结束", font=default_font).pack(side='left')
            x_end = ttk.Entry(middle_rows[1], font=default_font, width=9, validate="key")
            x_end.delete(0, 'end')
            x_end.insert(0, "1")
            x_end.pack(side='left', padx=(2, 5))

            x_start.bind("<KeyRelease>", lambda event: update_interval()) # NEW
            x_end.bind("<KeyRelease>", lambda event: update_interval())

            ttk.Label(middle_rows[1], text="间隔", font=default_font).pack(side='left')
            x_interval = ttk.Entry(middle_rows[1], font=default_font, width= 9, validate="key")
            x_interval.delete(0, 'end')
            x_interval.insert(0, "0.01")
            x_interval.pack(side='left', padx=(2, 10))
        else:
            ttk.Label(middle_rows[1], text="分析参数选取：", font=bold_font).pack(side='left')
            ttk.Label(middle_rows[1], text="x轴", font=default_font).pack(side='left', padx=(5, 0))
            x_list = ttk.Combobox(middle_rows[1], state='readonly', font=default_font, width=9)
            x_list.pack(side='left', padx=(2, 5))
            ttk.Label(middle_rows[1], text="y轴", font=default_font).pack(side='left', padx=(5, 0))
            y_list = ttk.Combobox(middle_rows[1], state='readonly', font=default_font, width=9)
            y_list.pack(side='left', padx=(2, 10))
            x_list.bind("<<ComboboxSelected>>", lambda event: update_var_list())
            # y_list 选择后验证
            x_list.bind("<<ComboboxSelected>>", lambda event: validate_x_selection(x_list, y_list))
            y_list.bind("<<ComboboxSelected>>", lambda event: validate_y_selection(x_list, y_list))

            ttk.Label(middle_rows[1], text="x轴范围：", font=bold_font).pack(side='left', padx=(10, 2))
            ttk.Label(middle_rows[1], text="起始", font=default_font).pack(side='left', padx=(2, 0))
            x_start = ttk.Entry(middle_rows[1], font=default_font, width=7, validate="key")
            x_start.delete(0, 'end')
            x_start.insert(0, "0")
            x_start.pack(side='left', padx=(2, 5))
            ttk.Label(middle_rows[1], text="结束", font=default_font).pack(side='left')
            x_end = ttk.Entry(middle_rows[1], font=default_font, width=7, validate="key")
            x_end.delete(0, 'end')
            x_end.insert(0, "1")
            x_end.pack(side='left', padx=(2, 10))

            ttk.Label(middle_rows[1], text="y轴范围：", font=bold_font).pack(side='left', padx=(10, 0))
            ttk.Label(middle_rows[1], text="起始", font=default_font).pack(side='left', padx=(2, 0))
            y_start = ttk.Entry(middle_rows[1], font=default_font, width=7, validate="key")
            y_start.delete(0, 'end')
            y_start.insert(0, "0")
            y_start.pack(side='left', padx=(2, 5))
            ttk.Label(middle_rows[1], text="结束", font=default_font).pack(side='left')
            y_end = ttk.Entry(middle_rows[1], font=default_font, width=7, validate="key")
            y_end.delete(0, 'end')
            y_end.insert(0, "1")
            y_end.pack(side='left', padx=(5, 0))

        # 第3行：其他参数赋值
        def create_context_menu2(event):
            context_menu = tk.Menu(assigns_input, tearoff=0)
            context_menu.add_command(label="撤回(Undo)[Ctrl+Z]", command=lambda: assigns_input.event_generate("<<Undo>>"))
            context_menu.add_command(label="恢复(Redo)[Ctrl+Y]", command=lambda: assigns_input.event_generate("<<Redo>>"))
            context_menu.add_command(label="复制(Copy)[Ctrl+C]", command=lambda: assigns_input.event_generate("<<Copy>>"))
            context_menu.add_command(label="粘贴(Paste)[Ctrl+V]", command=lambda: assigns_input.event_generate("<<Paste>>"))
            context_menu.add_command(label="剪切(Cut)[Ctrl+X]", command=lambda: assigns_input.event_generate("<<Cut>>"))
            context_menu.add_command(label="全选(Select All)[Ctrl+A]", command=lambda: assigns_input.tag_add(tk.SEL, "1.0", tk.END))
            context_menu.post(event.x_root, event.y_root)

        ttk.Label(middle_rows[2], text="其他参数赋值：", font=default_font, ).pack(anchor='w')
        # 第4行：Assigns_input
        assigns_input = ScrolledText(middle_rows[3], font=("Times New Roman", 14), wrap='word', height=2, undo=True)
        assigns_input.pack(fill='both', expand=True)
        assigns_input.bind("<Button-3>", create_context_menu2)

        # 根据tab_type调整中间部分的布局
        # 第5行：x轴名称、y轴名称、z轴名称
        ttk.Label(middle_rows[4], text="坐标轴命名：", font=bold_font).pack(side='left')
        ttk.Label(middle_rows[4], text="x轴名称", font=default_font).pack(side='left', padx=(5, 0))
        x_name = ttk.Entry(middle_rows[4], font=default_font, width=20)
        x_name.delete(0, 'end')
        x_name.insert(0, "$x$-axis")
        x_name.pack(side='left', padx=(5, 10))
        ttk.Label(middle_rows[4], text="y轴名称", font=default_font).pack(side='left')
        y_name = ttk.Entry(middle_rows[4], font=default_font, width=20)
        y_name.delete(0, 'end')
        y_name.insert(0, "$y$-axis")
        y_name.pack(side='left', padx=(5, 10))
        if tab_type == "绘制仿真三维图":
            ttk.Label(middle_rows[4], text="z轴名称", font=default_font).pack(side='left')
            z_name = ttk.Entry(middle_rows[4], font=default_font, width=20)
            z_name.delete(0, 'end')
            z_name.insert(0, "$z$-axis")
            z_name.pack(side='left', padx=(5, 10))

        if tab_type in ["绘制仿真三维图", "绘制仿真折线图"]:
            ttk.Label(middle_rows[4], text="  | 图例设置：", font=bold_font).pack(side='left', padx=(10, 2))
            ttk.Label(middle_rows[4], text="位置", font=default_font).pack(side='left', padx=(2, 0))
            location = ttk.Combobox(middle_rows[4], state='readonly', values=global_location, font=default_font, width=7)
            location.current(0)
            location.pack(side='left', padx=(5, 5))
            ttk.Label(middle_rows[4], text="列数", font=default_font).pack(side='left')
            ncol = tk.Spinbox(middle_rows[4], from_=1, to=10, font=default_font, width=3)
            ncol.delete(0, 'end'); ncol.insert(0, "1"); ncol.pack(side='left', padx=(5, 0))

        # 第6行：
        if tab_type in ["绘制仿真折线图"]:
            ttk.Label(middle_rows[5], text="曲线外观：", font=bold_font).pack(side='left')
            ttk.Label(middle_rows[5], text="选择曲线", font=default_font).pack(side='left', padx=(5, 0))
            expr_list = ttk.Combobox(middle_rows[5], state='readonly', font=default_font, width=13)
            expr_list.pack(side='left', padx=(5, 10))
            expr_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=False))

            # 线粗
            ttk.Label(middle_rows[5], text=": 线粗", font=default_font).pack(side='left')
            lw_list = ttk.Combobox(middle_rows[5], values=global_width, font=default_font, width=3)
            lw_list.current(4)
            lw_list.pack(side='left', padx=(5, 10))
            lw_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=True))
            lw_list.bind("<KeyRelease>", lambda event: update_settings(submit=True))

            # 线形
            ttk.Label(middle_rows[5], text="线形", font=default_font).pack(side='left')
            lsy_list = ttk.Combobox(middle_rows[5], values=global_lsy, font=default_font, width=15)
            lsy_list.current(0)
            lsy_list.pack(side='left', padx=(5, 10))
            lsy_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=True))
            lsy_list.bind("<KeyRelease>", lambda event: update_settings(submit=True))

            # 线颜色
            ttk.Label(middle_rows[5], text="线色", font=default_font).pack(side='left')
            # 颜色选择按钮
            color_button = tk.Button(middle_rows[5], text=" ", font=("Times New Roman", 10), width=2,
                                     background=colors_dict[global_colors[0]], command=lambda: change_color())
            color_button.pack(side='left', padx=(1, 1))

            lcor_list = ttk.Combobox(middle_rows[5], values=global_colors, font=default_font, width=10)
            lcor_list.current(0)
            lcor_list.pack(side='left', padx=(5, 10))
            lcor_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=True))
            lcor_list.bind("<KeyRelease>", lambda event: update_settings(submit=True))

            # 标记号
            ttk.Label(middle_rows[5], text="标记点形状", font=default_font).pack(side='left')
            mark_list = ttk.Combobox(middle_rows[5], values=global_mark, font=default_font, width=5, state='readonly')
            mark_list.current(0)
            mark_list.pack(side='left', padx=(5, 10))
            mark_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=True))
            #mark_list.bind("<KeyRelease>", lambda event: update_settings(submit=True))

            # 标记大小
            ttk.Label(middle_rows[5], text="标记点大小", font=default_font).pack(side='left')
            marksize_list = ttk.Combobox(middle_rows[5], values=global_width, font=default_font, width=4)
            marksize_list.current(9)
            marksize_list.pack(side='left', padx=(5, 5))
            marksize_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=True))
            marksize_list.bind("<KeyRelease>", lambda event: update_settings(submit=True))

        if tab_type == "绘制模式比较图":
            ttk.Label(middle_rows[4], text="  | 标注设置：", font=bold_font).pack(side='left', padx=(10,2))
            ttk.Label(middle_rows[4], text="选择表达式", font=default_font).pack(side='left', padx=(2, 0))
            expr_list = ttk.Combobox(middle_rows[4], state='readonly', font=default_font, width=10)
            expr_list.pack(side='left', padx=(5, 10))
            expr_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=False))
            ttk.Label(middle_rows[4], text="若最大则标注", font=default_font).pack(side='left', padx=(2, 0))
            the_marker = ttk.Entry(middle_rows[4], font=default_font, width=15)
            the_marker.pack(side='left', padx=(5, 10))
            the_marker.bind("<KeyRelease>", lambda event: update_settings(submit=True))

            ttk.Label(middle_rows[5], text="区域外观：", font=bold_font).pack(side='left', padx=(0, 10))
            ttk.Label(middle_rows[5], text="选择区域序号", font=default_font).pack(side='left', padx=(2, 5))
            region_list = ttk.Combobox(middle_rows[5], values= [str(em+1) for em in range(20)], state='readonly', font=default_font, width=3)
            region_list.current(0)
            region_list.pack(side='left', padx=(5, 5))
            region_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=False))

            ttk.Label(middle_rows[5], text=": 区域颜色", font=default_font).pack(side='left', padx=(2, 0))
            # 颜色选择按钮
            color_button = tk.Button(middle_rows[5], text=" ", font=("Times New Roman", 10), width=2,
                                     background=colors_dict[global_colors2[0]], command=lambda: change_color())
            color_button.pack(side='left', padx=(1, 1))

            lcor_list = ttk.Combobox(middle_rows[5], values=global_colors2, font=default_font, width=10)
            lcor_list.current(0)
            lcor_list.pack(side='left', padx=(5, 10))
            lcor_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=True))
            lcor_list.bind("<KeyRelease>", lambda event: update_settings(submit=True))


            ttk.Label(middle_rows[5], text="区域条纹", font=default_font).pack(side='left', padx=(2, 0))
            pattern_list = ttk.Combobox(middle_rows[5], values=global_patterns, font=default_font, width=10)
            pattern_list.current(0)
            pattern_list.pack(side='left', padx=(5, 10))
            pattern_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=True))
            pattern_list.bind("<KeyRelease>", lambda event: update_settings(submit=True))

            ttk.Label(middle_rows[5], text="标注偏移", font=default_font).pack(side='left', padx=(2, 0))
            ttk.Label(middle_rows[5], text="±X", font=default_font).pack(side='left', padx=(2, 0))
            the_marker_posx = tk.Spinbox(middle_rows[5], from_=-10.0, to=10.0, increment=0.1, font=default_font, width=5,
                                  command=lambda: update_settings(submit=True))
            the_marker_posx.delete(0, 'end'); the_marker_posx.insert(0, "0.0")
            the_marker_posx.pack(side='left', padx=(2, 1))
            the_marker_posx.bind("<KeyRelease>", lambda event: update_settings(submit=True))


            ttk.Label(middle_rows[5], text="±Y", font=default_font).pack(side='left', padx=(2, 0))
            the_marker_posy = tk.Spinbox(middle_rows[5], from_=-10.0, to=10.0, increment=0.1, font=default_font, width=5,
                                  command=lambda: update_settings(submit=True))
            the_marker_posy.delete(0, 'end'); the_marker_posy.insert(0, "0.0")
            the_marker_posy.pack(side='left', padx=(2, 10))
            the_marker_posy.bind("<KeyRelease>", lambda event: update_settings(submit=True))

        if tab_type == "绘制关系区域图":
            ttk.Label(middle_rows[4], text="  | 标注设置：", font=bold_font).pack(side='left', padx=(10,5))
            ttk.Label(middle_rows[4], text="前缀", font=default_font).pack(side='left', padx=(2, 0))
            the_pref = ttk.Entry(middle_rows[4], font=default_font, width=9)
            the_pref.delete(0, 'end')
            the_pref.insert(0, "Region")
            the_pref.pack(side='left', padx=(5, 5))
            ttk.Label(middle_rows[4], text="序号形式", font=default_font).pack(side='left', padx=(10, 0))
            marker_way = ttk.Combobox(middle_rows[4], state='readonly', values=["罗马数字", "字母", "阿拉伯数字"], font=default_font, width=9)
            marker_way.current(0)
            marker_way.pack(side='left', padx=(5, 10))

            ttk.Label(middle_rows[5], text="区域外观：", font=bold_font).pack(side='left', padx=(0, 2))
            ttk.Label(middle_rows[5], text="选择区域序号", font=default_font).pack(side='left', padx=(1, 0))
            region_list = ttk.Combobox(middle_rows[5], values=[str(em + 1) for em in range(20)], state='readonly', font=default_font, width=4)
            region_list.current(0)
            region_list.pack(side='left', padx=(2, 5))
            region_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=False))

            ttk.Label(middle_rows[5], text=":  区域颜色", font=default_font).pack(side='left')
            # 颜色选择按钮
            color_button = tk.Button(middle_rows[5], text=" ", font=("Times New Roman", 10), width=2,
                                     background=colors_dict[global_colors2[0]], command=lambda: change_color())
            color_button.pack(side='left', padx=(1, 1))

            lcor_list = ttk.Combobox(middle_rows[5], values=global_colors2, font=default_font, width=10)
            lcor_list.current(0)
            lcor_list.pack(side='left', padx=(5, 10))
            lcor_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=True))
            lcor_list.bind("<KeyRelease>", lambda event: update_settings(submit=True))

            ttk.Label(middle_rows[5], text="区域条纹", font=default_font).pack(side='left')
            pattern_list = ttk.Combobox(middle_rows[5], values=global_patterns, font=default_font, width=10)
            pattern_list.current(0)
            pattern_list.pack(side='left', padx=(5, 10))
            pattern_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=True))
            pattern_list.bind("<KeyRelease>", lambda event: update_settings(submit=True))

            ttk.Label(middle_rows[5], text="标注偏移", font=default_font).pack(side='left', padx=(2, 0))
            ttk.Label(middle_rows[5], text="±X", font=default_font).pack(side='left', padx=(1, 0))
            the_marker_posx = tk.Spinbox(middle_rows[5], from_=-10.0, to=10.0, increment=0.1, font=default_font, width=5,
                                  command=lambda: update_settings(submit=True))
            the_marker_posx.delete(0, 'end'); the_marker_posx.insert(0, "0.0")
            the_marker_posx.pack(side='left', padx=(2, 1))
            the_marker_posx.bind("<KeyRelease>", lambda event: update_settings(submit=True))

            ttk.Label(middle_rows[5], text="±Y", font=default_font).pack(side='left', padx=(1, 0))
            the_marker_posy = tk.Spinbox(middle_rows[5], from_=-10.0, to=10.0, increment=0.1, font=default_font, width=5,
                                  command=lambda: update_settings(submit=True))
            the_marker_posy.delete(0, 'end'); the_marker_posy.insert(0, "0.0")
            the_marker_posy.pack(side='left', padx=(2, 10))
            the_marker_posy.bind("<KeyRelease>", lambda event: update_settings(submit=True))

        if tab_type == "绘制仿真三维图":
            ttk.Label(middle_rows[5], text="外观设置：", font=bold_font).pack(side='left')
            ttk.Label(middle_rows[5], text="选择表达式", font=default_font).pack(side='left', padx=(5, 0))
            expr_list = ttk.Combobox(middle_rows[5], state='readonly', font=default_font, width=13)
            expr_list.pack(side='left', padx=(5, 1))
            expr_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=False))

            # 曲面颜色
            ttk.Label(middle_rows[5], text=":  曲面颜色", font=default_font).pack(side='left', padx=(5, 0))
            # 颜色选择按钮
            color_button = tk.Button(middle_rows[5], text=" ", font=("Times New Roman", 10), width=2,
                                     background=colors_dict[global_colors[0]], command=lambda: change_color())
            color_button.pack(side='left', padx=(1, 1))

            lcor_list = ttk.Combobox(middle_rows[5], values=global_colors, font=default_font, width=10)
            lcor_list.current(0)
            lcor_list.pack(side='left', padx=(5, 10))
            lcor_list.bind("<<ComboboxSelected>>", lambda event: update_settings(submit=True))
            lcor_list.bind("<KeyRelease>", lambda event: update_settings(submit=True))

            # 曲面不透明度
            ttk.Label(middle_rows[5], text="曲面不透明度", font=default_font).pack(side='left', padx=(10, 0))
            alpha_3d = tk.Spinbox(middle_rows[5], from_=0.0, to=1.0, increment=0.1, font=default_font, width=4,
                                  command=lambda: update_settings(submit=True))
            alpha_3d.delete(0, 'end'); alpha_3d.insert(0, "0.8")
            alpha_3d.pack(side='left', padx=(2, 10))
            alpha_3d.bind("<KeyRelease>", lambda event: update_settings(submit=True))

            ttk.Label(middle_rows[5], text="  | 整体视角：", font=bold_font).pack(side='left', padx=(10, 0))
            ttk.Label(middle_rows[5], text="仰角", font=default_font).pack(side='left', padx=(2, 0))
            elevation = tk.Spinbox(middle_rows[5], from_=-360, to=360, font=default_font, width=4)
            elevation.delete(0, 'end')
            elevation.insert(0, "15")
            elevation.pack(side='left', padx=(5, 10))
            ttk.Label(middle_rows[5], text="方位角", font=default_font).pack(side='left')
            azimuth = tk.Spinbox(middle_rows[5], from_=-360, to=360, font=default_font, width=4)
            azimuth.delete(0, 'end')
            azimuth.insert(0, "45")
            azimuth.pack(side='left', padx=(5, 0))

        # 第7行：其他设置
        ttk.Label(middle_rows[6], text="其他设置：", font=bold_font).pack(side='left')
        ttk.Label(middle_rows[6], text="字号", font=default_font).pack(side='left', padx=(10, 0))
        fsize = tk.Spinbox(middle_rows[6], from_=1, to=100, font=default_font, width=5)
        fsize.delete(0, 'end'); fsize.insert(0, "17")
        fsize.pack(side='left', padx=(5, 10))
        ttk.Label(middle_rows[6], text="图片宽", font=default_font).pack(side='left', padx=(5, 0))
        figsizeW = tk.Spinbox(middle_rows[6], from_=1, to=100, font=default_font, width=5)
        figsizeW.delete(0, 'end')

        if tab_type == "绘制关系区域图":
            figsizeW.insert(0, "9")
        else:
            figsizeW.insert(0, "6")

        figsizeW.pack(side='left', padx=(5, 10))
        ttk.Label(middle_rows[6], text="图片高", font=default_font).pack(side='left', padx=(5, 0))
        figsizeH = tk.Spinbox(middle_rows[6], from_=1, to=100, font=default_font, width=5)
        figsizeH.delete(0, 'end'); figsizeH.insert(0, "5")
        figsizeH.pack(side='left', padx=(5, 10))
        ttk.Label(middle_rows[6], text="x轴标签旋转", font=default_font).pack(side='left', padx=(5, 0))
        xrotation = tk.Spinbox(middle_rows[6], from_=0, to=360, font=default_font, width=5)
        xrotation.delete(0, 'end'); xrotation.insert(0, "0")
        xrotation.pack(side='left', padx=(5, 10))
        ttk.Label(middle_rows[6], text="y轴标签旋转", font=default_font).pack(side='left', padx=(5, 0))
        yrotation = tk.Spinbox(middle_rows[6], from_=0, to=360, font=default_font, width=5)
        yrotation.delete(0, 'end'); yrotation.insert(0, "0")
        yrotation.pack(side='left', padx=(5, 0))
        if tab_type == "绘制仿真三维图":
            ttk.Label(middle_rows[6], text="z轴标签旋转", font=default_font).pack(side='left', padx=(5, 0))
            zrotation = tk.Spinbox(middle_rows[6], from_=0, to=360, font=default_font, width=5)
            zrotation.delete(0, 'end'); zrotation.insert(0, "90")
            zrotation.pack(side='left', padx=(5, 0))
        if tab_type != "绘制仿真折线图":
            ttk.Label(middle_rows[6], text="绘图精度(越大越慢): ", font=default_font).pack(side='left', padx=(5, 0))
            prec_list = ttk.Combobox(middle_rows[6], values=['100', '200', '300', '500',
                                                             '1000', '1500', '2000'], font=default_font, width=6, state='readonly')
            prec_list.current(4)
            prec_list.pack(side='left', padx=(5, 5))

        # 1.3 下部分：运行信息
        left_frame = ttk.Frame(_bottom)
        right_frame = ttk.Frame(_bottom)
        left_frame.pack(side='left', fill='both', expand=True, padx=3, pady=3)
        right_frame.pack(side='right', fill='both', expand=True, padx=3, pady=3)

        ttk.Label(left_frame, text="运行信息：", font=default_font).pack(side='top', fill='both')
        print_log = ScrolledText(left_frame, font=("Times New Roman", 15), wrap='word', state='disabled')
        print_log.pack(fill='both', expand=True)
        print_log.configure(foreground='blue')
        print_log.configure(state='normal')
        print_log.insert('1.0', "欢迎使用EasyFig向导！")
        print_log.configure(state='disabled')

        # 2.2 下部分：按钮
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(expand=True)
        btn_draw_image = ttk.Button(btn_frame, text="出图...", command=lambda: draw_image(), width=20, style="Custom.TButton")
        btn_draw_image.pack(pady=2, fill='both')
        btn_save_code = ttk.Button(btn_frame, text="保存...", command=lambda: save_code(), width=20, style="Custom.TButton")
        btn_save_code.pack(pady=2, fill='both')
        btn_import_code = ttk.Button(btn_frame, text="打开...", command=lambda: import_code(), width=20, style="Custom.TButton")
        btn_import_code.pack(pady=2, fill='both')
        btn_import_case = ttk.Button(btn_frame, text="加载案例", command=lambda: import_case(), width=20,style="Custom.TButton")
        btn_import_case.pack(pady=2, fill='both')

        # 存储控件以便后续使用
        tab.controls = {
            'Exp_input': exp_input,
            'convert_button': btn_convert,
            'x_list': x_list,
            'y_list': y_list if tab_type not in ["绘制仿真折线图"] else None,
            'x_start': x_start,
            'x_end': x_end,
            'x_interval': x_interval if tab_type in ["绘制仿真折线图"] else None,
            'y_start': y_start if tab_type not in ["绘制仿真折线图"] else None,
            'y_end': y_end if tab_type not in ["绘制仿真折线图"] else None,
            'Assigns_input': assigns_input,
            'x_name': x_name,
            'y_name': y_name,
            'z_name': z_name if tab_type in ["绘制仿真三维图"] else None,
            'location': location if tab_type in ["绘制仿真折线图", "绘制仿真三维图"] else None,
            'ncol': ncol if tab_type in ["绘制仿真折线图", "绘制仿真三维图"] else None,
            'the_marker': the_marker if tab_type in ["绘制模式比较图"] else None,
            'marker_way': marker_way if tab_type in ["绘制关系区域图"] else None,
            'the_pref': the_pref if tab_type in ["绘制关系区域图"] else None,
            'fsize': fsize,
            'figsizeW': figsizeW,
            'figsizeH': figsizeH,
            'xrotation': xrotation,
            'yrotation': yrotation,
            'zrotation': zrotation if tab_type in ["绘制仿真三维图"] else None,
            'print_log': print_log,
            'buttons': {
                'import_case': btn_import_case,
                'import_code': btn_import_code,
                'draw_image': btn_draw_image,
                'save_code': btn_save_code,
                'btn_convert': btn_convert
            },
            'elevation': elevation if tab_type == "绘制仿真三维图" else None,
            'azimuth': azimuth if tab_type == "绘制仿真三维图" else None,
            'alpha_3d': alpha_3d if tab_type == "绘制仿真三维图" else None,
            'lcor_list': lcor_list,
            'color_button': color_button,
            'expr_list': expr_list if tab_type in ["绘制仿真折线图", "绘制模式比较图", "绘制仿真三维图"] else None,
            'lw_list': lw_list if tab_type in ["绘制仿真折线图"] else None,
            'lsy_list': lsy_list if tab_type in ["绘制仿真折线图"] else None,
            'mark_list': mark_list if tab_type in ["绘制仿真折线图"] else None,
            'marksize_list': marksize_list if tab_type in ["绘制仿真折线图"] else None,
            'region_list': region_list if tab_type in [ "绘制模式比较图", "绘制关系区域图"] else None,
            'pattern_list': pattern_list if tab_type in ["绘制模式比较图", "绘制关系区域图"] else None,
            'the_marker_posx': the_marker_posx if tab_type in ["绘制模式比较图", "绘制关系区域图"] else None,
            'the_marker_posy': the_marker_posy if tab_type in ["绘制模式比较图", "绘制关系区域图"] else None,
            'prec_list': prec_list if tab_type != "绘制仿真折线图" else None,
        }

    # 创建所有标签页
    create_tab(tabs[0], "绘制仿真折线图")
    create_tab(tabs[1], "绘制模式比较图")
    create_tab(tabs[2], "绘制关系区域图")
    create_tab(tabs[3], "绘制仿真三维图")


    def change_color():
        current_tab = notebook.select()
        tab_index = notebook.index(current_tab)
        tab = tabs[tab_index]
        current_color = tab.controls['color_button'].cget("background")
        # 打开颜色选择对话框
        selected_color = tk.colorchooser.askcolor(color=current_color, title="选择颜色")
        if selected_color[1]:  # 如果用户选择了颜色（而不是取消）
            tab.controls['color_button'].config(background=selected_color[1])
            swapped_dict = {value: key for key, value in colors_dict.items()}
            if selected_color[1] in swapped_dict:
                tab.controls['lcor_list'].set(swapped_dict[selected_color[1]])
            else:
                tab.controls['lcor_list'].set(selected_color[1])
            update_settings(submit=True)


    def update_interval():
        current_tab = notebook.select()
        tab_index = notebook.index(current_tab)
        tab = tabs[tab_index]
        if tab_index == 0:
            try:
                x1 = float(tab.controls['x_start'].get())
                x2 = float(tab.controls['x_end'].get())
                sug = (x2 - x1)/100
                sug = round(sug, 6)
                tab.controls['x_interval'].delete(0, tk.END)
                tab.controls['x_interval'].insert(tk.END, str(sug))
            except:
                return


    def update_settings(submit=False):
        current_tab = notebook.select()
        tab_index = notebook.index(current_tab)
        tab = tabs[tab_index]
        exp_text = tab.controls['Exp_input'].get("1.0", tk.END)

        if exp_text == '' or '如果第一次用，请点击“加载案例”，熟悉使用方法。' in exp_text:
            # 根据右侧下拉列表颜色，改按钮颜色
            the_color = tab.controls['lcor_list'].get().strip()
            if the_color in colors_dict:
                tab.controls['color_button'].config(background=colors_dict[the_color])
                tab.controls['print_log'].configure(state='normal')
                tab.controls['print_log'].delete("1.0", tk.END)
                tab.controls['print_log'].configure(foreground='blue')
                tab.controls['print_log'].insert(tk.END, f'用户成功选择颜色：颜色值{the_color}。')
                tab.controls['print_log'].configure(state='disabled')
            else:
                # 判断the_color是不是正确的十六进制颜色，#开头的
                if check_hex_color(the_color):
                    tab.controls['color_button'].config(background=the_color)
                    tab.controls['print_log'].configure(state='normal')
                    tab.controls['print_log'].delete("1.0", tk.END)
                    tab.controls['print_log'].configure(foreground='blue')
                    tab.controls['print_log'].insert(tk.END, f'用户成功选择颜色：颜色值{the_color}。')
                    tab.controls['print_log'].configure(state='disabled')
                else:
                    tab.controls['print_log'].configure(state='normal')
                    tab.controls['print_log'].delete("1.0", tk.END)
                    tab.controls['print_log'].configure(foreground='#b75b00')
                    tab.controls['print_log'].insert(tk.END, f'警告：颜色值{the_color}无效，将继续保持原来的旧颜色。')
                    tab.controls['print_log'].configure(state='disabled')
            return

        if tab_index != 2:
            the_expr_name = tab.controls['expr_list'].get().strip()
            cur_index_list = setting_dict[tab_index]['fn_name']
            get_fn_index = cur_index_list.index(the_expr_name)
        if tab_index == 1 or tab_index == 2:
            the_region_name = tab.controls['region_list'].get().strip()
            cur_region_list = setting_dict[tab_index]['region_name']
            get_region_index = cur_region_list.index(the_region_name)

        if submit:
            if tab_index == 0:
                setting_dict[tab_index]['lw_list'][get_fn_index] = float(tab.controls['lw_list'].get().strip())
                setting_dict[tab_index]['lsy_list'][get_fn_index] = tab.controls['lsy_list'].get().strip()
                setting_dict[tab_index]['lcor_list'][get_fn_index] = tab.controls['lcor_list'].get().strip()
                setting_dict[tab_index]['mark_list'][get_fn_index] = tab.controls['mark_list'].get().strip()
                setting_dict[tab_index]['marksize_list'][get_fn_index] = float(tab.controls['marksize_list'].get().strip())
            if tab_index == 1:
                setting_dict[tab_index]['the_marker'][get_fn_index] = tab.controls['the_marker'].get().strip() # NEW
            if tab_index == 1 or tab_index == 2:
                setting_dict[tab_index]['lcor_list'][get_region_index] = tab.controls['lcor_list'].get().strip()
                setting_dict[tab_index]['pattern_list'][get_region_index] = tab.controls['pattern_list'].get().strip()
                setting_dict[tab_index]['the_marker_posx'][get_region_index] = float(tab.controls['the_marker_posx'].get().strip())
                setting_dict[tab_index]['the_marker_posy'][get_region_index] = float(tab.controls['the_marker_posy'].get().strip())
            if tab_index == 3:
                setting_dict[tab_index]['lcor_list'][get_fn_index] = tab.controls['lcor_list'].get().strip()
                setting_dict[tab_index]['alpha_3d'][get_fn_index] = float(tab.controls['alpha_3d'].get().strip())
        else:
            # 显示设置
            if tab_index == 0:
                for name_ in ['lw_list', 'marksize_list']:
                    the_gets = [str(em) for em in setting_dict[tab_index][name_]]
                    #tab.controls[name_]['values'] = the_gets
                    the_get = the_gets[get_fn_index]
                    tab.controls[name_].set(the_get)

                for name_ in ['lsy_list', 'lcor_list', 'mark_list']:
                    the_gets = setting_dict[tab_index][name_]
                    #tab.controls[name_]['values'] = the_gets
                    the_get = the_gets[get_fn_index]
                    tab.controls[name_].set(the_get)

            if tab_index == 1:
                the_get = setting_dict[tab_index]['the_marker'][get_fn_index]
                tab.controls['the_marker'].delete(0, tk.END)
                tab.controls['the_marker'].insert(0, the_get.replace('\\\\', '\\')) # NEW

            if tab_index == 1 or tab_index == 2:
                for name_ in ['lcor_list', 'pattern_list']:
                    the_gets = setting_dict[tab_index][name_]
                    #tab.controls[name_]['values'] = the_gets
                    the_get = the_gets[get_region_index]
                    tab.controls[name_].set(the_get)

                for name_ in ['the_marker_posx', 'the_marker_posy']:
                    the_get = setting_dict[tab_index][name_][get_region_index]
                    tab.controls[name_].delete(0, tk.END)
                    tab.controls[name_].insert(0, the_get)

            if tab_index == 3:
                name_ = 'lcor_list'
                the_gets = setting_dict[tab_index][name_]
                #tab.controls[name_]['values'] = the_gets
                the_get = the_gets[get_fn_index]
                tab.controls[name_].set(the_get)

                name_ = 'alpha_3d'
                the_gets = [str(em) for em in setting_dict[tab_index][name_]]
                #tab.controls[name_]['values'] = the_gets
                the_get = the_gets[get_fn_index]
                tab.controls[name_].delete(0, tk.END)
                tab.controls[name_].insert(0, the_get)

        # 根据右侧下拉列表颜色，改按钮颜色
        the_color = tab.controls['lcor_list'].get().strip()
        if the_color in colors_dict:
            tab.controls['color_button'].config(background=colors_dict[the_color])
            tab.controls['print_log'].configure(state='normal')
            tab.controls['print_log'].delete("1.0", tk.END)
            tab.controls['print_log'].configure(foreground='blue')
            tab.controls['print_log'].insert(tk.END, f'用户成功选择颜色：颜色值{the_color}。')
            tab.controls['print_log'].configure(state='disabled')
        else:
            # 判断the_color是不是正确的十六进制颜色，#开头的
            if check_hex_color(the_color):
                tab.controls['color_button'].config(background=the_color)

                tab.controls['print_log'].configure(state='normal')
                tab.controls['print_log'].delete("1.0", tk.END)
                tab.controls['print_log'].configure(foreground='blue')
                tab.controls['print_log'].insert(tk.END, f'用户成功选择颜色：颜色值{the_color}。')
                tab.controls['print_log'].configure(state='disabled')
            else:
                tab.controls['print_log'].configure(state='normal')
                tab.controls['print_log'].delete("1.0", tk.END)
                tab.controls['print_log'].configure(foreground='#b75b00')
                tab.controls['print_log'].insert(tk.END, f'警告：颜色值{the_color}无效，将继续保持原来的旧颜色。')
                tab.controls['print_log'].configure(state='disabled')

        #print(setting_dict)

    # 定义按钮回调函数（需要根据实际功能完善）
    def on_convert():
        current_tab = notebook.select()
        tab_index = notebook.index(current_tab)
        tab = tabs[tab_index]
        exp_text = tab.controls['Exp_input'].get("1.0", tk.END)
        if exp_text == '' or '如果第一次用，请点击“加载案例”' in exp_text:
            messagebox.showerror("未操作提示", "请输入表达式，一行一个！")
            return

        code_str, variables_str, expression_indexs = convert_pycode(exp_text)
        if code_str:
            # 更新x_list和y_list
            variables = variables_str.split(", ")
            tab.controls['x_list']['values'] = variables

            if not tab.controls['x_list'].get().strip():
                tab.controls['x_list'].set(variables[0])
                update_var_list()

            if tab.controls['y_list']:
                tab.controls['y_list']['values'] = variables
                if not tab.controls['y_list'].get().strip():
                    if len(variables) > 1:
                        tab.controls['y_list'].set(variables[1])
                        update_var_list()


            # 初始化设置列表（有函数的部分）*************************************
            # 载入函数名列表
            the_expr_list = [em for em in expression_indexs.keys()]
            expr_num = len(the_expr_list)
            if tab_index != 2:
                tab.controls['expr_list']['values'] = the_expr_list
                setting_dict[tab_index]['fn_name'] = the_expr_list.copy()
                tab.controls['expr_list'].set(the_expr_list[0])

            # 更新设置字典
            if tab_index == 0:
                for item_ in [('lw_list', [1.0]*expr_num), ('lsy_list', global_lsy), ('lcor_list', global_colors),
                              ('mark_list', global_mark), ('marksize_list', [3.5]*expr_num)]:
                    setting_dict[tab_index][item_[0]] = []
                    for i in range(expr_num):
                        setting_dict[tab_index][item_[0]].append(item_[1][i])

            if tab_index == 1:
                item_ = ('the_marker', the_expr_list)
                setting_dict[tab_index][item_[0]] = []
                for i in range(expr_num):
                    setting_dict[tab_index][item_[0]].append(item_[1][i])  # 标记 $$$
                tab.controls['the_marker'].delete(0, tk.END)
                tab.controls['the_marker'].insert(tk.END, the_expr_list[0])

            if tab_index == 3:
                for item_ in [('lcor_list', global_colors), ('alpha_3d', [0.8] * expr_num)]:
                    setting_dict[tab_index][item_[0]] = []
                    for i in range(expr_num):
                        setting_dict[tab_index][item_[0]].append(item_[1][i])

            # 更新变量**************************************************
            update_settings(submit=True)
            # 完成********************************************************

            tab.controls['print_log'].configure(state='normal')
            tab.controls['print_log'].delete("1.0", tk.END)
            tab.controls['print_log'].configure(foreground='blue')
            tab.controls['print_log'].insert(tk.END, "公式识别成功！")
            tab.controls['print_log'].configure(state='disabled')
            tab.controls['buttons']['btn_convert'].configure(text='公式重新识别')
        else:
            # 识别失败，显示错误信息
            tab.controls['print_log'].configure(state='normal')
            tab.controls['print_log'].delete("1.0", tk.END)
            tab.controls['print_log'].configure(foreground='red')
            tab.controls['print_log'].insert(tk.END, variables_str)
            tab.controls['print_log'].configure(state='disabled')

    def validate_y_selection(x_list, y_list):
        x_val = x_list.get()
        y_val = y_list.get()
        if x_val == y_val:
            messagebox.showerror("选择错误", "y轴和x轴参数名应不同，请重新选择")
            y_list.set('')
        else:
            update_var_list()

    def validate_x_selection(x_list, y_list):
        x_val = x_list.get()
        y_val = y_list.get()
        if x_val == y_val:
            messagebox.showerror("选择错误", "y轴和x轴参数名应不同，请重新选择")
            x_list.set('')
        else:
            update_var_list()

    def update_var_list():
        current_tab = notebook.select()
        tab_index = notebook.index(current_tab)
        tab = tabs[tab_index]
        exp_text = tab.controls['Exp_input'].get("1.0", tk.END)
        code_str, variables_str, _ = convert_pycode(exp_text)
        variables = variables_str.split(", ")

        last_assi_text = tab.controls['Assigns_input'].get("1.0", tk.END).strip()
        if last_assi_text != '':
            last_assi = [tuple(pair.strip().split(" = ")) for pair in last_assi_text.split(",")]
            # 可选：将数字转为 float
            last_assi_result = [(k, float(v)) for k, v in last_assi]
            last_params = dict(last_assi_result)
        else:
            last_params = {}

        # 更新Assigns_input
        selected_x = tab.controls['x_list'].get()
        selected_y = tab.controls['y_list'].get() if tab.controls['y_list'] else None
        assigns = ""
        for var in variables:
            if var != selected_x and var != selected_y:
                if var in last_params:
                    assigns += f"{var} = {last_params[var]}, "
                else:
                    assigns += f"{var} = 0.0, "
        tab.controls['Assigns_input'].delete("1.0", tk.END)
        tab.controls['Assigns_input'].insert(tk.END, assigns.rstrip(", "))

        tab.controls['x_name'].delete(0, tk.END)
        if selected_x in greek_letters:
            tab.controls['x_name'].insert(tk.END, '$\\'+selected_x+'$')
        else:
            tab.controls['x_name'].insert(tk.END, '$' + selected_x + '$')

        if tab_index != 0:
            tab.controls['y_name'].delete(0, tk.END)
            if selected_y in greek_letters:
                tab.controls['y_name'].insert(tk.END, '$\\' + selected_y + '$')
            else:
                tab.controls['y_name'].insert(tk.END, '$'+selected_y+'$')


    def on_clear():
        current_tab = notebook.select()
        tab_index = notebook.index(current_tab)
        tab = tabs[tab_index]
        isclear = messagebox.askyesno("提示", "确认清空函数输入框？")
        if not isclear:
            return
        tab.controls['Exp_input'].delete("1.0", tk.END)
        tab.controls['Assigns_input'].delete("1.0", tk.END)
        tab.controls['buttons']['btn_convert'].configure(text='公式识别')

        tab.controls['Exp_input'].insert('1.0', hint_text)
        tab.controls['Exp_input'].tag_configure("hint", foreground="gray")
        tab.controls['Exp_input'].tag_add("hint", "1.0", tk.END)


    def import_case():
        current_tab = notebook.select()
        tab_index = notebook.index(current_tab)
        tab = tabs[tab_index]
        tab_name = notebook.tab(current_tab, "text")

        if tab_name == '绘制仿真折线图':
            content = r"""
# 定义符号
alpha, b, c_n, c_r, delta, E, e_n, e_r, k, p_e = symbols('alpha, b, c_n, c_r, delta, E, e_n, e_r, k, p_e')

# 表达式
expressions = {
	'$\\pi_r^{NW}$': E*p_e+(k*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2)/(8*(k+alpha*delta*(1-alpha*delta))**2),
	'$\\pi_r^{BW}$': E*p_e + ( k*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/(8*(k+delta-delta**2)**2),
	'$\\pi_r^{NS}$': E*p_e + ((k+2*alpha*delta)*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2 )/(8*(k+alpha*delta*(2-alpha*delta))**2),
	'$\\pi_r^{BS}$': E*p_e + ( (k+2*delta)*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/( 8*(k+2*delta-delta**2)**2),
}

# 参数赋值
assigns = {E : 2.0, alpha : 0.9, c_n : 0.2, c_r : 0.1, delta : 0.8, e_n : 1.0, e_r : 0.6, k : 1.1, p_e : 0.1}

# 要分析的参数，及其取值范围
the_var = b
ranges = [0, 0.08, 0.01]

# xy轴的名字
x_name = '(a) Parameter $b$'
y_name = '$\\pi_r$'

# 图片保存路径、文件名
save_dir = None

# 图例的方位
location = 'best'

# 图例的列数
ncol = 1

# 图片中字号的大小
fsize = 17

# 图片大小
figsize = [6, 5]

# x轴刻度及轴标签旋转
xt_rotation = 0
xrotation = 0
yrotation = 0

# 线的风格
linestyles = ['-', (0, (5, 5)), '--', '-.', None]

# 线粗，默认均1.0
linewidth = [1.5, 1.5, 1.5, 1.5] 

# 线上的标记符号
markers = ['o', 's', '*', 'P']

# 标记符号的大小，默认均3.5。
markersize = [4.0, 4.0, 4.0, 4.0]

# 线的颜色
colors = ['red', 'blue', 'black', 'chocolate']

# 去除网格
isgrid = False

# 分别为x/y轴刻度值距离横轴的距离。
xpad = 3
ypad = 3

# 分别为x/y轴名字标签距离纵轴刻度的距离。
xlabelpad = 9
ylabelpad = 9

# 坐标轴字体大小
xlabelsize = 'auto'
ylabelsize = 'auto'
legendsize = 'auto'

# 传给draw_lines函数
the_plt = draw_lines(expressions=expressions, assigns=assigns, the_var=the_var, ranges=ranges, x_name=x_name, y_name=y_name, 
    save_dir=save_dir, location=location, ncol=ncol, fsize=fsize, figsize=figsize, xt_rotation=xt_rotation,
    xrotation=xrotation, yrotation=yrotation, linestyles=linestyles, linewidth=linewidth, markers=markers,
    markersize=markersize, colors=colors, isgrid=isgrid, xpad=xpad, ypad=ypad, xlabelpad=xlabelpad, ylabelpad=ylabelpad,
    xlabelsize=xlabelsize, ylabelsize=ylabelsize, legendsize=legendsize)
"""
        elif tab_name == '绘制模式比较图':
            content = r"""
# 定义符号
alpha, b, c_n, c_r, delta, E, e_n, e_r, k, p_e = symbols('alpha, b, c_n, c_r, delta, E, e_n, e_r, k, p_e')

# 表达式
expressions = {
	'$\\pi_r^{NW}$': E*p_e+(k*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2)/(8*(k+alpha*delta*(1-alpha*delta))**2),
	'$\\pi_r^{BW}$': E*p_e + ( k*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/(8*(k+delta-delta**2)**2),
	'$\\pi_r^{NS}$': E*p_e + ((k+2*alpha*delta)*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2 )/(8*(k+alpha*delta*(2-alpha*delta))**2),
	'$\\pi_r^{BS}$': E*p_e + ( (k+2*delta)*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/( 8*(k+2*delta-delta**2)**2),
}

# 参数赋值
assigns = {E : 2.0, c_n : 0.2, c_r : 0.1, delta : 0.8, e_n : 1.0, e_r : 0.6, k : 1.1, p_e : 0.1}

# 要分析的参数，及其取值范围
the_var_x = alpha
start_end_x = [0.7, 0.8] 
the_var_y = b
start_end_y = [0, 0.08] 

# xy轴的名字
x_name = '$\\alpha$ \n (b) With blockchain' 
y_name = '$b$'  

# 图片保存路径、文件名
save_dir = None 

# 四个表达式分别达到最大时显示的标签、区域背景颜色和区域图案。
texts = ['NW', 'BW', 'NS', 'BS']
colors = ['beige', 'wheat', 'olivedrab', 'silver', 'darkgrey', 'grey', 'dimgrey', 'wheat', 'beige', 'slategrey', 'plum', 'cadetblue', 'gold', 'darkgoldenrod', 'darkcyan', 'indigo', 'chocolate', 'olivedrab', 'teal', 'navy', 'firebrick', 'darkgreen']
patterns = ['xx', '--', '..', '||', '..', 'oo', '++', '**', '\\\\\\\\', '////', '-', 'x', '|', '.', 'o', '+', '*', '\\\\', '//', '---', 'xxx', '|||', '...', 'ooo', '+++', '***', '\\\\\\\\\\\\', '//////']

# 全局字号
fsize = 17

# 绘图精度
precision = 1000

# 区域标签字号增量
text_fsize_add = 1 

# 图片大小
figsize = [6, 5] 

# x轴标签名旋转角度（0为不旋转）
xrotation = 0    

# y轴标签名旋转角度（0为不旋转）。
yrotation = 0  

# 线粗
linewidths = 0.2 

# x/y轴名字标签距离横轴刻度的距离
xlabelpad = 10
ylabelpad = 10

# 自定义坐标轴字体大小，默认'auto'，自动和fsize一样大
xlabelsize = 'auto'
ylabelsize = 'auto' 

# 标签背景色和位置偏移自定义设置，默认'auto'自动
pattern_colors = 'auto'

# 区域标签较原来的偏移量，(x方向，y方向) 例如 [(0, 0), (0, 0), (0, 0), (0, 0)]
pattern_moves = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)] 

# 传给draw_max_area函数
the_plt = draw_max_area(expressions=expressions, assigns=assigns, 
              the_var_x=the_var_x, start_end_x=start_end_x, 
              the_var_y=the_var_y, start_end_y=start_end_y, x_name=x_name, y_name=y_name, 
              fsize=fsize, texts=texts, text_fsize_add=text_fsize_add,
              save_dir=save_dir, figsize=figsize, colors=colors, patterns=patterns,
              xrotation=xrotation, yrotation=yrotation, linewidths=linewidths,
             xlabelsize=xlabelsize, ylabelsize=ylabelsize, pattern_colors=pattern_colors, 
              pattern_moves=pattern_moves, xlabelpad=xlabelpad, ylabelpad=ylabelpad, precision=precision)
"""
        elif tab_name == '绘制关系区域图':
            content = r"""
# 定义符号
alpha, b, c_n, c_r, delta, E, e_n, e_r, k, p_e = symbols('alpha, b, c_n, c_r, delta, E, e_n, e_r, k, p_e')

# 表达式
expressions = {
	'$\\pi_r^{NW}$': E*p_e+(k*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2)/(8*(k+alpha*delta*(1-alpha*delta))**2),
	'$\\pi_r^{BW}$': E*p_e + ( k*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/(8*(k+delta-delta**2)**2),
	'$\\pi_r^{NS}$': E*p_e + ((k+2*alpha*delta)*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2 )/(8*(k+alpha*delta*(2-alpha*delta))**2),
	'$\\pi_r^{BS}$': E*p_e + ( (k+2*delta)*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/( 8*(k+2*delta-delta**2)**2),
}

# 参数赋值
assigns = {E : 2.0, c_n : 0.2, c_r : 0.1, delta : 0.8, e_n : 1.0, e_r : 0.6, k : 1.1, p_e : 0.1}

# 要分析的参数，及其取值范围
the_var_x = alpha
start_end_x = [0.7, 0.8] 
the_var_y = b
start_end_y = [0, 0.08] 

# xy轴的名字
x_name = '$\\alpha$ \n (b) With blockchain' 
y_name = '$b$'  

# 图片保存路径、文件名
save_dir = None 

# 每个关系区域的标签前缀、编号样式、背景颜色和图案。
# 前缀。可以是"区域"也可以是"Region"，默认"Region"。
prefix = 'Region'

# 序号标记风格。有三种可选："roman", "letter" 和"number"，分别表示罗马数字、大写英文字母和阿拉伯数字。
numbers = 'roman' 

# 区域颜色
colors = ['beige', 'green', 'red', 'plum', 'wheat', 'dimgrey', 'dimgrey', 'wheat', 'beige', 'slategrey', 'plum', 'cadetblue', 'gold', 'darkgoldenrod', 'darkcyan', 'indigo', 'chocolate', 'olivedrab', 'teal', 'navy', 'firebrick', 'darkgreen']
patterns = ['..', '--', 'xx', '+', '**', None, '++', '**', '\\\\\\\\', '////', '-', 'x', '|', '.', 'o', '+', '*', '\\\\', '//', '---', 'xxx', '|||', '...', 'ooo', '+++', '***', '\\\\\\\\\\\\', '//////']

# 全局字号
fsize = 17

# 绘图精度
precision = 1000

# 区域标签字号增量
text_fsize_add = -2
 
# 图片大小。
figsize = [9, 5] 

# x轴标签名旋转角度（0为不旋转）
xrotation = 0  
 
# y轴标签名旋转角度（0为不旋转）
yrotation = 0  

# 线粗
linewidths = 0.1

# x/y轴名字标签距离横轴刻度的距离
xlabelpad = 10
ylabelpad = 10

# 自定义坐标轴字体大小，默认'auto'，自动和fsize一样大
xlabelsize = 'auto'
ylabelsize = 'auto'
legendsize = 'auto'

# 标签背景色和位置偏移自定义设置，默认'auto'自动
pattern_colors = 'auto'
pattern_moves =  [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]    

# 传给draw_detail_area函数
the_plt = draw_detail_area(expressions=expressions, assigns=assigns, 
        the_var_x=the_var_x, start_end_x=start_end_x, the_var_y=the_var_y, start_end_y=start_end_y, 
        x_name=x_name, y_name=y_name, fsize=fsize, text_fsize_add=text_fsize_add,
        save_dir=save_dir, figsize=figsize, colors=colors, patterns=patterns, precision=precision,
        xrotation=xrotation, yrotation=yrotation, linewidths=linewidths,
        prefix=prefix, numbers=numbers, xlabelsize=xlabelsize, ylabelsize=ylabelsize, legendsize=legendsize, 
      pattern_colors=pattern_colors, pattern_moves=pattern_moves, xlabelpad=xlabelpad, ylabelpad=ylabelpad)

"""
        else:
            content = r"""
alpha, b, c_n, c_r, delta, E, e_n, e_r, k, p_e = symbols('alpha, b, c_n, c_r, delta, E, e_n, e_r, k, p_e')
expressions = {
	'$\\pi_r^{NW}$': E*p_e+(k*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2)/(8*(k+alpha*delta*(1-alpha*delta))**2),
	'$\\pi_r^{BW}$': E*p_e + ( k*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/(8*(k+delta-delta**2)**2),
	'$\\pi_r^{NS}$': E*p_e + ((k+2*alpha*delta)*(alpha*delta*(c_n+e_n*p_e)-(c_r+e_r*p_e))**2 )/(8*(k+alpha*delta*(2-alpha*delta))**2),
	'$\\pi_r^{BS}$': E*p_e + ( (k+2*delta)*(delta*(c_n+e_n*p_e)-(c_r+e_r*p_e+b))**2 )/( 8*(k+2*delta-delta**2)**2),
}
assigns = {E:2.0, c_n:0.2, c_r:0.1, delta:0.8, e_n:1.0, e_r:0.6, k:1.1, p_e:0.1}
the_var_x = alpha
start_end_x = [0.7, 0.8] 
the_var_y = b
start_end_y = [0, 0.08] 
x_name = '$\\alpha$' 
y_name = '$b$'  
z_name = '$\\pi_r$'
save_dir = None 
color_alpha = [0.8, 0.8, 0.8, 0.8] 
location = 'north' 
ncol = 4
fsize = 17
# 绘图精度
precision = 1000
figsize = [7, 5]
xrotation = 0
yrotation = 0
zrotation = 90
isgrid = True
colors = ['red', 'blue', 'darkgoldenrod', 'green']
edgecolor = 'black'
linestyles = ['-', '--', '-.', ':', None, (0, (1, 10)), (0, (5, 10)), (0, (3, 10, 1, 10, 1, 10)), (5, (10, 3)), (0, (5, 5)), (0, (5, 1))]
linewidth = 0.5 
density = 50 
elevation = 15
azimuth = 45
left_margin = 0
bottom_margin = 0
right_margin = 1
top_margin = 1
xpad = 3
ypad = 3
zpad = 3
xlabelpad = 10
ylabelpad = 10
zlabelpad = 10
xlabelsize = 'auto'
ylabelsize = 'auto'
zlabelsize = 'auto'
legendsize = 'auto'

# 传给draw_3D函数
the_plt = draw_3D(expressions=expressions, assigns=assigns, the_var_x=the_var_x, start_end_x=start_end_x, the_var_y=the_var_y, 
        start_end_y=start_end_y, x_name=x_name, y_name=y_name, z_name=z_name, 
        save_dir=save_dir, color_alpha=color_alpha, location=location, ncol=ncol, fsize=fsize, figsize=figsize, 
        xrotation=xrotation, yrotation=yrotation, zrotation=zrotation, isgrid=isgrid, colors=colors, precision=precision, 
        edgecolor=edgecolor, linestyles=linestyles, linewidth=linewidth, density=density, elevation=elevation, azimuth=azimuth, 
        left_margin=left_margin, bottom_margin=bottom_margin, right_margin=right_margin, top_margin=top_margin,
        xpad=xpad, ypad=ypad, zpad=zpad, xlabelpad=xlabelpad, ylabelpad=ylabelpad, zlabelpad=zlabelpad,
       xlabelsize=xlabelsize, ylabelsize=ylabelsize, zlabelsize=zlabelsize, legendsize=legendsize)
"""
        if "“加载案例”" not in tab.controls['Exp_input'].get("1.0", tk.END):
            save_choice = messagebox.askyesno("提示", "引入案例会替换之前的信息，是否继续引入案例？")
            if not save_choice:
                return
        decode_codestr(content)
        tab.controls['buttons']['btn_convert'].configure(text='公式重新识别')


    def decode_codestr(txt): # 代码-->界面
        current_tab = notebook.select()
        tab_index = notebook.index(current_tab)
        tab = tabs[tab_index]
        tab_name = notebook.tab(current_tab, "text")

        if 'draw_lines' in txt:
            try_type = '绘制仿真折线图'
        elif 'draw_3D' in txt:
            try_type = '绘制仿真三维图'
        elif 'draw_max_area' in txt:
            try_type = '绘制模式比较图'
        elif 'draw_detail_area' in txt:
            try_type = '绘制关系区域图'
        else:
            try_type = '其他代码'

        if tab_name != try_type:
            messagebox.showerror("选择错误", f"当前代码的绘图类型`{try_type}`与该面板绘图类型`{tab_name}`不一致，请重新选择！")
            return

        pattern = re.compile(r"expressions\s*=\s*\{([\s\S]*?)\}\n", re.MULTILINE)
        match = pattern.search(txt)

        Exp_input_get = match.group(1)
        # 进行替换操作
        Exp_input_get = Exp_input_get.replace("'", "").replace(",", "").replace(":", "=").replace("**", "^").replace("\t", "").replace('\\\\', '\\') # NEW
        # print(Exp_input_get)

        tab.controls['Exp_input'].delete("1.0", tk.END)
        tab.controls['Exp_input'].insert(tk.END, Exp_input_get.strip())

        pattern = re.compile(r"assigns\s*=\s*\{([\s\S]*?)\}", re.MULTILINE)
        match = pattern.search(txt)
        if match:
            Assi_input_get = match.group(1)
            # 进行替换操作
            Assi_input_get = Assi_input_get.replace(":", "=").replace("\\\\", "\\").strip()  # NEW
            tab.controls['Assigns_input'].delete("1.0", tk.END)
            tab.controls['Assigns_input'].insert(tk.END, Assi_input_get.strip())
        else:
            tab.controls['Assigns_input'].delete("1.0", tk.END)

        pattern = re.compile(r"x_name\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
        match = pattern.search(txt)
        if match:
            the_get = match.group(1)
            the_get = the_get.replace("r'", "").replace("'", "").replace("\\\\", "\\").strip()  # NEW
            tab.controls['x_name'].delete(0, tk.END)
            tab.controls['x_name'].insert(0, the_get)
        else:
            tab.controls['x_name'].delete(0, tk.END)

        pattern = re.compile(r"y_name\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
        match = pattern.search(txt)
        if match:
            the_get = match.group(1)
            the_get = the_get.replace("r'", "").replace("'", "").replace("\\\\", "\\").strip()  # NEW
            tab.controls['y_name'].delete(0, tk.END)
            tab.controls['y_name'].insert(0, the_get)
        else:
            tab.controls['y_name'].delete(0, tk.END)

        pattern = re.compile(r"fsize\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
        match = pattern.search(txt)
        the_get = match.group(1)
        tab.controls['fsize'].delete(0, tk.END)
        tab.controls['fsize'].insert(0, the_get)

        pattern = re.compile(r"xrotation\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
        match = pattern.search(txt)
        the_get = match.group(1)
        tab.controls['xrotation'].delete(0, tk.END)
        tab.controls['xrotation'].insert(0, the_get)

        pattern = re.compile(r"yrotation\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
        match = pattern.search(txt)
        the_get = match.group(1)
        tab.controls['yrotation'].delete(0, tk.END)
        tab.controls['yrotation'].insert(0, the_get)

        pattern = re.compile(r"figsize\s*=\s*\[(.*?)\]", re.MULTILINE)
        match = pattern.search(txt)
        the_get = match.group(1)
        number_list = eval(f"[{the_get}]")
        number_list = [str(em).strip() for em in number_list]
        tab.controls['figsizeW'].delete(0, tk.END)
        tab.controls['figsizeW'].insert(0, number_list[0].strip())
        tab.controls['figsizeH'].delete(0, tk.END)
        tab.controls['figsizeH'].insert(0, number_list[1].strip())

        code_str, variables_str, expression_indexs = convert_pycode(Exp_input_get)
        if code_str:
            tab.controls['print_log'].configure(state='normal')
            tab.controls['print_log'].delete("1.0", tk.END)
            tab.controls['print_log'].configure(foreground='blue')
            tab.controls['print_log'].insert(tk.END, "公式识别成功！")
            tab.controls['print_log'].configure(state='disabled')
        else:
            # 识别失败，显示错误信息
            tab.controls['print_log'].configure(state='normal')
            tab.controls['print_log'].delete("1.0", tk.END)
            tab.controls['print_log'].configure(foreground='red')
            tab.controls['print_log'].insert(tk.END, variables_str)
            tab.controls['print_log'].configure(state='disabled')
            return

        # 初始化设置列表（有函数的部分）*************************************
        the_expr_list = [em for em in expression_indexs.keys()]
        if tab_index != 2:
            tab.controls['expr_list']['values'] = the_expr_list
            setting_dict[tab_index]['fn_name'] = the_expr_list.copy()
            tab.controls['expr_list'].set(the_expr_list[0])

        if tab_index == 0:
            for item in [('linewidth', 'lw_list'), ('markersize', 'marksize_list')]:
                pattern = re.compile(item[0] + r"\s*=\s*\[(.*?)\]", re.MULTILINE)
                match = pattern.search(txt)
                the_get = match.group(1)
                #the_list0 = the_get.split(",")
                the_list0 = eval(f"[{the_get}]")
                the_list = [float(em) for em in the_list0]
                setting_dict[tab_index][item[1]] = the_list
                tab.controls[item[1]].set(the_list[0])

            for item in [('linestyles', 'lsy_list'), ('colors', 'lcor_list'), ('markers', 'mark_list')]:
                pattern = re.compile(item[0] + r"\s*=\s*\[(.*?)\]", re.MULTILINE)
                match = pattern.search(txt)
                the_get = match.group(1)
                the_get = the_get.replace("r'", "").strip()
                #the_list = the_get.split(",")
                the_list = eval(f"[{the_get}]")
                the_list = [str(em).strip() for em in the_list]
                tab.controls[item[1]].set(the_list[0])
                #the_list = [None if item == 'None' else item for item in the_list]
                setting_dict[tab_index][item[1]] = the_list

        if tab_index == 1:
            item = ('texts', 'the_marker')
            pattern = re.compile(item[0] + r"\s*=\s*\[(.*?)\]", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_get = the_get.replace("r'", "").strip()
            #the_list = the_get.split(",")
            the_list = eval(f"[{the_get}]")
            the_list = [str(em).replace("\\\\", "\\").strip()  for em in the_list]  # NEW
            tab.controls[item[1]].delete(0, tk.END)
            tab.controls[item[1]].insert(0, the_list[0])
            #the_list = [None if item == 'None' else item for item in the_list]
            setting_dict[tab_index][item[1]] = the_list

            # 加载区域设置
            for item in [('colors', 'lcor_list'), ('patterns', 'pattern_list')]:
                pattern = re.compile(item[0] + r"\s*=\s*\[(.*?)\]", re.MULTILINE)
                match = pattern.search(txt)
                the_get = match.group(1)
                #the_list0 = the_get.split(",")
                the_list0 = eval(f"[{the_get}]")
                the_list = [str(em).strip() for em in the_list0]
                setting_dict[tab_index][item[1]] = the_list
                tab.controls[item[1]].set(the_list[0])

            pattern = re.compile(r"pattern_moves\s*=\s*\[(.*?)\]", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_list0 = eval(f"[{the_get}]")
            get_posx = []
            get_posy = []
            for em in the_list0:
                get_posx.append(em[0])
                get_posy.append(em[1])
            setting_dict[tab_index]['the_marker_posx'] = get_posx
            tab.controls['the_marker_posx'].delete(0, tk.END)
            tab.controls['the_marker_posx'].insert(0, str(get_posx[0]))
            setting_dict[tab_index]['the_marker_posy'] = get_posy
            tab.controls['the_marker_posy'].delete(0, tk.END)
            tab.controls['the_marker_posy'].insert(0, str(get_posy[0]))

        if tab_index == 2:
            # 加载区域设置
            for item in [('colors', 'lcor_list'), ('patterns', 'pattern_list')]:
                pattern = re.compile(item[0] + r"\s*=\s*\[(.*?)\]", re.MULTILINE)
                match = pattern.search(txt)
                the_get = match.group(1)
                # the_list0 = the_get.split(",")
                the_list0 = eval(f"[{the_get}]")
                the_list = [str(em).strip() for em in the_list0]
                setting_dict[tab_index][item[1]] = the_list
                tab.controls[item[1]].set(the_list[0])

            pattern = re.compile(r"pattern_moves\s*=\s*\[(.*?)\]", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_list0 = eval(f"[{the_get}]")
            get_posx = []
            get_posy = []
            for em in the_list0:
                get_posx.append(em[0])
                get_posy.append(em[1])
            setting_dict[tab_index]['the_marker_posx'] = get_posx
            tab.controls['the_marker_posx'].delete(0, tk.END)
            tab.controls['the_marker_posx'].insert(0, str(get_posx[0]))
            setting_dict[tab_index]['the_marker_posy'] = get_posy
            tab.controls['the_marker_posy'].delete(0, tk.END)
            tab.controls['the_marker_posy'].insert(0, str(get_posy[0]))


        if tab_index == 3:
            item = ('colors', 'lcor_list')
            pattern = re.compile(item[0] + r"\s*=\s*\[(.*?)\]", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_get = the_get.replace("r'", "").strip()
            #the_list = the_get.split(",")
            the_list = eval(f"[{the_get}]")
            the_list = [str(em).strip() for em in the_list]
            tab.controls[item[1]].set(the_list[0])
            tab.controls[item[1]].set(the_list[0])
            setting_dict[tab_index][item[1]] = the_list

            item = ('color_alpha', 'alpha_3d')
            pattern = re.compile(item[0] + r"\s*=\s*\[(.*?)\]", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            #the_list0 = the_get.split(",")
            the_list0 = eval(f"[{the_get}]")
            the_list = [float(em) for em in the_list0]
            setting_dict[tab_index][item[1]] = the_list
            tab.controls[item[1]].delete(0, tk.END)
            tab.controls[item[1]].insert(0, the_list[0])

        # 更新界面显示**************************************************
        update_settings(submit=False)
        # 完成********************************************************

        if tab_name != '绘制仿真折线图':
            pattern = re.compile(r"the_var_x\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            # 更新x_list和y_list
            variables = variables_str.split(",")
            variables = [em.strip() for em in variables]
            tab.controls['x_list']['values'] = variables
            tab.controls['y_list']['values'] = variables
            tab.controls['x_list'].set(the_get)

            pattern = re.compile(r"the_var_y\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            tab.controls['y_list'].set(the_get)

            pattern = re.compile(r"precision\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            #print(txt)
            the_get = match.group(1)
            tab.controls['prec_list'].set(the_get)  # NEW
        else:
            pattern = re.compile(r"the_var\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            # 更新x_list和y_list
            variables = variables_str.split(",")
            variables = [em.strip() for em in variables]
            tab.controls['x_list']['values'] = variables
            tab.controls['x_list'].set(the_get)

            pattern = re.compile(r"ranges\s*=\s*\[(.*?)\]", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            #number_list = the_get.split(",")
            number_list = eval(f"[{the_get}]")
            number_list = [str(em).strip() for em in number_list]
            tab.controls['x_start'].delete(0, tk.END)
            tab.controls['x_start'].insert(0, number_list[0].strip())
            tab.controls['x_end'].delete(0, tk.END)
            tab.controls['x_end'].insert(0, number_list[1].strip())
            tab.controls['x_interval'].delete(0, tk.END)
            tab.controls['x_interval'].insert(0, number_list[2].strip())


        if tab_name == '绘制仿真折线图':
            pattern = re.compile(r"location\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_get = the_get.replace("r'", "").replace("'", "").strip()
            tab.controls['location'].set(the_get)

            pattern = re.compile(r"ncol\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_get = the_get.strip()
            tab.controls['ncol'].delete(0, tk.END)
            tab.controls['ncol'].insert(0, the_get)

        if tab_name == '绘制模式比较图':
            pattern = re.compile(r"start_end_x\s*=\s*\[(.*?)\]", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            number_list = eval(f"[{the_get}]")
            number_list = [str(em).strip() for em in number_list]
            tab.controls['x_start'].delete(0, tk.END)
            tab.controls['x_start'].insert(0, number_list[0].strip())
            tab.controls['x_end'].delete(0, tk.END)
            tab.controls['x_end'].insert(0, number_list[1].strip())

            pattern = re.compile(r"start_end_y\s*=\s*\[(.*?)\]", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            number_list = eval(f"[{the_get}]")
            number_list = [str(em).strip() for em in number_list]
            tab.controls['y_start'].delete(0, tk.END)
            tab.controls['y_start'].insert(0, number_list[0].strip())
            tab.controls['y_end'].delete(0, tk.END)
            tab.controls['y_end'].insert(0, number_list[1].strip())

        if tab_name == '绘制关系区域图':
            pattern = re.compile(r"prefix\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_get = the_get.replace("'", "").strip()
            tab.controls['the_pref'].delete(0, tk.END)
            tab.controls['the_pref'].insert(0, the_get)

            pattern = re.compile(r"numbers\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_get = the_get.replace("r'", "").replace("'", "").strip()
            tab.controls['marker_way'].set(prefix2name[the_get])

            pattern = re.compile(r"start_end_x\s*=\s*\[(.*?)\]", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            number_list = eval(f"[{the_get}]")
            number_list = [str(em).strip() for em in number_list]
            tab.controls['x_start'].delete(0, tk.END)
            tab.controls['x_start'].insert(0, number_list[0].strip())
            tab.controls['x_end'].delete(0, tk.END)
            tab.controls['x_end'].insert(0, number_list[1].strip())

            pattern = re.compile(r"start_end_y\s*=\s*\[(.*?)\]", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            number_list = eval(f"[{the_get}]")
            number_list = [str(em).strip() for em in number_list]
            tab.controls['y_start'].delete(0, tk.END)
            tab.controls['y_start'].insert(0, number_list[0].strip())
            tab.controls['y_end'].delete(0, tk.END)
            tab.controls['y_end'].insert(0, number_list[1].strip())

        if tab_name == '绘制仿真三维图':
            pattern = re.compile(r"start_end_x\s*=\s*\[(.*?)\]", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            number_list = eval(f"[{the_get}]")
            number_list = [str(em).strip() for em in number_list]
            tab.controls['x_start'].delete(0, tk.END)
            tab.controls['x_start'].insert(0, number_list[0].strip())
            tab.controls['x_end'].delete(0, tk.END)
            tab.controls['x_end'].insert(0, number_list[1].strip())

            pattern = re.compile(r"start_end_y\s*=\s*\[(.*?)\]", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            number_list = eval(f"[{the_get}]")
            number_list = [str(em).strip() for em in number_list]
            tab.controls['y_start'].delete(0, tk.END)
            tab.controls['y_start'].insert(0, number_list[0].strip())
            tab.controls['y_end'].delete(0, tk.END)
            tab.controls['y_end'].insert(0, number_list[1].strip())

            pattern = re.compile(r"location\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_get = the_get.replace("r'", "").replace("'", "").strip()
            tab.controls['location'].set(the_get)

            pattern = re.compile(r"ncol\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_get = the_get.strip()
            tab.controls['ncol'].delete(0, tk.END)
            tab.controls['ncol'].insert(0, the_get)

            pattern = re.compile(r"z_name\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_get = the_get.replace("r'", "").replace("'", "").replace("\\\\", "\\").strip()  # NEW
            tab.controls['z_name'].delete(0, tk.END)
            tab.controls['z_name'].insert(0, the_get)

            pattern = re.compile(r"elevation\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_get = the_get.strip()
            tab.controls['elevation'].delete(0, tk.END)
            tab.controls['elevation'].insert(0, the_get)

            pattern = re.compile(r"azimuth\s*=\s*([\s\S]*?)(\n|$)", re.MULTILINE)
            match = pattern.search(txt)
            the_get = match.group(1)
            the_get = the_get.strip()
            tab.controls['azimuth'].delete(0, tk.END)
            tab.controls['azimuth'].insert(0, the_get)


    def import_code():
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("Double-click Python", "*.pyw"), ("Text Files", "*.txt")])
        if file_path:  # 检查文件路径是否存在
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            content = content.replace(r"lamda", r"lambda")
            if r"#the_plt.show()" not in content:
                content = content.replace(r"the_plt.show()", r"#the_plt.show()")
            decode_codestr(content)

    def compile_code():
        pycode_str = ""
        current_tab = notebook.select()
        tab_index = notebook.index(current_tab)
        tab = tabs[tab_index]
        exp_text = tab.controls['Exp_input'].get("1.0", tk.END)
        # NEW
        exp_text = convert_latex_escape(exp_text)
        code_str, variables_str, _ = convert_pycode(exp_text)

        if not code_str:
            # 识别失败，显示错误信息
            tab.controls['print_log'].configure(state='normal')
            tab.controls['print_log'].delete("1.0", tk.END)
            tab.controls['print_log'].configure(foreground='red')
            tab.controls['print_log'].insert(tk.END, variables_str)
            tab.controls['print_log'].configure(state='disabled')
            print(variables_str)
            return

        Assigns_text = tab.controls['Assigns_input'].get("1.0", tk.END).strip()
        assi_str = Assigns_text.replace("=", ":")

        x_var_name = tab.controls['x_list'].get()
        x_start_val = tab.controls['x_start'].get()
        x_end_val = tab.controls['x_end'].get()

        x_name_str = tab.controls['x_name'].get()
        y_name_str = tab.controls['y_name'].get()

        fsize_str = tab.controls['fsize'].get()
        figsizeW_str = tab.controls['figsizeW'].get()
        figsizeH_str = tab.controls['figsizeH'].get()

        xrotation_str = tab.controls['xrotation'].get()
        yrotation_str = tab.controls['yrotation'].get()

        if tab_index == 0:
            x_interval_val = tab.controls['x_interval'].get()
            location_str = tab.controls['location'].get()
            ncol_str = tab.controls['ncol'].get()

            pycode_str += f"""
{code_str}

# 参数赋值
assigns = {{{assi_str}}}

# 要分析的参数，及其取值范围
the_var = {x_var_name}
ranges = [{x_start_val}, {x_end_val}, {x_interval_val}]

# xy轴的名字
x_name = '{convert_latex_escape(x_name_str)}'
y_name = '{convert_latex_escape(y_name_str)}'

# 图片保存路径、文件名
save_dir = None

# 图例的方位
location = '{location_str}'

# 图例的列数
ncol = {ncol_str}

# 图片中字号的大小
fsize = {fsize_str}

# 图片大小
figsize = [{figsizeW_str}, {figsizeH_str}]

# x轴刻度及轴标签旋转
xt_rotation = 0
xrotation = {xrotation_str}
yrotation = {yrotation_str}

# 线的风格
linestyles = {str(setting_dict[tab_index]['lsy_list']).replace("'(", "(").replace(")'", ")")}

# 线粗，默认均1.0
linewidth = {str(setting_dict[tab_index]['lw_list'])} 

# 线上的标记符号
markers = {str(setting_dict[tab_index]['mark_list']).replace("'None'", "None")}

# 标记符号的大小，默认均3.5。
markersize = {str(setting_dict[tab_index]['marksize_list'])}

# 线的颜色
colors = {str(setting_dict[tab_index]['lcor_list']).replace("'None'", "None")}

# 去除网格
isgrid = False

# 分别为x/y轴刻度值距离横轴的距离。
xpad = 3
ypad = 3

# 分别为x/y轴名字标签距离纵轴刻度的距离。
xlabelpad = 10
ylabelpad = 10

# 坐标轴字体大小
xlabelsize = 'auto'
ylabelsize = 'auto'
legendsize = 'auto'

# 传给draw_lines函数
the_plt = draw_lines(expressions=expressions, assigns=assigns, the_var=the_var, ranges=ranges, x_name=x_name, y_name=y_name, 
    save_dir=save_dir, location=location, ncol=ncol, fsize=fsize, figsize=figsize, xt_rotation=xt_rotation,
    xrotation=xrotation, yrotation=yrotation, linestyles=linestyles, linewidth=linewidth, markers=markers,
    markersize=markersize, colors=colors, isgrid=isgrid, xpad=xpad, ypad=ypad, xlabelpad=xlabelpad, ylabelpad=ylabelpad,
    xlabelsize=xlabelsize, ylabelsize=ylabelsize, legendsize=legendsize)
#the_plt.show()
"""
        elif tab_index == 1:
            y_var_name = tab.controls['y_list'].get()
            y_start_val = tab.controls['y_start'].get()
            y_end_val = tab.controls['y_end'].get()
            precision_ = tab.controls['prec_list'].get()
            # 区域标签较原来的偏移量，(x方向，y方向) 例如 [(0, 0), (0, 0), (0, 0), (0, 0)]
            pos_xy = []
            for i in range(len(setting_dict[tab_index]['region_name'])):
                pos_xy.append((setting_dict[tab_index]['the_marker_posx'][i], setting_dict[tab_index]['the_marker_posy'][i]))

            pycode_str = f"""
{code_str}

# 参数赋值
assigns = {{{assi_str}}}

# 要分析的参数，及其取值范围
the_var_x = {x_var_name}
start_end_x = [{x_start_val}, {x_end_val}] 
the_var_y = {y_var_name}
start_end_y = [{y_start_val}, {y_end_val}] 

# xy轴的名字
x_name = '{convert_latex_escape(x_name_str)}' 
y_name = '{convert_latex_escape(y_name_str)}'  

# 图片保存路径、文件名
save_dir = None 

# 四个表达式分别达到最大时显示的标签、区域背景颜色和区域图案。
texts = {str(setting_dict[tab_index]['the_marker'])}
colors = {str(setting_dict[tab_index]['lcor_list']).replace("'None'", "None")}
patterns = {str(setting_dict[tab_index]['pattern_list']).replace("'None'", "None")}

# 全局字号
fsize = {fsize_str}

# 区域标签字号增量
text_fsize_add = 1 

# 图片大小
figsize = [{figsizeW_str}, {figsizeH_str}] 

# x轴标签名旋转角度（0为不旋转）
xrotation = {xrotation_str}  

# y轴标签名旋转角度（0为不旋转）。
yrotation = {yrotation_str} 

# 绘图精度
precision = {precision_}

# 线粗
linewidths = 0.2 

# x/y轴名字标签距离横轴刻度的距离
xlabelpad = 10
ylabelpad = 10

# 自定义坐标轴字体大小，默认'auto'，自动和fsize一样大
xlabelsize = 'auto'
ylabelsize = 'auto' 

# 标签背景色和位置偏移自定义设置，默认'auto'自动
pattern_colors = 'auto'

# 区域标签较原来的偏移量，(x方向，y方向) 例如 [(0, 0), (0, 0), (0, 0), (0, 0)]
pattern_moves = {str(pos_xy)} 

# 传给draw_max_area函数
the_plt = draw_max_area(expressions=expressions, assigns=assigns, 
              the_var_x=the_var_x, start_end_x=start_end_x, 
              the_var_y=the_var_y, start_end_y=start_end_y, x_name=x_name, y_name=y_name, 
              fsize=fsize, texts=texts, text_fsize_add=text_fsize_add, precision=precision,
              save_dir=save_dir, figsize=figsize, colors=colors, patterns=patterns,
              xrotation=xrotation, yrotation=yrotation, linewidths=linewidths,
             xlabelsize=xlabelsize, ylabelsize=ylabelsize, pattern_colors=pattern_colors, 
              pattern_moves=pattern_moves, xlabelpad=xlabelpad, ylabelpad=ylabelpad)
#the_plt.show()
"""
        elif tab_index == 2:
            y_var_name = tab.controls['y_list'].get()
            y_start_val = tab.controls['y_start'].get()
            y_end_val = tab.controls['y_end'].get()
            precision_ = tab.controls['prec_list'].get()

            the_pref_val = tab.controls['the_pref'].get()
            marker_way_val = tab.controls['marker_way'].get()

            # 区域标签较原来的偏移量，(x方向，y方向) 例如 [(0, 0), (0, 0), (0, 0), (0, 0)]
            pos_xy = []
            for i in range(len(setting_dict[tab_index]['region_name'])):
                pos_xy.append(
                    (setting_dict[tab_index]['the_marker_posx'][i], setting_dict[tab_index]['the_marker_posy'][i]))

            pycode_str = f"""
{code_str}

# 参数赋值
assigns = {{{assi_str}}}

# 要分析的参数，及其取值范围
the_var_x = {x_var_name}
start_end_x = [{x_start_val}, {x_end_val}] 
the_var_y = {y_var_name}
start_end_y = [{y_start_val}, {y_end_val}] 

# xy轴的名字
x_name = '{convert_latex_escape(x_name_str)}' 
y_name = '{convert_latex_escape(y_name_str)}'  

# 图片保存路径、文件名
save_dir = None 

# 每个关系区域的标签前缀、编号样式、背景颜色和图案。
# 前缀。可以是"区域"也可以是"Region"，默认"Region"。
prefix = '{convert_latex_escape(the_pref_val)}'

# 序号标记风格。有三种可选："roman", "letter" 和"number"，分别表示罗马数字、大写英文字母和阿拉伯数字。
numbers = '{name2prefix[marker_way_val]}' 

# 区域颜色
colors = {str(setting_dict[tab_index]['lcor_list']).replace("'None'", "None")}
patterns = {str(setting_dict[tab_index]['pattern_list']).replace("'None'", "None")}

# 全局字号
fsize = {fsize_str}

# 绘图精度
precision = {precision_}

# 区域标签字号增量
text_fsize_add = -2
 
# 图片大小。
figsize = [{figsizeW_str}, {figsizeH_str}] 

# x轴标签名旋转角度（0为不旋转）
xrotation = {xrotation_str} 
 
# y轴标签名旋转角度（0为不旋转）
yrotation = {yrotation_str} 

# 线粗
linewidths = 0.1

# x/y轴名字标签距离横轴刻度的距离
xlabelpad = 10
ylabelpad = 10

# 自定义坐标轴字体大小，默认'auto'，自动和fsize一样大
xlabelsize = 'auto'
ylabelsize = 'auto'
legendsize = 'auto'

# 标签背景色和位置偏移自定义设置，默认'auto'自动
pattern_colors = 'auto'
pattern_moves =  {str(pos_xy)}    

# 传给draw_detail_area函数
the_plt = draw_detail_area(expressions=expressions, assigns=assigns, 
        the_var_x=the_var_x, start_end_x=start_end_x, the_var_y=the_var_y, start_end_y=start_end_y, 
        x_name=x_name, y_name=y_name, fsize=fsize, text_fsize_add=text_fsize_add,
        save_dir=save_dir, figsize=figsize, colors=colors, patterns=patterns,
        xrotation=xrotation, yrotation=yrotation, linewidths=linewidths, precision=precision,
        prefix=prefix, numbers=numbers, xlabelsize=xlabelsize, ylabelsize=ylabelsize, legendsize=legendsize, 
      pattern_colors=pattern_colors, pattern_moves=pattern_moves, xlabelpad=xlabelpad, ylabelpad=ylabelpad)
#the_plt.show()
"""
        else:
            y_var_name = tab.controls['y_list'].get()
            y_start_val = tab.controls['y_start'].get()
            y_end_val = tab.controls['y_end'].get()

            z_name_str = tab.controls['z_name'].get()

            location_str = tab.controls['location'].get()
            ncol_str = tab.controls['ncol'].get()

            zrotation_str = tab.controls['zrotation'].get()
            azimuth_str = tab.controls['azimuth'].get()
            elevation_str = tab.controls['elevation'].get()

            precision_ = tab.controls['prec_list'].get()

            pycode_str = f"""
{code_str}

# 参数赋值
assigns = {{{assi_str}}}

# 要分析的参数，及其取值范围
the_var_x = {x_var_name}
start_end_x = [{x_start_val}, {x_end_val}] 
the_var_y = {y_var_name}
start_end_y = [{y_start_val}, {y_end_val}] 

# xy轴的名字
x_name = '{convert_latex_escape(x_name_str)}' 
y_name = '{convert_latex_escape(y_name_str)}'  
z_name = '{convert_latex_escape(z_name_str)}'

# 图片保存路径、文件名
save_dir = None 

# 曲面的透明度。取值范围0到1，浮点数。0表示全透明，1表示完全不透明。
color_alpha = {str(setting_dict[tab_index]['alpha_3d'])} 

# 图例的方位，可以选填的内容有'best','northeast','northwest','southwest','southeast','east','west','south','north','center'。
location = '{location_str}' 

# 图例的列数，默认为1列，即竖着排布。
ncol = {ncol_str}

# 图片中字号的大小
fsize = {fsize_str}

# 绘图精度
precision = {precision_}

# 图片的大小，写成`[宽, 高]`的形式。默认为`[7, 5]`。
figsize = [{figsizeW_str}, {figsizeH_str}]

# xrotation/yrotation: x/y轴名字标签旋转角度，默认值0，基本不需要动。
xrotation = {xrotation_str}
yrotation = {yrotation_str}

# Z轴名字标签旋转角度，默认值90，字是正的。如果Z轴的名字较长，不好看，可以设成0，字是竖倒着写的，紧贴Z轴
zrotation = {zrotation_str}

# 是否要网格。要就填True，不要就是False
isgrid = True

# 在多面图中用于按顺序制定每个面的颜色（包含标记符号的颜色）。
colors = {str(setting_dict[tab_index]['lcor_list']).replace("'None'", "None")}

# 曲面上线框的颜色。若为None，则曲面上不画线。当该参数不为None时，参数`linestyles`，`linewidth`和`density`才起作用。
edgecolor = 'black'
linestyles = {str(global_lsy).replace("'(", "(").replace(")'", ")")}
# 线粗
linewidth = 0.5 
# 曲面上画线的密度，也就是曲面横纵方向各画多少根线。
density = 50 

# 仰角 (elevation)。定义了观察者与 xy 平面之间的夹角，也就是观察者与 xy 平面之间的旋转角度。
elevation = {elevation_str}

# 方位角 (azimuth)。定义了观察者绕 z 轴旋转的角度。它决定了观察者在 xy 平面上的位置。
azimuth = {azimuth_str}

# 左、下、右、上的图片留白，默认分别为0,0,1,1。不需要动，除非不好看。
left_margin = 0
bottom_margin = 0
right_margin = 1
top_margin = 1

# 分别为/y/z轴刻度值距离横轴的距离。
xpad = 3
ypad = 3
zpad = 3

# 分别为/y/z轴名字标签距离纵轴刻度的距离。
xlabelpad = 10
ylabelpad = 10
zlabelpad = 10

# 自定义坐标轴字体大小，默认'auto'，自动和fsize一样大
xlabelsize = 'auto'
ylabelsize = 'auto'
zlabelsize = 'auto'
legendsize = 'auto'

# 传给draw_3D函数 (不要改！)
# Passed to the draw_3D function (Don't change!)
the_plt = draw_3D(expressions=expressions, assigns=assigns, the_var_x=the_var_x, start_end_x=start_end_x, the_var_y=the_var_y, 
        start_end_y=start_end_y, x_name=x_name, y_name=y_name, z_name=z_name, 
        save_dir=save_dir, color_alpha=color_alpha, location=location, ncol=ncol, fsize=fsize, figsize=figsize, 
        xrotation=xrotation, yrotation=yrotation, zrotation=zrotation, isgrid=isgrid, colors=colors, 
        edgecolor=edgecolor, linestyles=linestyles, linewidth=linewidth, density=density, elevation=elevation, azimuth=azimuth, 
        left_margin=left_margin, bottom_margin=bottom_margin, right_margin=right_margin, top_margin=top_margin,
        xpad=xpad, ypad=ypad, zpad=zpad, xlabelpad=xlabelpad, ylabelpad=ylabelpad, zlabelpad=zlabelpad,
       xlabelsize=xlabelsize, ylabelsize=ylabelsize, zlabelsize=zlabelsize, legendsize=legendsize, precision=precision)
#the_plt.show()
"""
        return pycode_str

    def check_syntax():
        # 这里应该添加语法检查的实际实现
        current_tab = notebook.select()
        tab_index = notebook.index(current_tab)
        tab = tabs[tab_index]

        pycode_str = compile_code()
        if r"#the_plt.show()" not in pycode_str:
            pycode_str = pycode_str.replace(r"the_plt.show()", r"#the_plt.show()")
        pycode_str = pycode_str.replace(r"lambda", r"lamda")
        pycode_str = pycode_str.replace(r"\lamda", r"\lambda")
        try:
            ast.parse(pycode_str)
            tab.controls['print_log'].configure(state='normal')
            tab.controls['print_log'].delete("1.0", tk.END)
            tab.controls['print_log'].configure(foreground='black')
            tab.controls['print_log'].insert(tk.END, f"OK！所有填写的信息语法上无错误！代码如下：\n\n{pycode_str}")
            tab.controls['print_log'].configure(state='disabled')
            return 'OK'
        except SyntaxError as e:
            #print(f"填写的信息存在语法错误: {e}\n\n{pycode_str}")
            # 识别失败，显示错误信息
            tab.controls['print_log'].configure(state='normal')
            tab.controls['print_log'].delete("1.0", tk.END)
            tab.controls['print_log'].configure(foreground='red')
            tab.controls['print_log'].insert(tk.END, f"填写的信息存在语法错误: {e}, 代码为：\n{pycode_str}")
            tab.controls['print_log'].configure(state='disabled')
            return 'NO'

    def draw_image():
        current_tab = notebook.select()
        tab_index = notebook.index(current_tab)
        tab = tabs[tab_index]
        # 这里应该添加绘制图片的实际实现
        ret = check_syntax()
        if ret != 'OK':
            messagebox.showerror("绘制图片", "信息有误，绘制失败。")
            return
        # 绘制成功，启用保存图片按钮
        pycode_str = compile_code()
        import sympy
        exec_vars = {}
        for name in sympy_names:
            try:
                exec_vars[name] = getattr(sympy, name)
            except AttributeError:
                print(f'提示：当前Sympy版本不支持{name}属性！')
                continue

        try:
            if r"#the_plt.show()" not in pycode_str:
                pycode_str = pycode_str.replace(r"the_plt.show()", r"#the_plt.show()")
            pycode_str = pycode_str.replace(r"lambda", r"lamda")
            pycode_str = pycode_str.replace(r"\lamda", r"\lambda")
            exec(pycode_str, exec_vars)
            value_of_plt = exec_vars.get('the_plt')
            # 获取当前的 Figure 对象
            value_fig = value_of_plt.gcf()
            show_plot(value_fig, root)
        except Exception as e:
            tab.controls['print_log'].configure(state='normal')
            tab.controls['print_log'].delete("1.0", tk.END)
            tab.controls['print_log'].configure(foreground='red')
            tab.controls['print_log'].insert(tk.END, f"填写的信息存在语法错误: {e}，代码为: \n{pycode_str}")
            tab.controls['print_log'].configure(state='disabled')


    def save_code():
        current_tab = notebook.select()
        tab_index = notebook.index(current_tab)
        tab = tabs[tab_index]
        pycode_str = compile_code()
        pycode_str = pycode_str.replace(r"#the_plt.show()",r"the_plt.show()")
        pycode_str = pycode_str.replace(r"lambda", r"lamda")
        pycode_str = pycode_str.replace(r"\lamda", r"\lambda")
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".pyw",
                                                     filetypes=[("Double-click Python", "*.pyw"), ("Python Files", "*.py"), ("Text Files", "*.txt")])
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(pycode_str)
                messagebox.showinfo("保存代码", f"代码已保存到：{file_path}")
        except Exception as e:
            tab.controls['print_log'].configure(state='normal')
            tab.controls['print_log'].delete("1.0", tk.END)
            tab.controls['print_log'].configure(foreground='red')
            tab.controls['print_log'].insert(tk.END, f"填写的信息存在语法错误: {e}，代码为: \n{pycode_str}")
            tab.controls['print_log'].configure(state='disabled')

    # 启动主循环
    root.mainloop()


if __name__ == '__main__':
    makefig()