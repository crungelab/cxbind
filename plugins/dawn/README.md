# dawny

[![PyPI - Version](https://img.shields.io/pypi/v/dawny.svg)](https://pypi.org/project/dawny)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dawny.svg)](https://pypi.org/project/dawny)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install dawny
```

## License

`dawny` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Quick Start

    git clone --recursive https://github.com/kfields/dawny
    cd dawny
    mkdir build
    cd build
    cmake ..

## Debug Build

    mkdir build-debug
    cd build-debug
    cmake -DCMAKE_BUILD_TYPE=Debug ..
    # or
    cmake -G Ninja -DCMAKE_BUILD_TYPE=Debug ..
    # or
    cmake -G "Visual Studio 17 2022" -DCMAKE_BUILD_TYPE=Debug ..
