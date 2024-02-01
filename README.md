# SupernovaController
Manages communications with the Supernova host-adapter USB HID device.

## Introduction
SupernovaController is a Python-based tool designed to interface with the Supernova host-adapter USB HID device. Offering a blocking API, it simplifies command sequences and interactions in the context of asynchronous operation environments like the one offered by the Supernova host-adapter. This approach enhances usability and efficiency, providing a streamlined experience for developers working with the Supernova device.

## Features
- **Blocking API:** A streamlined approach to interact with the Supernova device, minimizing the complexity of handling asynchronous callbacks.
- **Multi-Interface:** Easily communicate with UART, I2C and I3C Devices in an All-In-One package.
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

## Getting started

This section provides a quick guide to get you started with the `SupernovaController`.

### Prerequisites

Before proceeding, make sure you have installed the `SupernovaController` package as outlined in the Installation section.

## I3C protocol

### I3C features

This section provides a quick guide to get you started with the `SupernovaController` focusing on the I3C protocol.
In an I3C bus, the Supernova can act either as a controller or as a target.

* In controller mode the Supernova supports several features: 
    * Supernova initialization in I3C controller mode.
    * Bus initialization.
    * Setting of bus parameters.
    * Discovery of devices on the bus.
    * I3C read operations of up to 255 bytes and I3C write operations of up to 1024 bytes.
    * CCCs.
    * Handling of IBIs.
* In target mode the Supernova acts as non-circular and addressable memory that can have different layouts:
    - memory of 1024 registers of 1 byte size
    - memory of 512 registers of 2 bytes size
    - memory of 256 registers of 4 bytes size

    In this mode, it supports several features: 
    * Supernova initialization in I3C target mode.
    * Command to change its configuration after its initialization.
    * Write and Read commands to modify the memory via USB.
    * Notifications that indicate the end of a transfer (that involves the Supernova) detection.

### Basic I3C Communication

#### Operations valid for the Supernovas in I3C target mode and I3C controller mode

1. ***Initializing the Supernova Device:***

   Imports and initializes the `SupernovaDevice`. Optionally, specifies the USB HID path if multiple devices are connected:

   ```python
   from supernovacontroller.sequential import SupernovaDevice

   device = SupernovaDevice()
   # Optionally specify the USB HID path
   device.open(usb_address='your_usb_hid_path')
   ```

   Call `open()` without parameters if you don't need to specify a particular device.

2. ***Creating an I3C Interface:***

   Creates an I3C controller interface:

   ```python
   i3c = device.create_interface("i3c.controller")
   ```
    Or an I3C target interface:

   ```python
   i3c = device.create_interface("i3c.target")
   ```    

3. ***Closing the Device:***

   Closes the device when done:

   ```python
   device.close()
   ```

### Operations intended for the Supernova in I3C controller mode

1. ***Initializing the I3C peripheral:***

    Initializes the Supernova I3C peripheral in controller mode:

    ```python
   success, status = device.controller_init()
   ```
    By default, the peripheral is initialized by the open() method in controller mode, so it may not be needed to call it in most cases.

2. ***Setting Bus Voltage:***

   Sets the bus voltage (in mV) for the I3C bus. This step is required before initializing the bus if you don't specify the voltage parameter in `init_bus`:

   ```python
   success, data = i3c.set_bus_voltage(3300)
   ```

3. ***Initializing the I3C Bus:***

   Initializes the I3C bus. The voltage parameter is optional here if already set via `set_bus_voltage`:

   ```python
   success, data = i3c.init_bus()  # Voltage already set, so no need to specify it here
   ```

   If the bus voltage wasn't set earlier, you can initialize the bus with the voltage parameter:

   ```python
   success, data = i3c.init_bus(3300)  # Setting the voltage directly in init_bus
   ```

4. ***Discovering Devices on the Bus:***

   Retrieves a list of connected I3C devices:

   ```python
   success, targets = i3c.targets()
   if success:
       for target in targets:
           print(f"Found device: {target}")
   ```

5. ***Reading and Writing to a Device:***

   Performs I3C write and read operations on a target device:

   ```python
   # Write data specifying address, mode, register and a list of bytes.
    result = i3c_controller.write(TARGET_ADDRESS, TRANSFER_MODE, SUBADDR, DATA)

   # Read data specifying address, mode, register and buffer length.
   success, data = i3c_controller.read(TARGET_ADDRESS, TRANSFER_MODE, SUBADDR, LENGTH)
   if success:
       print(f"Read data: {data}")
   ```

    * TARGET_ADDRESS is a c_uint8 variable that specifies the dynamic address of the target this transfer is directed to.
    * TRANSFER_MODE: variable of type TransferMode that indicates the mode of the transaction.
    

   ```python
    class TransferMode(Enum):
        '''
        This enum represents the possible values to be assgined to the transfer mode bits in the command descriptor.
        Defined in the USB I3C Device class specification V1.0
        '''
        I3C_SDR     = 0x00
        I3C_HDR_DDR = 0x01
        I3C_HDR_TS  = 0x02        # Not supported.
        I3C_HDR_BT  = 0x03        # Not supported.
        I2C_MODE    = 0x08
        # 0x04 - 0x07 Reserved for future HDR modes.
   ```

    * SUBADDR indicates the address of the memory to start reading. If the memory layout (defined in target_init) is MEM_1_BYTE this field is a c_uint16 variable type, c_uint8 otherwise.
    * DATA is the list of bytes that represents the data the user wants to write.
    * LENGTH is a c_uint16 that indicates the data length the user intends to read, in bytes. 
    
6. ***Performing CCCs:***

   Requests CCCs on the I3C bus, directed to an specific target or broadcast. They take different parameters depending on the command, examples of them can be:

   ```python
    success, result = i3c_controller.ccc_getpid(TARGET_ADDRESS)

    MWL = 1024
    i3c_controller.ccc_unicast_setmwl(TARGET_ADDRESS, MWL)
    success, result = i3c_controller.ccc_getmwl(TARGET_ADDRESS)
   ```

### Operations intended for the Supernova in I3C target mode

1. ***Initializing the I3C peripheral:***

    Initializes the Supernova I3C peripheral in target mode and sets its initial configuration which includes: the internal memory layout, its maximum write length, maximum read length, seconds waited to allow an In-Band Interrupt (IBI) to drive SDA low when the controller is not doing so and some flags regarding the target behaviour in the I3C bus.

    ```python
   success, status = device.target_init(MEMORY_LAYOUT, USECONDS_TO_WAIT_FOR_IBI, MRL, MWL, TARGET_CONF)
   ```

    * MEMORY_LAYOUT indicates the layout of the Supernova internal memory, of I3cTargetMemoryLayout_t class:
    
        ```python
        class I3cTargetMemoryLayout_t(Enum):
            MEM_1_BYTE  = 0x00
            MEM_2_BYTES = 0x01
            MEM_4_BYTES = 0x02
        ```

    * USECONDS_TO_WAIT_FOR_IBI: c_uint16 that represents the micro seconds to allow an In-Band Interrupt (IBI) to drive SDA low when the controller is not doing so
    
    * MRL: c_uint16 that indicates the maximum read length that the user wants the Supernova to handle
    
    * MWL: c_uint16 that indicates the maximum write length that the user wants the Supernova to handle
    
    * TARGET_CONF: c_uint8 that represents a series of flags that describe the features of the Supernova in target mode. If no TARGET_CONF is assigned, it acquires its default value 12.
    
        The byte is formed joining fields from the following enums by the logical OR operation:

        ```python
        class I3cOffline(Enum):
            OFFLINE_UNFIT       = 0x00
            OFFLINE_CAPABLE     = 0x01
        ```

        If `I3cOffline = 0x01` when the target enable (`SCONFIG[SLVENA]) is set to 1, then the I3C module waits for either 60 s of bus quiet or an HDR Exit Pattern. This waiting ensures that the bus is not in HDR mode, and so can safely monitor for the next activity in Single Data Rate (SDR) mode.
    
        
        ```python
        class PartNOrandom(Enum):
            PART_NUMB_DEFINED      = 0x00
            PART_NUMB_RANDOM       = 0x02
        ```
        If `PartNOramdom = 0x00`, `SIDPARTNO[PARTNO]` is a part number and an instance.  
        If `PartNOrandom = 0x02`, `SIDPARTNO[PARTNO]` is a random number

        ```python
        class DdrOk(Enum):
            PROHIBITED_DDR      = 0x00
            ALLOWED_DDR         = 0x04
        ```
        Indicates whether HDR-DDR is allowed (`DdrOk = 0x04`) or not (`DdrOk = 0x00`).

        ```python
        class IgnoreTE0TE1Errors(Enum):
            NOT_IGNORE_ERRORS    = 0x00
            IGNORE_ERRORS        = 0x08
        ```
        If `IgnoreTE0TE1Errors = 0x08` the target does not detect TE0 or TE1 errors, so it does not lock up waiting on an Exit Pattern.
        
        ```python
        class MatchStartStop(Enum):
            NOT_MATCH   = 0x00
            MATCH       = 0x10
        ```
        This setting allows START and STOP to be used to detect the end of a message to/from this target if `MatchStartStop = 0x10`.
        
        ```python
        class AlwaysNack(Enum):
            NOT_ALWAYS_NACK     = 0x00
            ALWAYS_NACK         = 0x20
        ```
        If `AlwaysNack = 0x20` the target rejects all requests to it, except for broadcast Common Command Codes (CCCs).
        
2. ***Set Supernova configuration:***

    Sets the configuration of the Supernova such as its maximum write length, maximum read length, seconds waited to allow an In-Band Interrupt (IBI) to drive SDA low when the controller is not doing so and some flags regarding the target behaviour in the I3C bus:

    ```python
   success, status = device.set_configuration(USECONDS_TO_WAIT_FOR_IBI, MRL, MWL, TARGET_CONF)
   ```
    All the input parameters hold the same meaning as the ones for target_init command described above.

3. ***Write memory:***

    Writes the internal memory of the Supernova:

    ```python
   success, error = device.write_memory(SUBADDR, DATA)
   ```
    * SUBADDR indicates the address of the memory to start writing. 
    If the memory layout (defined in target_init) is MEM_1_BYTE this field is a c_uint16 variable type, c_uint8 otherwise.
    * DATA is the list of bytes that represents the data the user wants to write
    
4. ***Read memory:***

    Retrieves data from the Supernova internal memory:

    ```python
   success, data = device.read_memory(SUBADDR, LENGTH)
   ```

    * SUBADDR indicates the address of the memory to start reading. 
    If the memory layout (defined in target_init) is MEM_1_BYTE this field is a c_uint16 variable type, c_uint8 otherwise.
    * LENGTH is a c_uint16 that indicates the data length the user intends to read, in bytes.
    

***Target Notification:***

When the Supernova acts in I3C target mode, it notifies everytime it detects the end of an I3C transfer it was involved in (not including CCCs).

The notification reports info about the last I3C transaction directed to the target Supernova.

A typical target notification looks like:

```python
{'transfer_type': 'I3C_TARGET_READ', 'memory_address': 7, 'transfer_length': 5, 'usb_result': 'CMD_SUCCESSFUL', 'manager_result': 'I3C_TARGET_TRANSFER_SUCCESS', 'driver_result': ['NO_ERROR'], 'data': [238, 238, 238, 238, 238]}
```

* The transfer_type indicates if the transfer was a read or write operation from the target point of view. It holds a value belonging to I3cTargetTransferType_t:

```python
class I3cTargetTransferType_t(Enum):
    '''
    This enum represents the type of transfer when the Supernova acts an I3C target
    '''
    I3C_TARGET_WRITE    = 1
    I3C_TARGET_READ     = 2
```

* The memory_address (c_uint8 or c_uint16 depending on the memory layout) indicates the memory address where the transfer started to work with.  
* The transfer_length (c_uint16) represents the length, in bytes, of the data transferred.
* The usb_result indicates if there was an error on the USB module or not. It holds a value belonging to UsbCommandResponseStatus:

```python
class UsbCommandResponseStatus(Enum):
    '''
    This enum identifies different response status
    CMD_SUCCESSFUL: The command was successfully requested to the corresponding module manager
    CMD_DESTINATARY_BUSY: The destinatary module could not receive the command because it was busy
    CMD_NOT_AVAILABLE: The command does not belong to the list of available commands
    '''
    CMD_SUCCESSFUL          = 0x00
    CMD_DESTINATARY_BUSY    = 0x01  
    CMD_NOT_AVAILABLE       = 0x02
```    
    
* The manager_result indicates if there was an error on the manager side of the I3C module (not driver related). It holds a value belonging to I3cTargetTransferType_t:

```python
class I3cTargetTransferResult_t(Enum):
    '''
    Represents the result of a transfer from the Supernova in I3C target mode
    '''
    I3C_TARGET_TRANSFER_SUCCESS     = 0
    I3C_TARGET_TRANSFER_FAIL        = 1
```    
    
* The driver_result indicates if there was no error, if there was an abort condition or a list of all the driver errors that arose during the transfer. It can take values belonging to I3cTargetTransferError_t:

```python
class I3cTargetTransferError_t(Enum):
    '''
    Represents the error of a transfer from the Supernova in I3C target mode
    '''
    NO_ERROR            = 0x0000
    ORUN_ERROR          = 0x0001
    URUN_ERROR          = 0x0002
    URUNNACK_ERROR      = 0x0004
    ABORT_CONDITION     = 0x0008
    INVSTART_ERROR      = 0x0010
    SPAR_ERROR          = 0x0020
    HPAR_ERROR          = 0x0040
    HCRC_ERROR          = 0x0080
    S0S1_ERROR          = 0x0100
    OREAD_ERROR         = 0x1000
    OWRITE_ERROR        = 0x2000
```
* The data field shows the list of bytes that were transferred during the transaction. 

**Border Cases**

The fact that the memory is not circular obligates to take into account border cases:

* If the user tries to start the transfer in an address surpassing the target memory range, the target will ignore the address and will start the transfer from the end of the the previous one.

* If the transfer starts in an allowed memory address but tries to surpass the range during the transaction, it will only modify the bytes in the allowed range and discard the rest. The end of the transfer is taken as the end of the memory.

### Next Steps

After installing the `SupernovaController` package, you can further explore its capabilities by trying out the examples included in the installation. These examples demonstrate practical applications of UART, I2C and I3C protocols:

- **Basic I3C Example (`basic_i3c_example.py`):** Learn the basics of I3C bus initialization and device communication using the Supernova as an I3C controller.
- **Basic I3C Target Mode Example (`basic_i3c_target_example.py`):** Learn the basics of I3C target mode implementation using two Supernovas, one as an I3C target and the other one as a controller.
- **Basic I2C Example (`basic_i2c_example.py`):** Get started with fundamental I2C operations.
- **Basic UART Example (`basic_uart_example.py`):** Try out the UART protocol Hands-On.
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
