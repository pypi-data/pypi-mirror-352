# CyEulerBallistic
LGPL library for small arms ballistic calculations based on point-mass (3 DoF) plus spin drift.
The fork of py_ballisticcalc.exts that can be used as side-package

[![license]][LGPL-3]
[![pypi]][PyPiUrl]
[![downloads]][pepy]
[![downloads/month]][pepy]
[![versions]][sources]
[![Made in Ukraine]][SWUBadge]

[![Python cythonized package tests (uv)](https://github.com/o-murphy/CyEulerBallistic/actions/workflows/pytest.yml/badge.svg)](https://github.com/o-murphy/CyEulerBallistic/actions/workflows/pytest.yml)

[sources]:
https://github.com/o-murphy/CyEulerBallistic
[license]:
https://img.shields.io/github/license/o-murphy/CyEulerBallistic?style=flat-square
[LGPL-3]:
https://opensource.org/licenses/LGPL-3.0-only
[pypi]:
https://img.shields.io/pypi/v/CyEulerBallistic?style=flat-square&logo=pypi
[PyPiUrl]:
https://pypi.org/project/CyEulerBallistic/
[coverage]:
coverage.svg
[downloads]:
https://img.shields.io/pepy/dt/CyEulerBallistic?style=flat-square
[downloads/month]:
https://static.pepy.tech/personalized-badge/CyEulerBallistic?style=flat-square&period=month&units=abbreviation&left_color=grey&right_color=blue&left_text=downloads%2Fmonth
[pepy]:
https://pepy.tech/project/CyEulerBallistic
[versions]:
https://img.shields.io/pypi/pyversions/CyEulerBallistic?style=flat-square
[Made in Ukraine]:
https://img.shields.io/badge/made_in-Ukraine-ffd700.svg?labelColor=0057b7&style=flat-square
[SWUBadge]:
https://stand-with-ukraine.pp.ua

### Table of contents
* **[Installation](#installation)**
  * [Latest stable](#latest-stable-release-from-pypi)

* **[Usage](#usage)**

* **[Contributors](#contributors)**
* **[About project](#about-project)**

# Installation

```shell
pip install CyEulerBallistic
# or 
uv add CyEulerBallistic
```

# Usage
Initialize CyEulerBallistic engine
```shell
from py_ballisticcalc import Calculator
calc = Calculator(_engine="CyEulerBallistic")
```
**Follow [Original README](Example.ipynb) for detailed illustrations of all features and usage.**


# About project

The library provides trajectory calculation for ballistic projectiles including air rifles, bows, firearms, artillery, and so on.

The 3DoF model that is used in this calculator is rooted in public C code of [JBM's calculator](https://jbmballistics.com/ballistics/calculators/calculators.shtml), ported to C#, optimized, fixed and extended with elements described in Litz's _Applied Ballistics_ book and from the friendly project of Alexandre Trofimov and then ported to Go.

This Python3 implementation has been expanded to support multiple ballistic coefficients and custom drag functions, such as those derived from Doppler radar data.

**[The online version of Go documentation is located here](https://godoc.org/github.com/gehtsoft-usa/go_ballisticcalc)**.

**[C# version of the package is located here](https://github.com/gehtsoft-usa/BallisticCalculator1), and [the online version of C# API documentation is located here](https://gehtsoft-usa.github.io/BallisticCalculator/web-content.html)**.

## Contributors
**This project exists thanks to all the people who contribute.**

<a href="https://github.com/o-murphy/py_ballisticcalc/graphs/contributors"><img height=32 src="https://contrib.rocks/image?repo=o-murphy/py_ballisticcalc" /></a>

Special thanks to:
- **[David Bookstaber](https://github.com/dbookstaber)** - Ballistics Expert\
*For help understanding and improving the functionality*
- **[Nikolay Gekht](https://github.com/nikolaygekht)** \
*For the sources code on C# and GO-lang from which this project firstly was forked*

[//]: # (## Sister projects)

[//]: # ()
[//]: # (* **Py-BalCalc** - GUI App for [py_ballisticcalc]&#40;https://github.com/o-murphy/py_ballisticcalc&#41; solver library and profiles editor)

[//]: # (* **eBallistica** - Kivy based mobile App for ballistic calculations)

[//]: # ()
[//]: # (* <img align="center" height=32 src="https://github.com/JAremko/ArcherBC2/blob/main/resources/skins/sol-dark/icons/icon-frame.png?raw=true" /> [ArcherBC2]&#40;https://github.com/JAremko/ArcherBC2&#41; and [ArcherBC2 mobile]&#40;https://github.com/ApodemusSylvaticus/archerBC2_mobile&#41; - Ballistic profile editors)

[//]: # (  - *See also [a7p_transfer_example]&#40;https://github.com/JAremko/a7p_transfer_example&#41; or [a7p]&#40;https://github.com/o-murphy/a7p&#41; repo to get info about the ballistic profile format*)

## RISK NOTICE

The library performs very limited simulation of a complex physical process and so it performs a lot of approximations. Therefore, the calculation results MUST NOT be considered as completely and reliably reflecting actual behavior or characteristics of projectiles. While these results may be used for educational purpose, they must NOT be considered as reliable for the areas where incorrect calculation may cause making a wrong decision, financial harm, or can put a human life at risk.

THE CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.
