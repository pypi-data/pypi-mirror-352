# StockSim

**Monte Carlo Stock & Crypto Price Simulation Tool**

StockSim is a Python command-line tool for estimating the probability of gain for stocks, cryptocurrencies, or indices using Monte Carlo simulation and real historical data.

---

## Features

- Simulate future price paths for stocks, crypto, or indices
- Uses real historical data via [yfinance](https://github.com/ranaroussi/yfinance)
- Multiprocessing for fast simulations
- Command-line interface
- Logging to file and console

---

## Requirements

- Python 3.7–3.12 (not compatible with Python 3.13)
- See `requirements.txt` for required packages

---

## Installation

### From PyPI (recommended)

```sh
pip install stocksim
```

### From source

```sh
git clone https://github.com/ElementalPublishing/StockSim.git
cd StockSim
pip install -e .
```

---

## Usage

After installation, run from the command line:

```sh
stocksim [options]
```

Or, if running from source:

```sh
python -m stocksim.main [options]
```

---

## Build Windows Executable (Optional)

To build a Windows executable with your custom icon:

```sh
pyinstaller --icon=shaggy.ico --name=StockSim stocksim/main.py
```

- The EXE will be in the `dist` folder as `StockSim.exe`.

---

## Notes

- Compatible with Python 3.7–3.12, PyInstaller 5.13.2, and setuptools <80 (tested with 79.0.1).
- Log files are saved in the `logs` folder, with a new file for each run.
- For issues or feature requests, please use the [GitHub Issue Tracker](https://github.com/ElementalPublishing/StockSim/issues).

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.