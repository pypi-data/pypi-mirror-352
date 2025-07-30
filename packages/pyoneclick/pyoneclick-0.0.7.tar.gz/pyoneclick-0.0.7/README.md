
# pyoneclick

This Python tool can automatically screen control variables to adjust the significance of specific variables, similar to Stata's `oneclick` command but with more powerful features.

- 中文：[README_zh.md](https://github.com/zpjbtdjm/pyoneclick/blob/master/README_zh.md)

## Introduction

### Insights

The development of this research is based on the following insights:

1. A trade-off between time and optimal solutions needs to be made. During the process of filtering control variables, when there are too many control variables, finding the optimal solution becomes time-consuming and unacceptable. In many cases, we only need a quick result that works, that is, an approximate optimal solution rather than all possible usable results.

2. Addressing the issue of "solve one problem only to find another cropping up." Oftentimes, when a variable becomes significant in a specific command, another variable or the same variable in another command may no longer be significant. Therefore, the command used for screening must address such issues where simultaneous significance is required.

### Command Features

Compared to the `oneclick` command in Stata, this command incorporates several new features. It has the following characteristics:

1. More efficient filtering. This command is based on the simulated annealing algorithm rather than enumeration, resulting in lower time complexity during the search for usable control variables.

2. Clearer logic. The original Stata code can be directly passed into the command during execution, without needing to change coding habits, making the command more readable.

3. Broader functionality. Supports joint estimation across multiple commands and adjusts the significance of multiple variables or multiple commands at the same time.

## Usage

### Requirements

Before formal use, we need to meet the following conditions:

1. Licensed Stata software. The version must be Stata 17 or above.

2. An appropriate Python 3 environment. Python 3.8 or higher is recommended.

### Installation

1. First, set a global system variable named `STATA_PATH` in the Windows Control Panel. The value of the variable should be the installation path of Stata plus the version number. For example, for the MP version of Stata 18 on a 64-bit computer, the default installation path would look like this:
```
STATA_PATH=C:\Program Files\Stata18\StataMP-64.exe
```

2. Install the `pyoneclick` command:
```shell
pip install pyoneclick
```

### Getting Started

The functionality of the `pyoneclick` command is relatively complex, and mastering it fully may take some time.
- We provide detailed instructions to help users get started quickly: [View detailed usage instructions](https://github.com/zpjbtdjm/pyoneclick/blob/master/docs/USAGE.md)

## Acknowledgments

The development of this project was inspired by the [StataOneClick](https://github.com/ShutterZor/StataOneClick) project, and we sincerely thank the author of that project. Their excellent work provided valuable insights and became a crucial foundation for our project’s development.

## Third-Party Libraries

This project uses the following open-source libraries:
- [stata-setup](https://pypi.org/project/stata-setup/): Licensed under [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

