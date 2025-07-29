from setuptools import setup, Extension, find_packages
import pybind11

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

ext_modules = [
    Extension(
        "shansort",                     # module name without .cpp
        sources=["shansort.cpp"],      # your C++ source file
        include_dirs=[pybind11.get_include()],
        language="c++"
    ),
]

setup(
    name='shansort',
    version='0.1.2',
    author='Bhavani Shanker',
    author_email='bhavanishanker9@proton.me',
    description='Unified fast radix sort for int, float, and string',
    long_description=long_description,
    long_description_content_type='text/markdown',
    ext_modules=ext_modules,
    install_requires=['pybind11>=2.6.0'],
    setup_requires=['pybind11>=2.6.0', 'wheel'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: C++',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
