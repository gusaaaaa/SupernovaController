# SupernovaController
Manages communications with the Supernova host-adapter USB HID device.

## Introduction
SupernovaController is a Python-based tool designed to interface with the Supernova host-adapter USB HID device. Offering a blocking API, it simplifies command sequences and interactions in the context of asynchronous operation environments like the one offered by the Supernova host-adapter. This approach enhances usability and efficiency, providing a streamlined experience for developers working with the Supernova device.

## Features
- **Blocking API:** A streamlined approach to interact with the Supernova device, minimizing the complexity of handling asynchronous callbacks.
- **Communication** Seamlessly manages command responses and notifications, facilitating easier and more intuitive command sequencing.
- **Examples:** Comprehensive examples demonstrating the practical application of the blocking API.

## Installation

To install the SupernovaController package, follow these steps:

1. **Prerequisites:**
   - Ensure that you have Python 3.5 or later installed on your system.
   - It's recommended to use a virtual environment for the installation to avoid any conflicts with other Python packages. You can create a virtual environment using tools like `venv` or `conda`.

2. **Install the Package:**
   - Open your command line interface (CLI).
   - Navigate to your project directory or the directory where you want to install the SupernovaController.
   - Run the following command:
     ```sh
     pip install supernovacontroller
     ```

    This command will download and install the SupernovaController package along with its dependencies (`transfer_controller` and `BinhoSupernova`) from PyPI.

3. **Updating the Package:**
   - To update the SupernovaController to the latest version, run:
     ```sh
     pip install --upgrade supernovacontroller
     ```

4. **Troubleshooting:**
   - If you encounter any issues during the installation, make sure that your Python and pip are up to date. You can update pip using:
     ```sh
     pip install --upgrade pip
     ```
   - For any other issues or support, please contact [support@binho.io](mailto:support@binho.io).

## Usage
After installation, you can run the example scripts to see how the SupernovaController works with the Supernova host-adapter. To run an example, use the following command from the project root directory:

```sh
python -m examples.<example_script_name>
```

Replace `<example_script_name>` with the name of the example you wish to run. For instance, to run the `basic_i2c_example.py` script, you would use:

```sh
python -m examples.basic_i2c_example
```

This ensures that the example runs with the correct package context, resolving the import of the `supernovacontroller` package correctly.

## License
[TO DO]

## Contact
[TO DO]
