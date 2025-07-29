# deltacalc

- HomePage: https://github.com/kzhu2099/Delta-Calculus
- Issues: https://github.com/kzhu2099/Delta-Calculus/issues

[![PyPI Downloads](https://static.pepy.tech/badge/deltacalc)](https://pepy.tech/projects/deltacalc)

Author: Kevin Zhu

## Features

- seed setting
- both integrals and derivatives
- image making from latex
- built in trainer
- random problems that are difficult

## Installation

To install deltacalc, use pip: ```pip install deltacalc```.

However, many prefer to use a virtual environment.

macOS / Linux:

```sh
# make your desired directory
mkdir /path/to/your/directory
cd /path/to/your/directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install deltacalc
source .venv/bin/activate
pip install deltacalc

deactivate # when you are completely done
```

Windows CMD:

```sh
# make your desired directory
mkdir C:path\to\your\directory
cd C:path\to\your\directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install deltacalc
.venv\Scripts\activate
pip install deltacalc

deactivate # when you are completely done
```

## Usage

This class aims to provide challenging problems of calculus quickly.

Simply use `RandomDerivative` or `RandomIntegral` to generate a problem and check your work using `check()`. Or, use the Trainer class to easily train yourself with a certain amount of problems.

Set your seed manually to get repeatable problems, using the set_seed method.
Warning: these problems get REALLY messy!!

## License

The License is an MIT License found in the LICENSE file.