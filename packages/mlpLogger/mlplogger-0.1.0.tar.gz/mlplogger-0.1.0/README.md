
# mlpLogger

**mlpLogger** is a Python package designed to simplify structured logging for your applications. It provides easy-to-use methods to create daily log files, manage log handlers, and include structured metadata in your logs.

---

## 📦 Installation

Install the latest version from [PyPI](https://pypi.org/project/mlpLogger/) using:

```bash
pip install mlpLogger
```

---

## 🚀 Usage

Here’s a quick example of how to use `mlpLogger` in your project:

```python
from mlpLogger import MLPLogger

# Initialize the logger
logger = MLPLogger()

# Print the current log file name
print(f"Current log file: {logger.logfilename}")

# Log a simple info message
logger.logger.info("This is a simple info log message.")

# Change the log file name dynamically
logger.logfilename = "custom_mlpLogger.log"
print(f"Updated log file: {logger.logfilename}")

# Log a message to the new file
logger.logger.info("This is a log message in the new file.")

# Log a structured 'success' outcome
log_extras = logger.logSuccess({})
print(f"Logged success with extras: {log_extras}")
```

---

## 🛠️ Features

✅ **Automatic Daily Log Files**  
✅ **Structured Logging with ECS Formatter**  
✅ **Dynamic Log File Switching**  
✅ **Helper Methods for Structured Logging (e.g., `logSuccess`)**  
✅ **Fully Configurable for Use in Any Project**

---

## 🔧 Methods

- **`MLPLogger.logfilename`**  
  - *Getter*: Prints and returns the current log filename.  
  - *Setter*: Dynamically updates the log file and reconfigures the logger.

- **`MLPLogger.logSuccess(logExtrasIn)`**  
  - Logs a structured “success” message and returns the updated dictionary of log extras.

- **`MLPLogger.createDailyLogfileName(logfile)`**  
  - Creates a daily log filename based on UTC date.

- **`MLPLogger.createScriptRunID(scriptname)`**  
  - Generates a unique ID for script runs.

---

## 📂 Project Structure

```
mlpLogger/
├── mlpLogger/          # Main package module
│   ├── __init__.py
│   └── mlpLogger.py
├── tests/              # Unit tests
├── LICENSE
├── README.md
├── setup.py
├── pyproject.toml
└── example_usage.py    # Demonstration script
```

---

## ⚖️ License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Michael Baskaran**  
Email: [mbas@caasco.ca](mailto:mbas@caasco.ca)  

---

## 🙏 Contributing

Contributions are welcome! Please fork this repository and submit a pull request with your improvements.

---

**mlpLogger** — making structured logging simpler and more reliable for your Python applications!
