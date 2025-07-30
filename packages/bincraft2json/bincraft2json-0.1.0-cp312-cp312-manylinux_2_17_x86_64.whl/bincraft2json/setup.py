from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import setuptools
from wheel.bdist_wheel import bdist_wheel

class BuildExt(build_ext):
    def build_extensions(self):
        # Détecter le compilateur
        compiler = self.compiler.compiler_type
        if compiler == 'msvc':
            raise RuntimeError("Ce module n'est supporté que sous Linux")
        else:
            opts = ['-std=c++17', '-fvisibility=hidden']
            for ext in self.extensions:
                ext.extra_compile_args = opts
        build_ext.build_extensions(self)

class get_pybind_include(object):
    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)

class BdistWheel(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()
        if plat.startswith('linux'):
            plat = 'manylinux_2_17_x86_64'
        return python, abi, plat

ext_modules = [
    Extension(
        "bincraft2json",
        ["bincraft2json.cpp"],
        include_dirs=[
            get_pybind_include(),
            get_pybind_include(user=True),
            os.path.dirname(os.path.abspath(__file__))
        ],
        libraries=['zstd'],
        language='c++'
    ),
]

# Lire le contenu du README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bincraft2json",
    version="0.1.0",
    author="Aymene69",
    author_email="belmegaming@gmail.com",
    description="Module Python to convert BinCraft files to JSON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aymene69/bincraft2json",
    packages=["bincraft2json"],
    package_dir={"bincraft2json": "."},
    ext_modules=ext_modules,
    cmdclass={
        "build_ext": BuildExt,
        "bdist_wheel": BdistWheel
    },
    install_requires=['pybind11>=2.6.0'],
    setup_requires=['pybind11>=2.6.0'],
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    zip_safe=False,
    package_data={
        "bincraft2json": ["*.hpp", "*.cpp"],
    },
) 