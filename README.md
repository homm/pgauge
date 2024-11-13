# PGauge

PGauge is a command-line utility for macOS that parses power metrics from
the `powermetrics` command and displays them in a user-friendly format.
It provides real-time CPU and GPU power usage statistics,
helping you monitor your system's performance efficiently.


## Features

* **Real-time monitoring**: Shows up-to-date statistics on CPU and GPU power usage.
* **Summary Statistics**: Shows minimum and maximum values over a specified period.
* **History Keeping**: Provides an option to keep a history of all updates.
* **Automatic Terminal Resizing**: Adjusts the terminal window size for optimal display.

## Requirements

* **Operating System**: macOS (Apple Silicon only)
* **Permissions**: Administrator privileges (requires admin password)
* **Python Version**: Python 3.8 or higher

## Installation

Install PGauge using pip:

    pip install pgauge

## Usage

    pgauge [-h] [-i mS] [-s S] [-k] [-r WxH]

Alternatively, you can run PGauge as a Python module:

    python -m pgauge [-h] [-i mS] [-s S] [-k] [-r WxH]

### Optional Arguments

- `-h`, `--help`  
    Show the help message and exit.
    
- `-i mS`, `--interval mS`  
    Set the stats update interval in milliseconds. Default is `1000` (one second).
    
- `-s S`, `--summary S`  
    Display the minimum and maximum values for a period in seconds. Set to `0` to disable history. Default is `60` (one minute).
    
- `-k`, `--keep-history`  
    Print each update on a new line instead of refreshing the current line.
    
- `-r WxH`, `--resize WxH`  
    Resize the terminal window to the specified width and height (`WxH`). You can also set it to `auto` for automatic resizing.

### Examples

- **Run with Default Settings**

      pgauge
    
- **Set Update Interval to 500ms**
    
      pgauge -i 500
    
- **Disable Summary History**

      pgauge -s 0
    
- **Keep History of All Updates**

      pgauge -k
    
- **Automatically Resize Terminal Window**
    
      pgauge -r auto

## Important Notes

* **Administrator Privileges Required**: PGauge uses the `powermetrics` command,
  which requires administrator privileges. You will be prompted for your admin password
  when running `pgauge`. You can grant privileges for the current user
  to run `powermetrics` without a password by running the following command:

      echo `whoami` "ALL=(ALL) NOPASSWD: /usr/bin/powermetrics *" | sudo tee /etc/sudoers.d/powermetrics

* **macOS Only**: This utility is designed to work exclusively on macOS systems with Apple architecture.
