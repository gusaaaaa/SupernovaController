from transfer_controller import TransferController
from BinhoSupernova.Supernova import Supernova
from supernovacontroller.errors import BackendError, BusVoltageError
from BinhoSupernova.commands.definitions import (
    SpiControllerBitOrder, SpiControllerMode, SpiControllerDataWidth,
    SpiControllerChipSelect, SpiControllerChipSelectPolarity, COMMANDS_DICTIONARY,
    SPI_CONTROLLER_INIT, SPI_CONTROLLER_SET_PARAMETERS, SPI_CONTROLLER_TRANSFER
)

class SupernovaSPIControllerBlockingInterface:
    # Private Methods
    def __init__(self, driver: Supernova, controller: TransferController, notification_subscription):
        """
        Initializes a new instance of the SupernovaSPIControllerBlockingInterface class. This interface is used for
        blocking SPI controller communication with the Supernova.
        By default the SPI controller peripheral is configured with the following parameters:
            Bit order: MSB first
            Mode: Mode 0
            Data width: 8 bits data width, can't be changed
            Chip select: CS0
            Chip select polarity: Active low
            Frequency: 10 MHz
        """

        # Supernova driver instance
        self.driver = driver
        # Transfer controller instance
        self.controller = controller
        # SPI controller communication parameters
        self.bitOrder = SpiControllerBitOrder.MSB                        # MSB first
        self.mode = SpiControllerMode.MODE_0                             # Mode 0
        self.dataWidth = SpiControllerDataWidth._8_BITS_DATA             # 8 bits data width
        self.chipSelect = SpiControllerChipSelect.CHIP_SELECT_0          # Chip select 0
        self.chipSelectPol = SpiControllerChipSelectPolarity.ACTIVE_LOW  # Active low
        self.frequency = 10000000                                        # 10 MHz
        self.bus_voltage = None
    
    def __store_parameters(self, bitOrder: SpiControllerBitOrder=None, mode: SpiControllerMode=None, chipSelect: SpiControllerChipSelect=None,
                           chipSelectPol: SpiControllerChipSelectPolarity=None, frequency: int=None):
        """
        Stores the SPI controller communication parameters.

        This method allows setting and updating specific SPI controller communication parameters such as bit order, spi mode,
        data width, chip select, chip select polarity and frequency. It selectively updates the parameters if new values are provided,
        retaining existing values otherwise.

        Args:
        bitOrder (SpiControllerBitOrder, optional): The bit order for SPI communication (default: None).
        mode (SpiControllerMode, optional): The mode for SPI communication (default: None).
        chipSelect (SpiControllerChipSelect, optional): The selected Chip to communicate with (default: None).
        chipSelectPol (SpiControllerChipSelectPolarity, optional): The chip select polarity setting for SPI communication (default: None).
        frequency (int, optional): The clock frequency for the SPI communication (default: None).
        """

        # Update parameters if provided
        self.bitOrder = bitOrder or self.bitOrder
        self.mode = mode or self.mode
        self.chipSelect = chipSelect or self.chipSelect
        self.chipSelectPol = chipSelectPol or self.chipSelectPol
        self.frequency = frequency or self.frequency

    def __check_data_complete(self):
        """
        Checks if all required SPI controller communication parameters are complete.

        This method verifies whether all the essential SPI controller communication parameters, including bit order, spi mode,
        data width, chip select, chip select polarity and frequency, have been properly set and are not None.

        Returns:
        bool: True if all parameters are complete, False otherwise.
        """

        # Check if all the configuration for SPI controller communication are set
        return all([
            self.bitOrder is not None,
            self.mode is not None,
            self.dataWidth is not None,
            self.chipSelect is not None,
            self.chipSelectPol is not None,
            self.frequency is not None
        ])
    
    def __check_if_response_is_correct(self, response):
        """
        Checks if the response received from the Supernova indicates successful execution of the SPI controller method.

        Args:
        response (dict): A dictionary containing response data from the Supernova SPI controller request.

        Returns:
        bool: True if the response indicates successful, False otherwise.
        """

        # Check if the USB, manager or driver had issues handling the SPI controller request
        return all([
            response["usb_error"] == "CMD_SUCCESSFUL",
            response["manager_error"] == "SPI_NO_ERROR" or response["manager_error"] == "SPI_ALREADY_INITIALIZED_ERROR",
            response["driver_error"] == "SPI_DRIVER_NO_TRANSFER_ERROR"
        ])
    
    def set_bus_voltage(self, voltage_mv: int):
        """
        Sets the bus voltage for the SPI controller interface to a specified value.
        The method updates the bus voltage of the instance only if the operation is successful. The success
        or failure of the operation is determined based on the response from the hardware.

        Args:
        voltage_mv (int): The voltage value to be set for the SPI bus in millivolts (mV).

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

        Raises:
        BackendError: If an exception occurs setting the bus voltage process.
        """

        # Set the SPI bus voltage accordingly
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.setI2cSpiUartBusVoltage(transfer_id, voltage_mv),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e
        
        # Check if the response is of the expected type (by name) and it was successful 
        response_success = responses[0]["name"] == "SET I2C-SPI-UART BUS VOLTAGE" and responses[0]["result"] == 0

        # If successful, update the bus voltage
        if response_success:
            result = (True, voltage_mv)
            self.bus_voltage = voltage_mv
        # If not successful update method response
        else:
            result = (False, "Set bus voltage failed")
            self.bus_voltage = None

        return result
    
    def init_bus(self, bitOrder: SpiControllerBitOrder=None, mode: SpiControllerMode=None,
                 chipSelect: SpiControllerChipSelect=None, chipSelectPol: SpiControllerChipSelectPolarity=None, frequency: int=None):
        """
        Initializes the SPI bus with specified parameters.

        This method initializes the SPI bus with the provided communication parameters such as bit order, spi mode,
        chip select, chip select polarity and frequency. If parameters are provided, it configures the bus
        accordingly; otherwise, it retains the current settings.

        Args:
        bitOrder (SpiControllerBitOrder, optional): The bit order for SPI communication (default: None).
        mode (SpiControllerMode, optional): The mode for SPI communication (default: None).
        chipSelect (SpiControllerChipSelect, optional): The selected Chip to communicate with (default: None).
        chipSelectPol (SpiControllerChipSelectPolarity, optional): The chip select polarity setting for SPI communication (default: None).
        frequency (int, optional): The clock frequency for the SPI communication (default: None).

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the initialization.
            - The second element is a string describing the result of the initialization process.

        Raises:
        BackendError: If an exception occurs during the initialization process.

        Note:
        - The method does not perform validation on any of the SPI communication parameters. Users of this
          method should ensure that the provided configuration is valid.
        """

        # Update the SPI class attributes with the provided data
        self.__store_parameters(bitOrder=bitOrder, mode=mode, chipSelect=chipSelect, chipSelectPol=chipSelectPol, frequency=frequency)
        # Check if all the needed configurations for SPI communication are correctly set
        is_data_complete = self.__check_data_complete()
        # Return failure if data is incomplete
        if not is_data_complete: 
            return (False, "Init failed, incomplete parameters to initialize bus")
        
        # Request SPI controller initialization 
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.spiControllerInit(id=transfer_id, bitOrder=self.bitOrder, mode=self.mode, dataWidth=self.dataWidth, chipSelect=self.chipSelect, chipSelectPol=self.chipSelectPol, frequency=self.frequency)
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e
        
        # Check if the response is of the expected type (by name) and it was successful 
        response_success = responses[0]["name"] == COMMANDS_DICTIONARY[SPI_CONTROLLER_INIT]["name"] and self.__check_if_response_is_correct(responses[0])

        return (response_success, "Success" if response_success else "Init failed, error from the Supernova")
     
    def set_parameters(self, bitOrder: SpiControllerBitOrder=None, mode: SpiControllerMode=None,
                       chipSelect: SpiControllerChipSelect=None, chipSelectPol: SpiControllerChipSelectPolarity=None, frequency: int=None):
        """
        Sets SPI controller communication parameters.

        This method sets the SPI controller communication parameters such as bit order, spi mode, chip select,
        chip select polarity and frequency. If parameters are provided, it configures the parameters;
        otherwise, it retains the current settings.

        Args:
        bitOrder (SpiControllerBitOrder, optional): The bit order for SPI communication (default: None).
        mode (SpiControllerMode, optional): The mode for SPI communication (default: None).
        chipSelect (SpiControllerChipSelect, optional): The selected Chip to communicate with (default: None).
        chipSelectPol (SpiControllerChipSelectPolarity, optional): The chip select polarity setting for SPI communication (default: None).
        frequency (int, optional): The clock frequency for the SPI communication (default: None).

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of setting the parameters.
            - The second element is a string describing the result of setting the parameters.

        Raises:
        BackendError: If an exception occurs while setting the parameters.

        Note:
        - The method does not perform validation on any of the SPI communication parameters. Users of this
          method should ensure that the provided configuration is valid.
        """

        # Update the SPI class attributes with the provided data
        self.__store_parameters(bitOrder=bitOrder, mode=mode, chipSelect=chipSelect, chipSelectPol=chipSelectPol, frequency=frequency)
        # Check if all the needed configurations for SPI communication are correctly set
        is_data_complete = self.__check_data_complete()
        # Return failure if data is incomplete
        if not is_data_complete: 
            return (False, "Set parameters failed, incomplete parameters to do set parameters")

        responses = None
        # Request SPI controller set parameters 
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.spiControllerSetParameters(id=transfer_id, bitOrder=self.bitOrder, mode=self.mode, dataWidth=self.dataWidth, chipSelect=self.chipSelect, chipSelectPol=self.chipSelectPol, frequency=self.frequency)
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        # Check if the response is of the expected type (by name) and it was successful 
        response_success = responses[0]["name"] == COMMANDS_DICTIONARY[SPI_CONTROLLER_SET_PARAMETERS]["name"] and self.__check_if_response_is_correct(responses[0])

        return (response_success, "Success" if response_success else "Set Parameters failed, error from the Supernova")

    def get_parameters(self):
        """
        Retrieves the current SPI controller communication parameters.

        This method retrieves the current SPI controller communication parameters, including bit order, spi mode,
        data width, chip select, chip select polarity and frequency.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) of retrieving parameters.
            - The second element is a tuple containing the current SPI controller communication parameters:
                (bitOrder, mode, dataWidth, chipSelect, chipSelectPol, frequency).
        """

        # return configured SPI controller parameters
        return (True, (self.bitOrder, self.mode, self.dataWidth, self.chipSelect, self.chipSelectPol, self.frequency))
    
    def transfer(self, data, transferLength):
        """
        Transfers data over the SPI bus.

        This method performs a transfer of the provided data over the SPI bus if the bus is initialized. 

        Args:
        data: The data to be transmitted over the SPI bus.
        transferLength: 2-bytes integer that represents the transfer length. The range allowed is [1, 1024].

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the send operation.
            - The second element is a string describing the result of the SPI transfer.

        Raises:
        BackendError: If an exception occurs during the transmission process.
        """

        responses = None
        # Request SPI transfer
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.spiControllerTransfer(id=transfer_id, payload=data, transferLength=transferLength),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e
        
        # Check if the response is of the expected type (by name) and it was successful 
        response_success =  responses[0]["name"] == COMMANDS_DICTIONARY[SPI_CONTROLLER_TRANSFER]["name"] and self.__check_if_response_is_correct(responses[0])
            
        return (response_success, responses[0]["payload"] if response_success else None)