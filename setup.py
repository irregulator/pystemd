#!/usr/bin/env python3
#
# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the LICENSE file in
# the root directory of this source tree.
#


import ast
import atexit
import glob
import os
import sys
import time
from pathlib import Path

from setuptools import setup
from setuptools.extension import Extension


THIS_DIR = Path(__file__).parent

with (THIS_DIR / "README.md").open() as f:
    long_description = f.read()

# get and compute the version string
version_file = THIS_DIR / "pystemd" / "__version__.py"
release_file = THIS_DIR / "pystemd" / "RELEASE"

with version_file.open() as f:
    parsed_file = ast.parse(f.read())

__version__ = [
    expr.value.s
    for expr in parsed_file.body
    if isinstance(expr, ast.Assign)
    and isinstance(expr.targets[0], ast.Name)
    and isinstance(expr.value, ast.Str)
    and expr.targets[0].id == "__version__"
][0]

release_tag = "{}".format(int(time.time()))


if release_file.exists():
    __version__ += ".0"
elif "sdist" in sys.argv:
    with release_file.open("w") as f:
        atexit.register(lambda *x: f.unlink())
        f.write(release_tag)
    __version__ += ".0"
else:
    __version__ += ".{}".format(release_tag)


# Make sure Cython modules are compiled to C code if .c files are not present.
# This is the case when using a clone of the git repository, unlike the
# source distribution which includes both .pyx and .c files.
USE_CYTHON = not bool(glob.glob("pystemd/*.c"))
ext = ".pyx" if USE_CYTHON else ".c"
external_modules = [Extension("*", ["pystemd/*" + ext], libraries=["systemd"])]

if USE_CYTHON:
    try:
        from Cython.Build import cythonize

        external_modules = cythonize(external_modules)
    except ImportError:
        raise RuntimeError("Cython not installed.")

setup(
    name="pystemd",
    version=__version__,
    packages=["pystemd", "pystemd.systemd1", "pystemd.machine1", "pystemd.DBus"],
    author="Alvaro Leiva",
    author_email="aleivag@fb.com",
    ext_modules=external_modules,
    url="https://github.com/facebookincubator/pystemd",
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
    ],
    keywords=["systemd"],
    description="A systemd binding for python",
    package_data={"pystemd": ["RELEASE"]},
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="LGPL-2.1+",
)
