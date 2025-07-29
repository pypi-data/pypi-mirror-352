 # Codexium

A tool to auto-generate a professional README for your project.

## Installation

To install Codexium, use pip:

```bash
pip install codexium
```

## Usage

Navigate to your project directory and run the following command:

```bash
codexium .
```

Replace `.` with the path to your project folder if it's not in the current directory.

Codexium will scan for relevant files, compile them into a format suitable for a README, and then prompt an AI model to generate a comprehensive and well-written README.md file for you. The resulting file will be saved in the root of your project folder.

## Development

You can make changes to the code and test it locally by running:

```bash
python -m codexium .
```

## Contributing

Contributions are welcome! If you'd like to contribute, please fork this repository, create a new branch for your feature or bugfix, and submit a pull request when ready.

## Contact

For any questions or inquiries, feel free to open an issue on this repository or reach out via Github

---

This project is a simple example of using an AI model to generate documentation based on provided code snippets. It makes use of the [Click](https://click.pocoo.org/) and [Requests](https://requests.readthedocs.io/en/latest/) libraries in Python.

For further information about this project, refer to the source code or open an issue on this repository.
