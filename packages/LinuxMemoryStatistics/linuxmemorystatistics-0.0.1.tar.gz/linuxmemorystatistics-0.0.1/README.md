![LinuxMemoryStatistics Logo](https://mauricelambert.github.io/info/python/code/LinuxMemoryStatistics_small.png "LinuxMemoryStatistics logo")

# LinuxMemoryStatistics

## Description

This script prints memory usages and statistics (by process,
executable and for the full system).

## Requirements

This package require:
 - python3
 - python3 Standard Library

## Installation

### Pip

```bash
python3 -m pip install LinuxMemoryStatistics
```

### Git

```bash
git clone "https://github.com/mauricelambert/LinuxMemoryStatistics.git"
cd "LinuxMemoryStatistics"
python3 -m pip install .
```

### Wget

```bash
wget https://github.com/mauricelambert/LinuxMemoryStatistics/archive/refs/heads/main.zip
unzip main.zip
cd LinuxMemoryStatistics-main
python3 -m pip install .
```

### cURL

```bash
curl -O https://github.com/mauricelambert/LinuxMemoryStatistics/archive/refs/heads/main.zip
unzip main.zip
cd LinuxMemoryStatistics-main
python3 -m pip install .
```

## Usages

### Command line

```bash
LinuxMemoryStatistics              # Using CLI package executable
python3 -m LinuxMemoryStatistics   # Using python module
python3 LinuxMemoryStatistics.pyz  # Using python executable
LinuxMemoryStatistics.exe          # Using python Windows executable
```

### Python script

```python
from LinuxMemoryStatistics import *
```

## Links

 - [Pypi](https://pypi.org/project/LinuxMemoryStatistics)
 - [Github](https://github.com/mauricelambert/LinuxMemoryStatistics)
 - [Documentation](https://mauricelambert.github.io/info/python/code/LinuxMemoryStatistics.html)
 - [Python executable](https://mauricelambert.github.io/info/python/code/LinuxMemoryStatistics.pyz)
 - [Python Windows executable](https://mauricelambert.github.io/info/python/code/LinuxMemoryStatistics.exe)

## License

Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).
