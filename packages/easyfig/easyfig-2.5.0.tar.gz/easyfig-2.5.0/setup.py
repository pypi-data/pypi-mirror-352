# setup.py

from setuptools import setup, find_packages
import os

setup(
    name='easyfig',
    version='2.5.0',
    author='Yu-Xin Tian',
    author_email='neu.tianyuxin.2013@gmail.com',  
    description='A simple simulation plotting tool with GUI. 适合科研人员的Python快速仿真绘图工具版本！A Python tool for researchers to create figures for academic papers!',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Jesse-tien/Easyfig',  
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "sympy",
        "matplotlib",
        "ipython",
        "notebook",
        "pyperclip",
        "qrcode"
    ],
    entry_points={
        'console_scripts': [
            'easyfig=easyfig.main:makefig',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
