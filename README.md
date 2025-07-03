# scramble

## Getting Started

Before running the code, make sure you have installed Python 3.12 or higher.

If you don't have Poetry installed, you can install it by following the instructions on
https://python-poetry.org/docs/#installation
or by running the following command:
```sh
pipx install poetry
```

Clone the repository and enter the project directory

```sh
git clone https://github.com/thatmariia/scramble.git
cd scramble
```

Create and activate the virtual environment

```sh
poetry install
```
This installs all dependencies in a virtual environment managed by Poetry.

Development code is located in the `dev` branch.
The `main` branch contains the latest stable version of the code.

---

## Using with CLI

Use Poetry to run the CLI commands:
```sh
poetry run scramble [OPTIONS] COMMAND [ARGS]...
```

Run the following to see the available commands:
```sh
poetry run scramble --help
```
To see the available subcommands for a specific command and the arguments they accept, run:
```sh
poetry run scramble COMMAND --help
```
For example, to see the parameters for `add` in the `player`, run:
```sh
poetry run scramble player add --help
```

--- 

## Using with API

Use Poetry to run the API server with the reload:
```sh
poetry run scramble-api
```

You can access the Swagger UI at [localhost:8000/docs](http://localhost:8000/docs).

---

## License

This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.

