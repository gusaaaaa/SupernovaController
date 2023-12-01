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

---
## Getting Started

This section provides a quick guide to get you started with the `SupernovaController`, focusing on using the I3C protocol. The example demonstrates how to initialize an I3C bus, set bus parameters, discover devices on the bus, and perform read/write operations.

### Prerequisites

Before proceeding, make sure you have installed the `SupernovaController` package as outlined in the Installation section.

### Basic I3C Communication

1. **Initializing the Supernova Device:**

   Import and initialize the `SupernovaDevice`. Optionally, specify the USB HID path if multiple devices are connected:

   ```python
   from supernovacontroller.sequential import SupernovaDevice

   device = SupernovaDevice()
   # Optionally specify the USB HID path
   device.open(usb_address='your_usb_hid_path')
   ```

   Call `open()` without parameters if you don't need to specify a particular device.

2. **Creating an I3C Interface:**

   Create an I3C controller interface:

   ```python
   i3c = device.create_interface("i3c.controller")
   ```

3. **Setting Bus Voltage:**

   Set the bus voltage for the I3C bus. This step is required before initializing the bus if you don't specify the voltage parameter in `init_bus`:

   ```python
   i3c.set_bus_voltage(3300)
   ```

4. **Initializing the I3C Bus:**

   Initialize the I3C bus. The voltage parameter is optional here if already set via `set_bus_voltage`:

   ```python
   i3c.init_bus()  # Voltage already set, so no need to specify it here
   ```

   If the bus voltage wasn't set earlier, you can initialize the bus with the voltage parameter:

   ```python
   i3c.init_bus(3300)  # Setting the voltage directly in init_bus
   ```

5. **Discovering Devices on the Bus:**

   Retrieve a list of connected I3C devices:

   ```python
   success, targets = i3c.targets()
   if success:
       for target in targets:
           print(f"Found device: {target}")
   ```

6. **Reading and Writing to a Device:**

   Perform write and read operations on a target device. Replace `0x08` with the dynamic address of the device:

   ```python
   # Write data
   i3c.write(0x08, i3c.TransferMode.I3C_SDR, [0x00, 0x00], [0xDE, 0xAD, 0xBE, 0xEF])

   # Read data
   success, data = i3c.read(0x08, i3c.TransferMode.I3C_SDR, [0x00, 0x00], 4)
   if success:
       print(f"Read data: {data}")
   ```

7. **Closing the Device:**

   Close the device when done:

   ```python
   device.close()
   ```

### Next Steps

After installing the `SupernovaController` package, you can further explore its capabilities by trying out the examples included in the installation. These examples demonstrate practical applications of both I2C and I3C protocols:

- **Basic I3C Example (`basic_i3c_example.py`):** Learn the basics of I3C bus initialization and device communication.
- **Basic I2C Example (`basic_i2c_example.py`):** Get started with fundamental I2C operations.
- **IBI Example (`ibi_example.py`):** Understand handling In-Band Interrupts (IBI) in I3C.
- **ICM42605 I3C Example (`ICM42605_i3c_example.py`):** Explore a real-world application of I3C with the ICM42605 sensor.

#### Accessing the Examples

To access the examples, you first need to find the installation directory of the `SupernovaController` package. This can be done using the following Python commands:

```python
import supernovacontroller
import os

examples_path = os.path.join(supernovacontroller.__path__[0], 'examples')
print(f"Examples are located in: {examples_path}")
```

Navigate to this directory to find the example scripts. You can run an example directly from this directory using Python. For instance:

```sh
python /path/to/examples/basic_i2c_example.py
```

Replace `/path/to/examples/` with the actual path printed in the previous step and `basic_i2c_example.py` with the name of the example you wish to run.

#### Exploring Further

Each example is designed to provide insights into different aspects of the `SupernovaController` usage. By running and modifying these examples, you'll gain a deeper understanding of how to effectively use the package in various scenarios.

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
