
# Freqtrade Text User Interface

This script automates various tasks related to Freqtrade, a cryptocurrency trading platform. It provides an interactive command-line interface to perform actions such as testing strategies, downloading data, hyperparameter optimization, trading, and plotting profit graphs.

## Features

- **Test Strategies**: Backtest one or all strategies over specified timeframes and timeranges.
- **Download Data**: Download historical market data for specified timeframes and timeranges.
- **Hyperopt**: Optimize hyperparameters for one or all strategies using different loss functions and parameter spaces.
- **Trade**: Run live or dry-run trading sessions with selected strategies.
- **Plot**: Generate profit graphs for strategies over specified pairs and timeranges.

## Prerequisites

- Python 3.x
- Freqtrade installed and configured.

Required Python packages:
- `os`
- `concurrent.futures`
- `subprocess`
- `hashlib`
- `shlex`
- `re`

## Setup

1. Clone or download the script and place it in your desired directory.
2. Update the directory paths at the beginning of the script to match your Freqtrade setup:

   ```python
   STRATEGY_PATH = "/path/to/your/freqtrade/user_data/strategies"
   CONFIG_PATH = "/path/to/your/freqtrade/user_data/configs"
   RESULTS_PATH = "/path/to/your/freqtrade/user_data/results"
   ```

3. Ensure that your strategies are placed in the `strategies` directory and your configuration files are in the `configs` directory.

Run the script using:

```bash
python freqtrade_tui.py
```

The script will prompt you to select an action:

- Test Strategies
- Download Data
- Hyperopt
- Trade
- Plot

### Test Strategies

- Choose to test all strategies or a selected strategy.
- Select the timeframe and timerange for backtesting.
- Results will be saved in the `results` directory.

### Download Data

- Select the timeframe(s) and timerange for which you want to download data.
- The script will execute the `freqtrade download-data` command accordingly.

### Hyperopt

- Choose to optimize all strategies or a selected strategy.
- Select the loss function, parameter spaces, number of epochs, timeframe, and timerange.
- The script will run hyperparameter optimization using Freqtrade's `hyperopt` feature.

### Trade

- Select the strategy you want to use for trading.
- The script will execute the `freqtrade trade` command with the selected strategy.

### Plot

- Select the strategy, timeframe, currency pair, and timerange.
- The script will generate a profit plot using the `freqtrade plot-profit` command.

## Results

Outputs and logs from the commands are saved in the `results` directory. Filenames are generated based on the action, strategy name, and command executed. Long filenames are shortened while ensuring uniqueness using a hash.

## Customization

- **Timeframes, Timeranges, Spaces, and Loss Functions**: You can customize the available options by modifying the respective lists at the beginning of the script.

   ```python
   TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "8h", "1d"]
   TIMERANGES = ["20200101-", "20210101-20211231", ...]
   SPACES = ["roi stoploss", "buy sell", "all", ...]
   LOSS_FUNCTIONS = ["SharpeHyperOptLoss", "SortinoHyperOptLoss", ...]
   ```

- **Max Workers for ThreadPoolExecutor**: Adjust the number of workers for parallel execution in the testing phase by changing the `max_workers` parameter.

   ```python
   with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
   ```

## Error Handling

- The script includes error handling for subprocess execution and file operations.
- Timeouts are set for long-running commands during parallel execution.
- Invalid inputs are handled with prompts to the user for correction.

## Notes

- Ensure Freqtrade is properly configured and all dependencies are met.
- Be cautious when running live trades; always test in dry-run mode first.
- Backtesting and hyperopt can be resource-intensive; adjust parameters accordingly.

## License

This script is provided "as is" without any warranty. Use it at your own risk.
