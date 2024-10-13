import os
import concurrent.futures
import subprocess
import hashlib
import shlex
import re

# Paths to directories
STRATEGY_PATH = "/home/minisage/Documents/freqtrade/user_data/strategies"
CONFIG_PATH = "/home/minisage/Documents/freqtrade/user_data/configs"
RESULTS_PATH = "/home/minisage/Documents/freqtrade/user_data/results"

# Available values for timeframe, timerange, spaces, and loss_functions
TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "8h", "1d"]
TIMERANGES = [
    "20240601-20240825", "20240701-20240825", "20240601-",
    "20240810-20240825", "20240820-20240825",
    "20240824-20240825", "20240725-20240825"
]
SPACES = [
    "roi stoploss", "roi stoploss trailing", "buy sell",
    "buy sell roi", "buy sell roi stoploss", "stoploss roi",
    "roi", "buy", "sell", "all"
]
LOSS_FUNCTIONS = [
    "ShortTradeDurHyperOptLoss", "OnlyProfitHyperOptLoss",
    "SharpeHyperOptLoss", "SortinoHyperOptLoss"
]

def get_choice(options, prompt, allow_custom=True):
    """
    Function for user to select an option or enter a custom value.
    """
    print(prompt)
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")
    if allow_custom:
        print(f"{len(options) + 1}. Enter your own value")

    while True:
        choice = input("Enter the number or your own value: ").strip()

        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(options):
                return options[index]
            elif allow_custom and index == len(options):
                return input("Enter your own value: ").strip()
            else:
                print("Invalid choice, please try again.")
        else:
            if allow_custom:
                return choice
            else:
                print("Invalid input, please try again.")

def form_download_data_command(timeframe, timerange):
    # Form the command for downloading data
    return (
        f"freqtrade download-data --config "
        f"{os.path.join(CONFIG_PATH, config_file_name)} "
        f"--timeframe {timeframe} --timerange {timerange}"
    )

def form_backtesting_command(strategy, timeframe, timerange):
    # Form the command for backtesting
    return (
        f"freqtrade backtesting --strategy {strategy} "
        f"--config {os.path.join(CONFIG_PATH, config_file_name)} "
        f"--timerange {timerange} --timeframe {timeframe}"
    )

def form_plot_profit_command(strategy, timeframe, pairs, timerange):
    # Form the command for plotting profit
    return (
        f"freqtrade plot-profit --strategy {strategy} "
        f"--config {os.path.join(CONFIG_PATH, config_file_name)} "
        f"--timeframe {timeframe} --pairs {pairs} "
        f"--timerange {timerange}"
    )

def form_hyperopt_command(strategy, loss_function, spaces,
                          timeframe, timerange, epochs):
    # Form the command for hyperopt
    return (
        f"freqtrade hyperopt --strategy {strategy} "
        f"--hyperopt-loss {loss_function} --spaces {spaces} "
        f"--timerange {timerange} -e {epochs} "
        f"--config {os.path.join(CONFIG_PATH, config_file_name)} "
        f"--timeframe {timeframe}"
    )

def shorten_filename(filename, max_length=180):
    # Split the filename into name and extension
    filename_without_extension, extension = os.path.splitext(filename)
    if len(filename_without_extension) > max_length:
        # Shorten the name, keeping a hash for uniqueness
        hash_digest = hashlib.sha256(
            filename_without_extension.encode()
        ).hexdigest()[:8]
        allowed_length = (max_length - len(extension) -
                          len(hash_digest) - 1)
        filename_without_extension = (
            f"{filename_without_extension[:allowed_length]}"
            f"_{hash_digest}"
        )
    return f"{filename_without_extension}{extension}"

def save_command_result(command_result, command_name,
                        tested_file_name, command):
    # Create a safe filename from the command
    safe_command = re.sub(r'[^\w\-_\. ]', '_', command)
    original_filename = (
        f"{command_name}_{tested_file_name}_{safe_command}"
    )
    
    # Apply the filename shortening function
    filename = shorten_filename(original_filename)
    save_path = os.path.join(RESULTS_PATH, filename)
    
    try:
        with open(save_path, 'w', encoding='utf-8') as file:
            file.write(command_result)
        print(f"Result saved to file: {save_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

def form_trade_command(strategy):
    # Form the command for trading
    return (
        f"freqtrade trade --strategy {strategy} "
        f"--config {os.path.join(CONFIG_PATH, config_file_name)}"
    )

def run_command(command):
    print(f"Executing command: {command}")
    try:
        process = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        command_output, _ = process.communicate()
        print(command_output)
        
        args = shlex.split(command)
        if '--strategy' in args:
            strategy_index = args.index('--strategy') + 1
            strategy_name = args[strategy_index]
        else:
            strategy_name = 'general'
        
        return command_output, strategy_name
    except Exception as e:
        print(f"Error executing command '{command}': {e}")
        return "", "general"

# Get a list of strategy files
files = sorted([
    f for f in os.listdir(STRATEGY_PATH)
    if os.path.isfile(os.path.join(STRATEGY_PATH, f))
    and f.endswith('.py')
])

# Choose the function to run
function_choice = get_choice(
    ["Test Strategies", "Download Data",
     "Hyperopt", "Trade", "Plot"],
    "Select the function to run:"
)

# Get a list of configuration files
config_files = sorted([
    f for f in os.listdir(CONFIG_PATH)
    if os.path.isfile(os.path.join(CONFIG_PATH, f))
    and f.endswith('.json')
])

# Ask the user for the configuration file name
config_file_name = get_choice(
    config_files, "Select the configuration file:"
)

if function_choice == "Test Strategies":
    # Choose testing option
    test_option = get_choice(
        ["Test All Strategies",
         "Test Selected Strategy"],
        "Select an option:"
    )
    if test_option == "Test Selected Strategy":
        file_name_with_extension = get_choice(
            files, "Select a file:"
        )
        strategy_name = os.path.splitext(
            file_name_with_extension
        )[0]  # Remove .py extension
        timeframe_choice = get_choice(
            TIMEFRAMES, "Select timeframe:"
        )
        timerange_choice = get_choice(
            TIMERANGES, "Select timerange:"
        )

    elif test_option == "Test All Strategies":
        timeframe_choice = get_choice(
            TIMEFRAMES, "Select timeframe:"
        )
        timerange_choice = get_choice(
            TIMERANGES, "Select timerange:"
        )

elif function_choice == "Hyperopt":
    # Choose hyperopt option
    hyperopt_option = get_choice(
        ["Optimize All Strategies",
         "Optimize Selected Strategy"],
        "Select an option:"
    )
    if hyperopt_option == "Optimize Selected Strategy":
        file_name_with_extension = get_choice(
            files, "Select a file:"
        )
        strategy_name = os.path.splitext(
            file_name_with_extension
        )[0]  # Remove .py extension
        hyperopt_loss = get_choice(
            LOSS_FUNCTIONS, "Select loss function:"
        )
        spaces = get_choice(
            SPACES, "Select spaces:"
        )
        while True:
            epochs = input("Enter the number of epochs: ")
            if epochs.isdigit():
                break
            else:
                print("Please enter a numeric value.")
        
        timeframe_choice = get_choice(
            TIMEFRAMES, "Select timeframe:"
        )
        timerange_choice = get_choice(
            TIMERANGES, "Select timerange:"
        )
    
    elif hyperopt_option == "Optimize All Strategies":
        hyperopt_loss = get_choice(
            LOSS_FUNCTIONS, "Select loss function:"
        )
        spaces = get_choice(
            SPACES, "Select spaces:"
        )
        timeframe_choice = get_choice(
            TIMEFRAMES, "Select timeframe:"
        )
        timerange_choice = get_choice(
            TIMERANGES, "Select timerange:"
        )
        while True:
            epochs = input("Enter the number of epochs: ")
            if epochs.isdigit():
                break
            else:
                print("Please enter a numeric value.")

# Strategy files already filtered
strategy_files = files

# Form commands
commands = []

if function_choice == "Test Strategies":
    if test_option == "Test All Strategies":
        # Generate commands for all strategies
        commands = [
            form_backtesting_command(
                os.path.splitext(strategy_file)[0],
                timeframe_choice, timerange_choice
            )
            for strategy_file in strategy_files
        ]

        # Use ThreadPoolExecutor for parallel execution
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=4
        ) as executor:
            future_to_command = {
                executor.submit(
                    run_command, cmd
                ): cmd for cmd in commands
            }
            for future in concurrent.futures.as_completed(
                future_to_command
            ):
                cmd = future_to_command[future]
                try:
                    # Set a timeout for each command
                    command_output, strategy_name = future.result(
                        timeout=300  # 5-minute timeout
                    )
                    # Save command results to file
                    save_command_result(
                        command_output, "Test Strategies",
                        strategy_name, cmd
                    )
                    print(f"Command completed: {cmd}")
                except concurrent.futures.TimeoutError:
                    print(
                        f"Command exceeded time limit (5 minutes) "
                        f"and was skipped: {cmd}"
                    )
                except Exception as exc:
                    print(
                        f"Command generated an exception: {exc}. "
                        f"Command: {cmd}"
                    )

    elif test_option == "Test Selected Strategy":
        command = form_backtesting_command(
            strategy_name, timeframe_choice, timerange_choice
        )
        commands.append(command)

elif function_choice == "Download Data":
    timeframe_choice = get_choice(
        TIMEFRAMES + ["1m 5m 15m 30m 1h 4h 8h 1d",
                      "30m 1h 4h 8h 1d", "1m 5m 15m"],
        "Select timeframe:"
    )
    timerange_choice = get_choice(
        TIMERANGES, "Select timerange:"
    )
    command = form_download_data_command(
        timeframe_choice, timerange_choice
    )
    
    # Execute the command outside of thread pool
    command_output, _ = run_command(command)
    save_command_result(
        command_output, "Download Data", "general", command
    )

elif function_choice == "Trade":
    # Choose the strategy for trading
    strategy_file = get_choice(
        strategy_files, "Select strategy:"
    )
    strategy_name = os.path.splitext(
        strategy_file
    )[0]  # Get filename without extension

    command = form_trade_command(strategy_name)
    commands.append(command)
    
elif function_choice == "Hyperopt":
    if hyperopt_option == "Optimize All Strategies":
        for strategy_file in strategy_files:
            strategy_name = os.path.splitext(
                strategy_file
            )[0]  # Get filename without extension

            command = form_hyperopt_command(
                strategy_name, hyperopt_loss, spaces,
                timeframe_choice, timerange_choice, epochs
            )
            commands.append(command)
    elif hyperopt_option == "Optimize Selected Strategy":
        command = form_hyperopt_command(
            strategy_name, hyperopt_loss, spaces,
            timeframe_choice, timerange_choice, epochs
        )
        commands.append(command)

elif function_choice == "Plot":
    strategy_file = get_choice(
        strategy_files, "Select strategy:"
    )
    strategy_name = os.path.splitext(
        strategy_file
    )[0]  # Get filename without extension
    timeframe_choice = get_choice(
        TIMEFRAMES, "Select timeframe:"
    )
    pairs = input(
        "Enter the currency pair (e.g., LTC/USDT): "
    ).strip()
    timerange_choice = get_choice(
        TIMERANGES, "Select timerange:"
    )
    command = form_plot_profit_command(
        strategy_name, timeframe_choice, pairs, timerange_choice
    )
    commands.append(command)

# Execute commands
for cmd in commands:
    print(f"Executing command: {cmd}")
    try:
        process = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        command_output, _ = process.communicate()
        print(command_output)
        
        args = shlex.split(cmd)
        if '--strategy' in args:
            strategy_index = args.index('--strategy') + 1
            strategy_name = args[strategy_index]
        else:
            strategy_name = 'general'
        
        save_command_result(
            command_output, function_choice, strategy_name, cmd
        )
        print(f"Command completed: {cmd}")
    except Exception as e:
        print(f"Error executing command '{cmd}': {e}")

# Application finished
