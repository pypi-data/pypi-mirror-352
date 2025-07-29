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
stocksim
```

Or, if running from source:

```sh
python -m stocksim.main
```

---

## Command-Line Options

You can run StockSim with the following options:

- `--symbol`  
  Ticker symbol (e.g., `BTC-USD`, `ETH-USD`, `AAPL`, `SPX:IND`, `EURUSD:CUR`)

- `--years`  
  Investment period in years (e.g., `1`)

- `--simsize`  
  Simulation size: `small`, `medium`, or `large`

**Examples:**

```sh
stocksim --symbol BTC-USD --years 5 --simsize large
stocksim --symbol AAPL --years 3 --simsize medium
```

If you omit any option, the program will prompt you for input interactively.

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
- **Note:** Logging to files has been removed due to compatibility issues. All output is now printed to the console.
- For issues or feature requests, please use the [GitHub Issue Tracker](https://github.com/ElementalPublishing/StockSim/issues).

> **Note:**  
> If you get a `'stocksim' is not recognized as an internal or external command` error, you may need to add your Python Scripts directory to your system PATH.
>
> For a typical Python installation on Windows, add:
> ```
> C:\Users\<YourUser>\AppData\Local\Programs\Python\<Your Python Version>\Scripts
> ```
> (Replace `<YourUser>` with your actual username and `<Your Python Version>` with your installed Python version, e.g., `Python312`.)
>
> After updating your PATH, restart your terminal or Command Prompt and try running `stocksim` again.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.