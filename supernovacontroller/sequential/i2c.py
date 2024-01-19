from transfer_controller import TransferController
from BinhoSupernova.Supernova import Supernova
from supernovacontroller.errors import BackendError
from supernovacontroller.errors import BusVoltageError


class SupernovaI2CBlockingInterface:
    def __init__(self, driver: Supernova, controller: TransferController, notification_subscription):
        self.driver = driver
        self.controller = controller

        self.bus_voltage = None
        self.clock_frequency_hz = 1000000

    def set_parameters(self, clock_frequency_hz: int = 1000000):
        """
        Sets the I2C clock frequency to a specified value. The operation's success or failure
        is determined by the response from the device.

        This method configures the I2C clock frequency. By default, it sets the frequency to 1 MHz
        unless a different value is specified.

        Args:
        clock_frequency_hz (int, optional): The clock frequency in Hertz to be set for the I2C bus.
                                            Defaults to 1000000 (1 MHz).

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False)
              of the operation.
            - The second element is either the new clock frequency (indicating success) or
              an error message detailing the failure, obtained from the device's response.

        Note:
        - The method does not perform validation on the input frequency value. Users of this
          method should ensure that the provided frequency value is within acceptable limits for
          their specific I2C device and setup.
        """
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.i2cSetParameters(transfer_id, baudrate=clock_frequency_hz),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_ok = responses[0]["name"] == "I2C SET PARAMETERS" and responses[0]["completed"] == 0
        if response_ok:
            result = (True, clock_frequency_hz)
        else:
            result = (False, "Set parameters failed")

        return result

    def get_parameters(self):
        """
        Retrieves the current I2C clock frequency setting from the interface.

        This method returns the current clock frequency used for I2C communication. It does not
        query the hardware but returns the value stored in the interface instance.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean, always True in this case, indicating that the
              retrieval of the parameter is a non-failing operation (under normal circumstances).
            - The second element is the current clock frequency in Hertz (Hz) used for the I2C bus.

        Note:
        - This method assumes the internal state (clock_frequency_hz) is correctly synchronized
          with the actual hardware state. Any recent changes made by other means directly on the
          hardware might not be reflected in this returned value.
        """
        return (True, self.clock_frequency_hz)

    def set_bus_voltage(self, voltage_mv: int):
        """
        Sets the bus voltage for the I2C interface to a specified value.
        The method updates the bus voltage of the instance only if the operation is successful.

        This method attempts to set the bus voltage for the I2C interface
        to the specified value. The success or failure of the operation is determined based
        on the response from the hardware.

        Args:
        voltage_mv (int): The voltage value to be set for the I2C bus in millivolts (mV).

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False)
              of the operation.
            - The second element is either the new bus voltage (indicating success) or an
              error message detailing the failure, obtained from the device's response.

        Note:
        - The method does not perform validation on the input voltage value. Users of this
          method should ensure that the provided voltage value is within acceptable limits
          for their specific hardware configuration.
        - The bus voltage is updated in the interface instance only if the operation is successful.
        """
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.setI2cSpiUartBusVoltage(transfer_id, voltage_mv),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_ok = responses[0]["name"] == "SET I2C-SPI-UART BUS VOLTAGE" and responses[0]["result"] == 0
        if response_ok:
            result = (True, voltage_mv)
            self.bus_voltage = voltage_mv
        else:
            result = (False, "Set bus voltage failed")
            self.bus_voltage = None

        return result

    def init_bus(self, voltage: int=None):
        """
        Initializes the bus with a specified voltage, or uses the existing bus voltage if none is provided.

        This method is used to initialize the bus voltage for operations. If a voltage is provided,
        it attempts to set the bus to that voltage. If no voltage is specified, it uses the
        existing voltage setting of the bus. If the bus voltage has not been set previously and
        no voltage is provided, it raises an error.

        Args:
        voltage (int, optional): The voltage value in millivolts (mV) to initialize the bus with.
                                If None, the method uses the existing bus voltage. Defaults to None.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False)
              of the operation.
            - The second element is either the bus voltage (indicating success) or an error
              message detailing the failure.

        Raises:
        BusVoltageError: If no voltage is provided and the bus voltage has not been previously set.

        Note:
        - If a voltage is provided and the operation to set the bus voltage fails, the method
          returns the failure result immediately without attempting to use the existing bus voltage.
        """
        if voltage is None:
            if self.bus_voltage is None:
                raise BusVoltageError()
            voltage = self.bus_voltage
        else:
            (success, set_bus_voltage_result) = self.set_bus_voltage(voltage)
            if not success:
                return (False, set_bus_voltage_result)

        return (True, self.bus_voltage)

    def write(self, address, register, data):
        """
        Performs a write operation to a specified register on an I2C device.

        This method sends data to a specified register of a device with a given I2C address.
        Before performing the write operation, it checks if the bus voltage is initialized.
        If the bus is not initialized (i.e., bus voltage is None), it raises an error. The
        success or failure of the write operation is determined based on the response from the hardware.

        Args:
        address (int): The I2C address of the device to write to.
        register (int): The register address within the device where the data will be written.
        data (bytes): The data to be written to the specified register.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False)
              of the write operation.
            - The second element is None. It is reserved for future use where additional information
              might be returned in case of success or failure.

        Note:
        - It is important to ensure that the bus voltage is correctly set before attempting a write operation,
          as the correct voltage is crucial for the proper functioning of I2C communications.
        - The method does not perform any validation on the input parameters (address, register, data). Users
          should ensure these parameters are correct and within the acceptable range for the intended device.
        """
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.i2cWrite(transfer_id, address, register, data),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_ok = responses[0]["name"] == "I2C WRITE" and responses[0]["status"] == 0
        if response_ok:
            result = (True, None)
        else:
            result = (False, None)

        return result

    def read(self, address, length):
        """
        Performs a read operation from an I2C device.

        This method reads data from a device at a specified I2C address. The length of the data
        to be read is also specified. Before performing the read operation, it checks if the bus
        voltage is initialized. If the bus is not initialized (i.e., bus voltage is None), it
        raises an error. The success or failure of the read operation, along with the data read,
        is determined based on the response from the hardware.

        Args:
        address (int): The I2C address of the device to read from.
        length (int): The number of bytes to read from the device.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False)
              of the read operation.
            - The second element is the data read in bytes if the operation is successful,
              or None in case of failure.

        Note:
        - It is crucial to ensure that the bus voltage is correctly set before attempting a read operation,
          as the correct voltage is necessary for proper I2C communication.
        - The method does not perform any validation on the input parameters (address, length). Users
          should ensure these parameters are correct and within the acceptable range for the intended device.
        """
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.i2cRead(transfer_id, address, length),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_ok = responses[0]["name"] == "I2C READ" and responses[0]["status"] == 0
        if response_ok:
            result = (True, responses[0]["data"])
        else:
            result = (False, None)

        return result

    def read_from(self, address, register, length):
        """
        Performs a read operation from a specific register of an I2C device.

        This method reads data from a specified register of a device at a given I2C address.
        The number of bytes to read is also specified. Before performing the read operation,
        the method checks if the bus voltage is initialized. If the bus is not initialized
        (i.e., bus voltage is None), it raises an error. The success or failure of the read
        operation, along with the data read, is determined based on the response from the hardware.

        Args:
        address (int): The I2C address of the device to read from.
        register (int): The register address within the device from which to read.
        length (int): The number of bytes to read from the specified register.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False)
              of the read operation.
            - The second element is the data read in bytes if the operation is successful,
            or None in case of failure.

        Note:
        - It is important to ensure that the bus voltage is correctly set before attempting a read operation,
          as the correct voltage is essential for proper I2C communication.
        - The method does not perform any validation on the input parameters (address, register, length). Users
          should ensure these parameters are correct and within the acceptable range for the intended device.
        """
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.i2cReadFrom(transfer_id, address, register, length),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_ok = responses[0]["name"] == "I2C READ FROM" and responses[0]["status"] == 0
        if response_ok:
            result = (True, responses[0]["data"])
        else:
            result = (False, None)

        return result
