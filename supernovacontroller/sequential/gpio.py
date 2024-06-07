from transfer_controller import TransferController
from BinhoSupernova.Supernova import Supernova
from BinhoSupernova.commands.definitions import (
    GetUsbStringSubCommand, GpioPinNumber, GpioLogicLevel, GpioFunctionality, GpioTriggerType,
    COMMANDS_DICTIONARY, GPIO_CONFIGURE_PIN, GPIO_DIGITAL_WRITE, GPIO_DIGITAL_READ,
    GPIO_SET_INTERRUPT, GPIO_DISABLE_INTERRUPT
)
from supernovacontroller.errors import BackendError

class SupernovaGPIOInterface:
    def __init__(self, driver: Supernova, controller: TransferController, notification_subscription):
        """
        Initializes a new instance of the SupernovaGPIOInterface class. This interface is used for GPIO communication with the Supernova.
        """
        self.driver = driver
        self.controller = controller
        self.configured_pins = {}
        self.bus_voltage = None
        self.hardware_version = self.__get_hardware_version()

    def __get_hardware_version(self):
        """
        Retrieves the hardware version of the connected Supernova device.

        Returns:
        str: The hardware version of the Supernova device.
        """
        try:
            response = self.controller.sync_submit([
                lambda transfer_id: self.driver.getUsbString(transfer_id, GetUsbStringSubCommand.HW_VERSION)
            ])
            if response[0]["name"] == "GET USB STRING" and "message" in response[0]:
                return response[0]["message"]
        except Exception as e:
            raise BackendError(original_exception=e) from e

        raise BackendError("Unable to retrieve hardware version.")

    def set_bus_voltage(self, voltage_mv: int):
        """
        Sets the bus voltage for the GPIO interface to a specified value.
        The method updates the bus voltage of the instance only if the operation is successful. The success
        or failure of the operation is determined based on the response from the hardware.

        Args:
        voltage_mv (int): The voltage value to be set for the GPIO bus in millivolts (mV).

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
        set_voltage_method = None

        if self.hardware_version.startswith("HW-B"):
            set_voltage_method = self.driver.setI2cSpiUartBusVoltage
            expected_name = "SET I2C-SPI-UART BUS VOLTAGE"
        elif self.hardware_version.startswith("HW-C"):
            set_voltage_method = self.driver.setI3cBusVoltage
            expected_name = "SET I3C BUS VOLTAGE"
        else:
            raise BackendError(f"Unsupported hardware version: {self.hardware_version}")

        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: set_voltage_method(transfer_id, voltage_mv),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_success = responses[0]["name"] == expected_name and responses[0]["result"] == 0

        if response_success:
            self.bus_voltage = voltage_mv
            return (True, voltage_mv)
        else:
            return (False, "Set bus voltage failed")

    def __check_if_response_is_correct(self, response):
        """
        Checks if the response received from the Supernova indicates successful execution of the GPIO method.

        Args:
        response (dict): A dictionary containing response data from the Supernova GPIO request.

        Returns:
        bool: True if the response indicates successful, False otherwise.
        """
        return all([
            response["usb_error"] == "CMD_SUCCESSFUL",
            response["manager_error"] == "GPIO_NO_ERROR",
            response["driver_error"] == "GPIO_DRIVER_NO_ERROR"
        ])

    def configure_pin(self, pin_number: GpioPinNumber, functionality: GpioFunctionality):
        """
        Configures a GPIO pin with the specified functionality.

        Args:
        pin_number (GpioPinNumber): The GPIO pin number to configure.
        functionality (GpioFunctionality): The desired functionality for the GPIO pin.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the configuration.
            - The second element is a string describing the result of the configuration process.
        """
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.gpioConfigurePin(transfer_id, pin_number, functionality)
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_success = responses[0]["name"] == "CONFIGURE GPIO PIN" and self.__check_if_response_is_correct(responses[0])

        if response_success:
            self.configured_pins[pin_number] = functionality
        return (response_success, "Success" if response_success else "Configuration failed, error from the Supernova")

    def digital_write(self, pin_number: GpioPinNumber, logic_level: GpioLogicLevel):
        """
        Writes a digital logic level to a GPIO pin.

        Args:
        pin_number (GpioPinNumber): The GPIO pin number to write to.
        logic_level (GpioLogicLevel): The logic level to write to the GPIO pin.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the write operation.
            - The second element is a string describing the result of the write operation.
        """
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.gpioDigitalWrite(transfer_id, pin_number, logic_level)
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_success = responses[0]["name"] == "GPIO DIGITAL WRITE" and self.__check_if_response_is_correct(responses[0])
        return (response_success, "Success" if response_success else "Digital write failed, error from the Supernova")

    def digital_read(self, pin_number: GpioPinNumber):
        """
        Reads the digital logic level from a GPIO pin.

        Args:
        pin_number (GpioPinNumber): The GPIO pin number to read from.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the read operation.
            - The second element is the logic level read from the GPIO pin if successful, or an error message if failed.
        """
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.gpioDigitalRead(transfer_id, pin_number)
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_success = responses[0]["name"] == "GPIO DIGITAL READ" and self.__check_if_response_is_correct(responses[0])
        if response_success:
            return (True, responses[0]["logic_level"])
        return (False, "Digital read failed, error from the Supernova")

    def set_interrupt(self, pin_number: GpioPinNumber, trigger: GpioTriggerType):
        """
        Sets an interrupt on a GPIO pin.

        Args:
        pin_number (GpioPinNumber): The GPIO pin number to set the interrupt on.
        trigger (GpioTriggerType): The trigger type for the interrupt.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of setting the interrupt.
            - The second element is a string describing the result of setting the interrupt.
        """
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.gpioSetInterrupt(transfer_id, pin_number, trigger)
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_success = responses[0]["name"] == "GPIO SET INTERRUPT" and self.__check_if_response_is_correct(responses[0])
        return (response_success, "Success" if response_success else "Set interrupt failed, error from the Supernova")

    def disable_interrupt(self, pin_number: GpioPinNumber):
        """
        Disables an interrupt on a GPIO pin.

        Args:
        pin_number (GpioPinNumber): The GPIO pin number to disable the interrupt on.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of disabling the interrupt.
            - The second element is a string describing the result of disabling the interrupt.
        """
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.gpioDisableInterrupt(transfer_id, pin_number)
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_success = responses[0]["name"] == "GPIO DISABLE INTERRUPT" and self.__check_if_response_is_correct(responses[0])
        return (response_success, "Success" if response_success else "Disable interrupt failed, error from the Supernova")

    def wait_for_notification(self, timeout):
        """
        Waits for GPIO interrupt notification.

        This method waits for a notification related to GPIO interrupt for the specified timeout duration.
        It uses the GPIO notification subscription to wait for incoming interrupt notifications.

        Args:
        timeout: The duration in seconds to wait for the notification.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of receiving the notification.
            - The second element is either the received payload if successful or an error message.
        """
        received_data_flag, notification = self.gpio_notification.wait_for_notification(timeout)

        if not received_data_flag:
            return (False, "Timeout occurred while waiting for the GPIO interrupt notification")
        
        response_ok = self.__check_if_response_is_correct(notification)
        if not response_ok:
            return (False, "Error from Supernova while receiving GPIO interrupt data")

        return (True, notification["pin_number"])