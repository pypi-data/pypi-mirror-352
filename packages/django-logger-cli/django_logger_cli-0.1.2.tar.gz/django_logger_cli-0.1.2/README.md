# Django Logger CLI

A lightweight and interactive CLI tool to generate Django-style logging configurations — quickly, cleanly, and flexibly.

## Features

- Interactive logger setup with `click`
- Support for `FileHandler`, `StreamHandler`, and time-rotating handlers
- Option to select from default Django loggers or create custom ones
- Easy integration with existing Django projects
- Quick start with `--basic-config` for minimal setup
- CLI help system with `--help`

---

## Installation

### Install directly from PyPI:

1. **Install directly from PyPI:**

    ```bash
    pip install django-logger-cli

 **Make sure to provide a .env file for local development., craete one by copying from sampleenv.txt file.**

2. **Install locally:**

    ```bash
    git clone https://github.com/codewithmanuu/django-logger.git
    cd django-logger-cli
    pip install .

## Usage

1. **To initialize logging configuration interactively:**
    ```bash
    django-logger init

2. **For using the basic config without answering the prompt**
    ```bash
    djangologger init --basic-config

## Help Menu
1. 
    ```bash
    djangologger init --help

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Pull requests and suggestions are welcome!

- Fork the repo
- Create a branch (git checkout -b feature/fooBar)
- Commit your changes (git commit -am 'Add some fooBar')
- Push to the branch (git push origin feature/fooBar)
- Create a new Pull Request

## Author
- Manukrishna S
- <mailto:manukrishna.s2001@gmail.com>