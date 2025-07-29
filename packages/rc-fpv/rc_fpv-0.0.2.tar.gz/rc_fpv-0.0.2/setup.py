#!/usr/bin/env python
"""rc-fpv extension builder and installer"""

import io
import sys

import setuptools

name = "rc-fpv"
desc = "A library to control Drone that is normally controled by the 'RC FPV' android app"

with io.open("README.md", encoding="utf-8") as strm:
    long_desc = strm.read()

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: Freely Distributable",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: Implementation",
    "Programming Language :: Python :: Implementation :: CPython",
]
author = "Mickael Roger"
author_email = "mickael@mickael-roger.com"
url = "https://github.com/Mickael-Roger/rc-fpv"
license = "Apache License Version 2.0"
packages = ["rc-fpv"]

needs_pytest = set(["pytest", "test"]).intersection(sys.argv)
pytest_runner = ["pytest_runner"] if needs_pytest else []

test_require = []
with io.open("requirements.txt") as f:
    test_require = [l.strip() for l in f if not l.startswith("#")]

install_require = []
with io.open("requirements.txt") as f:
    install_require = [l.strip() for l in f if not l.startswith("#")]

setup_params = dict(
    name=name,
    version="0.0.2",
    description=desc,
    long_description=long_desc,
    classifiers=classifiers,
    author=author,
    author_email=author_email,
    url=url,
    license=license,
    packages=packages,
    include_package_data=True,
    install_requires=install_require,
    tests_require=test_require,
    setup_requires=pytest_runner,
    python_requires=">=3.10",
)


def main():
    """Package installation entry point."""
    setuptools.setup(**setup_params)


if __name__ == "__main__":
    main()
