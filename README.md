# CCTool
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/ffbe6b6e73b4483abe7ccbdab6a581bc?)](https://www.codacy.com/app/m-kus/cctool)
[![Maintainability](https://api.codeclimate.com/v1/badges/92508e368dde36b04087/maintainability)](https://codeclimate.com/github/m-kus/cctool/maintainability?)
[![Made With](https://img.shields.io/badge/made%20with-python-blue.svg?)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?)](https://opensource.org/licenses/MIT)

Import your trade history to the CryptoCompare.com, a portfolio tracking service.

## Supported exchanges

* Poloniex
* Bittrex

## Requirements

* git
* account on cryptocompare.com

## Installation

```
$ pip3 install git+https://github.com/m-kus/cctool --user
```

## Usage

### Export trades
#### Poloniex

1. Login into your Poloniex Account
2. Open the tab "ORDERS" -> "MY TRADE HISTORY & ANALYSIS" in the top navigation (https://www.poloniex.com/tradeHistory)
3. Click on "Export Complete Trade History" in the top right corner
4. Save the CSV file on your PC

#### Bittrex

1. Login into your Bittrex Account
2. Open "Orders" over the top navigation (https://bittrex.com/History)
3. Click on the "Download History" button at the top of the "MY ORDER HISTORY" table.
4. Save the CSV file on your PC

### Import trades
```
$ cctool <path-to-the-csv-file>
```

#### Portfolio name
You can specify an existing portfolio by full or partial name
```
$ cctool <path-to-the-csv-file> --portfolio "My portfolio"
```

#### Ignore errors
There are two kind of logical errors that might happen, if you sell more than you have, or if you add an existing item.
There is an option allowing to suppress these errors and simply skip such items.
```
$ cctool <path-to-the-csv-file> --ignore-errors
```
