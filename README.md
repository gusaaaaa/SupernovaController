# SupernovaController
Manages communications with the Supernova host-adapter USB HID device.

## Introduction
SupernovaController is a Python-based tool designed to interface with the Supernova host-adapter USB HID device. Offering a blocking API, it simplifies command sequences and interactions in the context of asynchronous operation environments like the one offered by the Supernova host-adapter. This approach enhances usability and efficiency, providing a streamlined experience for developers working with the Supernova device.

## Features
- **Blocking API:** A streamlined approach to interact with the Supernova device, minimizing the complexity of handling asynchronous callbacks.
- **Communication:** Seamlessly manages command responses and notifications, facilitating easier and more intuitive command sequencing.
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

   Set the bus voltage (in mV) for the I3C bus. This step is required before initializing the bus if you don't specify the voltage parameter in `init_bus`:

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
   # Write data specifying address, mode, register and a list of bytes.
   i3c.write(0x08, i3c.TransferMode.I3C_SDR, [0x00, 0x00], [0xDE, 0xAD, 0xBE, 0xEF])

   # Read data specifying address, mode, register and buffer length.
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

The example scripts are installed in a directory named `SupernovaExamples`, which is located in your Python environment's directory. To find this directory, you can use the following Python commands:

```python
import sys
import os

examples_dir_name = "SupernovaExamples"
examples_path = os.path.join(sys.prefix, examples_dir_name)
print(f"Examples are located in: {examples_path}")
```

This will print the path to the `SupernovaExamples` directory. Navigate to this directory to find the example scripts.

You can run an example directly from this directory using Python. For instance:

```sh
python /path/to/SupernovaExamples/basic_i2c_example.py
```

Replace `/path/to/SupernovaExamples/` with the actual path printed in the previous step and `basic_i2c_example.py` with the name of the example you wish to run.

#### Exploring Further

Each example is designed to provide insights into different aspects of the `SupernovaController` usage. By running and modifying these examples, you'll gain a deeper understanding of how to effectively use the package in various scenarios.

## Error Handling

When using the `SupernovaController`, it's important to distinguish between two types of errors: regular errors and exceptions. Regular errors are those that result from 'non-successful' operations of the host adapter, typically indicated by the success status in the operation's return value. Exceptions, on the other hand, are more severe and usually indicate issues with the device communication or incorrect usage of the API.

### Handling Regular Errors
Regular errors are part of normal operation and are often indicated by the return value of a method. For instance, an operation may return a success status of `False` to indicate a failure.

**Example:**
```python
success, result = i2c.write(0x50, [0x00,0x00], [0xDE, 0xAD, 0xBE, 0xEF])
if not success:
    print(f"Operation failed with error: {result}")
```

Regular errors should be checked after each operation and handled appropriately based on the context of your application.

### Handling Exceptions
Exceptions are raised when there are issues with the device's communication or incorrect usage of the API. These are more critical and need to be addressed immediately, often requiring changes in the code or the hardware setup.

Here are some common exceptions and how to handle them:

#### 1. DeviceOpenError
Occurs when the `open` method is called with an incorrect or inaccessible USB HID path.

**Example Handling:**
```python
try:
    device.open("incorrect_hid_path")
except DeviceOpenError:
    print("Failed to open device. Please check the HID path.")
```

#### 2. DeviceAlreadyMountedError
Raised when attempting to open a device that is already open.

**Example Handling:**
```python
try:
    device.open()
    device.open()
except DeviceAlreadyMountedError:
    print("Device is already open.")
```

#### 3. DeviceNotMountedError
Thrown when trying to perform operations on a device that has not been opened yet.

**Example Handling:**
```python
try:
    device.create_interface("i3c.controller")
except DeviceNotMountedError:
    print("Device not opened. Please open the device first.")
```

#### 4. UnknownInterfaceError
Occurs when an invalid interface name is passed to the `create_interface` method.

**Example Handling:**
```python
try:
    device.create_interface("invalid_interface")
except UnknownInterfaceError:
    print("Unknown interface. Please check the interface name.")
```

#### 5. BusNotInitializedError
Raised when attempting to perform bus operations without proper initialization.

**Example Handling:**
```python
try:
    i2c.read_from(0x50, [0x00,0x00], 4)
except BusNotInitializedError:
    print("Bus not initialized. Please initialize the bus first.")
```

#### 6. BackendError
Occurs when there is an issue at the backend level, often indicating deeper problems like hardware or driver issues.

**Example Handling:**
```python
try:
    # Some operation that might cause backend error
except BackendError as e:
    print(f"Backend error occurred: {e}")
```

### General Error Handling Advice
- Always validate inputs and states before performing operations.
- Use specific exception handling rather than a general catch-all where possible, as this leads to more informative error messages and debugging.
- Ensure that any cleanup or state reset logic is executed in the event of errors.

By understanding and properly handling both regular errors and exceptions, you can ensure stable and reliable operation of applications that utilize the `SupernovaController`.

## License
SupernovaController is licensed under a Proprietary License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any inquiries, support requests, or contributions regarding the `SupernovaController` package, please contact us:

- **Organization:** Binho LLC
- **Email:** [support@binho.io](mailto:support@binho.io)

We welcome feedback and we are happy to provide assistance with any issues you may encounter.

## Limitation of Responsibility

### Disclaimer

The `SupernovaController` is provided "as is" without warranty of any kind, either express or implied, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose. The entire risk as to the quality and performance of the `SupernovaController` is with you. Should the `SupernovaController` prove defective, you assume the cost of all necessary servicing, repair, or correction.

In no event will Binho LLC be liable to you for damages, including any general, special, incidental, or consequential damages arising out of the use or inability to use the `SupernovaController` (including but not limited to loss of data or data being rendered inaccurate or losses sustained by you or third parties or a failure of the `SupernovaController` to operate with any other software), even if Binho LLC has been advised of the possibility of such damages.

### Acknowledgement

By using the `SupernovaController`, you acknowledge that you have read this disclaimer, understood it, and agree to be bound by its terms.
