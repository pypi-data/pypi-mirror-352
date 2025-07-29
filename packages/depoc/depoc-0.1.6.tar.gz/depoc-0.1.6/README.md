# Depoc API Python Library
 
I built this library to simplify interaction with the Depoc API, which I'm currently developing. It enables convenient HTTP requests - retrieving, creating, updating, and deleting resources - and allows me to use the API daily in a real business environment.

This library also includes a CLI tool, accessible via the `depoc` command, which will be described in detail later.

Note: Both the API and this library are actively under development and may contain major issues.

This project was inspired by the [stripe-python](https://github.com/stripe/stripe-python) library.

## Installation

Install via [pip](http://www.pip-installer.org/)
```sh
$ Pip install depoc
```

## Getting Started

The library requires your account's access token for authentication.

Currently, the only supported method to get your token is to instantiate the Connection class with your username and password.

```python
from depoc import Connection

user = Connection(username="foo", password="bar")

# returns the account's access token
user.token
```

## Usage

You're now ready to start using the library. Instatiate the DepocClient class with the access token you just got.

```python
from depoc import DepocClient

client = DepocClient(user.token)

# Retrieve all customers
customers = client.customer.all()

# Retrieve an specific customer
customer = client.customer.get('ID-KLSJDF331')
```

## Handling Exceptions

~~Unsuccessful requests raise exceptions. The class of the exception will reflect the sort of error that occurred.~~

## Requirements

- Python 3.12+

## Third Party Libraries and Dependencies

The following libraries will be installed when you install the Depoc API library:
- requests
- appdirs
- click
- rich

## CLI

Installing the Depoic API Python library provides access to the `depoc` command. Before using the Depoc CLI, you must configure your credentials by running the `depoc login` command.

```sh
$ depoc login
Username: foo
Password: bar
```

## CLI Usage

```sh
depoc [command]

# Run `--help` for detailed information about the CLI commands
depoc [command] --help
```

## Commands

The Depoc CLI supports a broad number of commands. Bellow are some of the most used ones:
- me
- login
- logout
- account
- customer
- transaction
- bank
- payable
- receivable

## Command Output

The default output is a box layout rendered with [Rich](https://rich.readthedocs.io) for improved readability.

```sh
$ depoc bank 
╭─ ANY BANK ──────────────────────────────────────────────────╮
│                                                $10,374.12   │
│                                                             │
│ 01JN7MFR675GASDKFLJW31N22V                                  │
╰─────────────────────────────────────────────────────────────╯   
╭─ THE SECOND BANK ───────────────────────────────────────────╮
│                                                    $744.89  │
│                                                             │
│ 02JNLSKFJALSDKJFSALVKR962V                                  │
╰─────────────────────────────────────────────────────────────╯   
╭─ BANK ONE ──────────────────────────────────────────────────╮
│                                                      $2.53  │
│                                                             │
│ 03JN7MFR675G1SJLKDFJ20923J                                  │
╰─────────────────────────────────────────────────────────────╯

Total Balance: $11,121.54                 

```
