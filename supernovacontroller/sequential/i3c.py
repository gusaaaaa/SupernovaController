from transfer_controller import TransferController
from BinhoSupernova.Supernova import Supernova
from BinhoSupernova.commands.definitions import TransferMode
from BinhoSupernova.commands.definitions import I3cCommandType
from BinhoSupernova.commands.definitions import TransferDirection
from BinhoSupernova.commands.definitions import I3cSetFeatureSelector
from BinhoSupernova.commands.definitions import I3cClearFeatureSelector
from supernovacontroller.errors import BusVoltageError


class SupernovaI3CBlockingInterface:
    # TODO: Replicate definitions (TransferMode, I3cCommandType, TransferDirection)

    BROADCAST_ADDRESS = 0x7E

    def __init__(self, driver: Supernova, controller: TransferController):
        self.driver = driver
        self.controller = controller

        self.push_pull_clock_freq_mhz = None
        self.open_drain_clock_freq_mhz = None
        self.bus_voltage = None

    def set_parameters(self, push_pull_clock_freq_mhz: float, open_drain_clock_freq_mhz: float):
        """
        Sets the clock frequencies for push-pull and open-drain configurations.

        This method assigns the provided clock frequencies to the corresponding attributes of the instance.
        These frequencies are used for controlling the operation modes of the device.

        Args:
        push_pull_clock_freq_mhz (float): The clock frequency in MHz for the push-pull configuration.
                                        This frequency should be specified as a floating-point number
                                        indicating the desired frequency in megahertz.
        open_drain_clock_freq_mhz (float): The clock frequency in MHz for the open-drain configuration.
                                        Similar to the push-pull frequency, this should be a floating-point
                                        number indicating the frequency in megahertz.

        Note:
        - This method does not validate the input frequencies. It is the responsibility of the caller to ensure
        that the provided frequencies are within the operational limits and specifications of the device.
        - The method directly updates the instance attributes without any further processing or side effects.
        """
        self.push_pull_clock_freq_mhz = push_pull_clock_freq_mhz
        self.open_drain_clock_freq_mhz = open_drain_clock_freq_mhz

    def set_bus_voltage(self, voltage: int):
        """
        Sets the bus voltage to a specified value.
        The bus voltage of the instance is updated only if the operation is successful.

        Args:
        voltage (int): The voltage value to be set for the I3C bus in mV.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either the new bus voltage indicating success, or an error message
                detailing the failure, obtained from the device's response.

        Note:
        - The method assumes that the input voltage value is valid and does not perform any validation.
        Users of this method should ensure that the provided voltage value is within acceptable limits.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.setI3cBusVoltage(id, voltage)
        ])

        response_ok = responses[0]["name"] == "SET I3C BUS VOLTAGE" and responses[0]["result"] == 0
        if response_ok:
            result = (True, voltage)
            # We want to set the bus_voltage when we know the operation was successful
            self.bus_voltage = voltage
        else:
            result = (False, "Set bus voltage failed")
            self.bus_voltage = None

        return result

    def init_bus(self, voltage: int = None):
        """
        Initialize the bus with a given voltage (in mV).

        Args:
        voltage (int, optional): The voltage to initialize the bus with.
                                Defaults to None, in which case the existing
                                bus voltage is used.

        Raises:
        BusVoltageError: If 'voltage' is not provided or bus voltage was not set.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either the string "OK" indicating success, or an error message
                detailing the failure, obtained from the device's response.

        Note:
        - The method assumes that the input voltage value is valid and does not perform any validation.
        Users of this method should ensure that the provided voltage value is within acceptable limits.
        """

        if voltage is None:
            if self.bus_voltage is None:
                raise BusVoltageError()
            voltage = self.bus_voltage
        else:
            self.set_bus_voltage(voltage)

        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cInitBus(id, None)
        ])

        # TODO: Toggle IBIs off

        status = responses[0]["result"]
        if status == "I3C_BUS_INIT_SUCCESS":
            result = (True, "OK")
        else:
            result = (False, responses[0]["errors"])

        return result

    def reset_bus(self):
        """
        Resets the I3C bus to its default state.

        It is typically used to reset the bus to a known state, clearing any configurations or settings
        that might have been applied during the operation of the device.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either the string "OK" indicating success, or an error message
                detailing the failure, obtained from the device's response.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cClearFeature(id, I3cClearFeatureSelector.I3C_BUS, self.BROADCAST_ADDRESS)
        ])

        status = responses[0]["result"]
        if status == "I3C_CLEAR_FEATURE_SUCCESS":
            result = (True, "OK")
        else:
            result = (False, responses[0]["errors"])

        return result

    def targets(self):
        """
        Retrieves the target device table from the I3C bus.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either a list of dictionaries, or an error message detailing the failure,
                obtained from the device's response.
                Each dictionary entry contains formatted information about the device, including:
                - 'static_address': The static address in hexadecimal format.
                - 'dynamic_address': The dynamic address in hexadecimal format.
                - 'bcr': The Bus Characteristics Register value.
                - 'dcr': The Device Characteristics Register.
                - 'pid': Unique ID (Provisional ID) containing a manufacturer ID, a part ID and an instance ID.
        """

        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cGetTargetDeviceTable(id, None)
        ])

        # Note: Borrowed from MissionControlBridge's Supernova Adaptor
        targets = []
        for target_info in responses[0]["table"]:
            static_address = target_info["staticAddress"]
            dynamic_address = target_info["dynamicAddress"]
            bcr = target_info["bcr"]["value"][2]
            dcr = target_info["dcr"]
            pid = target_info["pid"][::-1] # Reversing using list slicing
            formatted_target_info = {
                "static_address" : f"{static_address:02X}",
                "dynamic_address" : f"{dynamic_address:02X}",
                "bcr" : bcr[2:4],
                "dcr" : f"{dcr:02X}",
                "pid" : [f"{num:02X}" for num in pid]
            }

            targets.append(formatted_target_info)

        status = responses[0]["errors"][0]
        if status == "NO_TRANSFER_ERROR":
            result = (True, "OK")
        else:
            result = (False, responses[0]["errors"])

        return result

    def toggle_ibi(self, target_address, enable: bool):
        """
        Toggles the In-Band Interrupt (IBI) feature for a specified target device on the I3C bus.

        This method either enables or disables the IBI feature for the device at the given address,
        based on the 'enable' flag.

        Args:
        target_address: The address of the target device on the I3C bus. This should be a valid address
                        corresponding to a device connected to the bus.
        enable (bool, optional): A flag indicating whether to enable (True) or disable (False) the IBI
                                feature.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either the string "OK" indicating success, or an error message
                detailing the failure, obtained from the controller's response.
        """
        if enable:
            responses = self.controller.sync_submit([
                lambda id: self.driver.i3cSetFeature(id, I3cSetFeatureSelector.REGULAR_IBI, target_address)
            ])
        else:
            responses = self.controller.sync_submit([
                lambda id: self.driver.i3cClearFeature(id, I3cClearFeatureSelector.REGULAR_IBI, target_address)
            ])

        status = responses[0]["result"]
        if status == "I3C_SET_FEATURE_SUCCESS" or status == "I3C_CLEAR_FEATURE_SUCCESS":
            result = (True, "OK")
        else:
            result = (False, responses[0]["errors"])

        return result

    def target_update_address(self, current_address, new_address):
        """
        Updates the dynamic address of a target device on the I3C bus.

        This method sends a command to the target device to change its dynamic address from a current
        address to a new address. It checks the operation's success status and returns a tuple
        indicating whether the operation was successful and either a confirmation message or error details.

        Args:
        current_address: The current dynamic address of the target device. This should be the address
                        that the device is currently using on the I3C bus.
        new_address: The new dynamic address to be assigned to the target device. This is the address
                    that the device will use on the I3C bus after successful execution of this command.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either the string "OK" indicating success, or an error message
                detailing the failure, obtained from the controller's response.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cChangeDynamicAddress(id, current_address, new_address)
        ])

        status = responses[0]["errors"][0]
        if status == "NO_TRANSFER_ERROR":
            result = (True, "OK")
        else:
            result = (False, responses[0]["errors"])

        return result

    def _process_response(self, command_name, responses, extra_data=None):
        def format_response_payload(command_name, response):
            match command_name:
                case "write" | "read": return response["data"]
                case "ccc_GETBCR": return response["bcr"]["value"][2][2:].upper()

            return None

        response = responses[0]
        if response["header"]["result"] == "I3C_TRANSFER_SUCCESS":
            data = format_response_payload(command_name, response)
            result_data = {"data": data, "length": response["descriptor"]["dataLength"]}
            if extra_data:
                result_data.update(extra_data)
            result = (True, result_data)
        else:
            result = (False, response["descriptor"]["errors"][0])
        return result

    def write(self, target_address, mode: TransferMode, subaddress: [], buffer: list):
        """
        Performs a write operation to a target device on the I3C bus.

        This method sends data to the specified target device. It includes various parameters like the target
        address, transfer mode, and data to be written. It checks the operation's success status and returns
        a tuple indicating whether the operation was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus to which data is to be written.
        mode (TransferMode): The transfer mode to be used for the write operation. This should be an instance
                            of the TransferMode enum, indicating the desired transfer mode.
        subaddress (list): A list of integers representing the subaddress to be used in the write operation.
        buffer (list): A list of data bytes to be written to the target device.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either a dictionary containing the data written and its length, indicating
                success, or an error message detailing the failure.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cWrite(
                id,
                target_address,
                mode,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
                subaddress,
                buffer,
            )
        ])
        return self._process_response("write", responses)

    def read(self, target_address, mode: TransferMode, subaddress: [], length):
        """
        Performs a read operation from a target device on the I3C bus.

        This method reads data from the specified target device using a given transfer mode, subaddress,
        and expected length of data. It sends the appropriate command to the controller and processes the
        response, returning either the successfully read data or an error message.

        Args:
        target_address: The address of the target device on the I3C bus from which data is to be read.
        mode (TransferMode): The transfer mode to be used for the read operation. This should be an instance
                            of the TransferMode enum, indicating the desired transfer mode.
        subaddress (list): A list of integers representing the subaddress to be used in the read operation.
        length (int): The expected length of data to be read from the device, specified as an integer.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either a dictionary containing the read data and its length, indicating
                success, or an error message detailing the failure.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cRead(
                id,
                target_address,
                mode,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
                subaddress,
                length,
            )
        ])
        return self._process_response("read", responses)

    def ccc_GETBCR(self, target_address):
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cGETBCR(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])
        return self._process_response("ccc_GETBCR", responses)

    def ccc_GETDCR(self, target_address):
        """
        Performs a GETDCR (Get Device Characteristics Register) operation on a target device on the I3C bus.

        This method requests the Device Characteristics Register (DCR) data from the specified target device.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus from which the DCR data is requested.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either a dictionary containing the DCR data and its length, indicating
                success, or an error message detailing the failure.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cGETDCR(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_GETDCR", responses)

    def ccc_GETPID(self, target_address):
        """
        Performs a GETPID (Get Provisional ID) operation on a target device on the I3C bus.

        This method requests the Provisional ID (PID) data from the specified target device.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus from which the PID data is requested.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either a dictionary containing the PID data and its length, indicating
                success, or an error message detailing the failure.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cGETPID(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_GETPID", responses)

    def ccc_GETACCCR(self, target_address):
        """
        Performs a GETACCCR (Get Acceptable Command Codes Register) operation on a target device on the I3C bus.

        This method requests the Acceptable Command Codes Register (ACCCR) data from the specified target device.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus from which the ACCCR data is requested.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either a dictionary containing the ACCCR data and its length, indicating
                success, or an error message detailing the failure.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cGETACCCR(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_GETACCCR", responses)

    def ccc_GETMXDS(self, target_address):
        """
        Performs a GETMXDS (Get Max Data Speed) operation on a target device on the I3C bus.

        This method requests the Maximum Data Speed information from the specified target device.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus from which the Max Data Speed information is requested.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either a dictionary containing the Max Data Speed information and its length, indicating
                success, or an error message detailing the failure.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cGETMXDS(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_GETMXDS", responses)

    def ccc_GETMRL(self, target_address):
        """
        Performs a GETMRL (Get Maximum Read Length) operation on a target device on the I3C bus.

        This method requests the Maximum Read Length information from the specified target device.
        The success of the operation is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus from which the Max Read Length information is requested.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either a dictionary containing the Max Read Length information and its length, indicating
                success, or an error message detailing the failure.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cGETMRL(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_GETMRL", responses)

    def ccc_GETMWL(self, target_address):
        """
        Performs a GETMWL (Get Maximum Write Length) operation on a target device on the I3C bus.

        This method requests the Maximum Write Length information from the specified target device.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus from which the Maximum Write Length information is requested.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either a dictionary containing the Maximum Write Length information and its length, indicating
                success, or an error message detailing the failure.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cGETMWL(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_GETMWL", responses)

    def ccc_GETXTIME(self, target_address):
        """
        Performs a GETXTIME (Get Extra Timing Information) operation on a target device on the I3C bus.

        This method requests the Extra Timing Information from the specified target device.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus from which the Extra Timing Information is requested.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either a dictionary containing the Extra Timing Information and its length, indicating
                success, or an error message detailing the failure.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cGETXTIME(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_GETXTIME", responses)

    def ccc_GETCAPS(self, target_address):
        """
        Performs a GETCAPS (Get Capabilities) operation on a target device on the I3C bus.

        This method requests the Capabilities information from the specified target device.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus from which the Capabilities information is requested.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either a dictionary containing the Capabilities information and its length, indicating
                success, or an error message detailing the failure.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cGETCAPS(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_GETCAPS", responses)

    def ccc_RSTDAA(self, target_address):
        """
        Performs a RSTDAA (Reset Dynamic Address Assignment) operation on a target device on the I3C bus.

        This method initiates a Reset Dynamic Address Assignment process on the specified target device.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus on which the RSTDAA process is initiated.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Since RSTDAA does not typically return data, only success or failure is indicated.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cRSTDAA(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_RSTDAA", responses)

    def ccc_broadcast_ENEC(self):
        """
        Performs a broadcast ENEC (Enable Events Command) operation on the I3C bus.

        This method sends a broadcast command to enable events on all devices on the I3C bus.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Since this is a broadcast command, no specific data is expected in return.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cBroadcastENEC(
                id,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        # Note: The command name 'ccc_broadcast_ENEC' should be handled appropriately in _process_response
        return self._process_response("ccc_broadcast_ENEC", responses)

    def ccc_broadcast_DISEC(self):
        """
        Performs a broadcast DISEC (Disable Events Command) operation on the I3C bus.

        This method sends a broadcast command to disable events on all devices on the I3C bus.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Since this is a broadcast command, no specific data is expected in return.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cBroadcastDISEC(
                id,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        # Note: The command name 'ccc_broadcast_DISEC' should be handled appropriately in _process_response
        return self._process_response("ccc_broadcast_DISEC", responses)

    def ccc_unicast_ENEC(self, target_address):
        """
        Performs a unicast ENEC (Enable Events Command) operation on a specific target device on the I3C bus.

        This method sends a command to enable events on a specific target device identified by its address.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus to which the ENEC command is directed.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cDirectENEC(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_unicast_ENEC", responses)

    def ccc_unicast_DISEC(self, target_address):
        """
        Performs a unicast DISEC (Disable Events Command) operation on a specific target device on the I3C bus.

        This method sends a command to disable events on a specific target device identified by its address.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus to which the DISEC command is directed.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cDirectDISEC(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_unicast_DISEC", responses)

    def ccc_SETDASA(self, static_address, dynamic_address):
        """
        Performs a SETDASA (Set Dynamic Address for Static Address) operation on the I3C bus.

        This method sets a dynamic address for a device with a known static address.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        static_address: The static address of the target device on the I3C bus.
        dynamic_address: The dynamic address to be assigned to the target device.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cSETDASA(
                id,
                static_address,
                dynamic_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_SETDASA", responses)

    def ccc_SETNEWDA(self, current_address, new_address):
        """
        Performs a SETNEWDA (Set New Dynamic Address) operation on the I3C bus.

        This method updates the dynamic address of a device currently on the I3C bus.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        current_address: The current dynamic address of the target device on the I3C bus.
        new_address: The new dynamic address to be assigned to the target device.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cSETNEWDA(
                id,
                current_address,
                new_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_SETNEWDA", responses)

    def ccc_unicast_SETGRPA(self, target_address):
        """
        Performs a unicast SETGRPA (Set Group Address) operation on a specific target device on the I3C bus.

        This method sends a command to set the group address of a specific target device identified by its address.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus to which the SETGRPA command is directed.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cDirectSETGRPA(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_unicast_SETGRPA", responses)

    def ccc_unicast_RSTGRPA(self, target_address):
        """
        Performs a unicast RSTGRPA (Reset Group Address) operation on a specific target device on the I3C bus.

        This method sends a command to reset the group address of a specific target device identified by its address.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus to which the RSTGRPA command is directed.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cDirectRSTGRPA(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_unicast_RSTGRPA", responses)

    def ccc_unicast_SETMRL(self, target_address, max_read_length):
        """
        Performs a unicast SETMRL (Set Maximum Read Length) operation on a specific target device on the I3C bus.

        This method sends a command to set the maximum read length for a specific target device identified by its address.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus to which the SETMRL command is directed.
        max_read_length: The maximum read length to be set for the target device.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cDirectSETMRL(
                id,
                target_address,
                max_read_length,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_unicast_SETMRL", responses)

    def ccc_unicast_SETMWL(self, target_address, max_write_length):
        """
        Performs a unicast SETMWL (Set Maximum Write Length) operation on a specific target device on the I3C bus.

        This method sends a command to set the maximum write length for a specific target device identified by its address.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus to which the SETMWL command is directed.
        max_write_length: The maximum write length to be set for the target device.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cDirectSETMWL(
                id,
                target_address,
                max_write_length,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_unicast_SETMWL", responses)

    def ccc_broadcast_SETMWL(self, max_write_length):
        """
        Performs a broadcast SETMWL (Set Maximum Write Length) operation on the I3C bus.

        This method sends a broadcast command to set the maximum write length for all devices on the I3C bus.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        max_write_length: The maximum write length to be set for all devices on the I3C bus.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cBroadcastSETMWL(
                id,
                max_write_length,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_broadcast_SETMWL", responses)

    def ccc_broadcast_SETMRL(self, max_read_length):
        """
        Performs a broadcast SETMRL (Set Maximum Read Length) operation on the I3C bus.

        This method sends a broadcast command to set the maximum read length for all devices on the I3C bus.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        max_read_length: The maximum read length to be set for all devices on the I3C bus.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cBroadcastSETMWL(
                id,
                max_read_length,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_broadcast_SETMRL", responses)

    def ccc_SETAASA(self):
        """
        Performs a broadcast SETAASA (Set All Agents to Static Address) operation on the I3C bus.

        This method sends a broadcast command to set all agents on the I3C bus to a static address.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cSETAASA(
                id,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_SETAASA", responses)

    def ccc_broadcast_ENDXFED(self):
        """
        Performs a broadcast ENDXFED (End Extra Fast-Mode Device Exchange) operation on the I3C bus.

        This method sends a broadcast command to signal the end of an extra fast-mode data exchange period on all devices on the I3C bus.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cBroadcastENDXFED(
                id,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_broadcast_ENDXFED", responses)

    def ccc_unicast_ENDXFER(self, target_address):
        """
        Performs a unicast ENDXFER (End Transfer) operation on a specific target device on the I3C bus.

        This method sends a command to end a data transfer operation for a specific target device identified by its address.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        target_address: The address of the target device on the I3C bus to which the ENDXFER command is directed.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cDirectENDXFER(
                id,
                target_address,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_unicast_ENDXFER", responses)

    def ccc_broadcast_SETXTIME(self, timing_parameter):
        """
        Performs a broadcast SETXTIME (Set Extra Timing) operation on the I3C bus.

        This method sends a broadcast command to configure extra timing parameters for all devices on the I3C bus.
        The operation's success status is checked, and it returns a tuple indicating whether the operation
        was successful along with the relevant data or error message.

        Args:
        timing_parameter: The extra timing parameter to be set for all devices on the I3C bus.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cBroadcastSETXTIME(
                id,
                timing_parameter,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_broadcast_SETXTIME", responses)

    def ccc_unicast_SETXTIME(self, target_address):
        pass

    def ccc_broadcast_SETBUSCON(self, context: int, data: list = []):
        """
        Performs a broadcast SETBUSCON (Set Bus Configuration) operation on the I3C bus.

        This method sends a broadcast command to set a particular context on the bus, which could be a higher-level protocol
        specification or a version of the MIPI I3C Specification. This context is used to activate special functionalities
        required to support the selected protocol on the bus.

        Args:
        context: An integer representing the context for the bus configuration. This could indicate a higher-level
                 protocol or a specific version of the MIPI I3C Specification.
        data: An optional list of data items relevant to the bus configuration.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message.
              Specific data is usually not returned in this operation, only the success or failure status.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cBroadcastSETBUSCON(
                id,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
                context,
                data
            )
        ])

        return self._process_response("ccc_broadcast_SETBUSCON", responses)

    def ccc_broadcast_ENTAS0(self):
        """
        Performs a broadcast ENTAS0 (Enter Activity State 0) operation on the I3C bus.

        This method sends a broadcast command to inform all devices on the I3C bus to enter Activity State 0,
        where the bus is expected to be idle for 1 microsecond (us). It is part of an activity state series
        (ENTAS0 to ENTAS3) that devices can use for power management, specifically to manage low power states during idle periods.

        The ENTAS0 command acts as a suggestion rather than a directive, allowing devices to prepare for a
        low-power state without overriding any specific or custom power-saving agreements that might be
        implemented at the application level.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message,
              reflecting the broadcast command's attempt to set the bus to the specified idle time.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cBroadcastENTAS0(
                id,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_broadcast_ENTAS0", responses)

    def ccc_broadcast_ENTAS1(self):
        """
        Sends a broadcast ENTAS1 command to all devices on the I3C bus, indicating that the bus will enter
        an idle state for 100 microseconds (us). This command is part of power management strategies to
        reduce power consumption during known periods of inactivity.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message,
              reflecting the broadcast command's attempt to set the bus to the specified idle time.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cBroadcastENTAS1(
                id,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_broadcast_ENTAS1", responses)

    def ccc_broadcast_ENTAS2(self):
        """
        Sends a broadcast ENTAS2 command to all devices on the I3C bus, indicating that the bus will enter
        an idle state for 2 milliseconds (ms). This command is part of power management strategies to
        reduce power consumption during known periods of inactivity.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message,
              reflecting the broadcast command's attempt to set the bus to the specified idle time.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cBroadcastENTAS2(
                id,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_broadcast_ENTAS2", responses)

    def ccc_broadcast_ENTAS3(self):
        """
        Sends a broadcast ENTAS3 command to all devices on the I3C bus, indicating that the bus will enter
        an idle state for 50 milliseconds (ms). This command is part of power management strategies to
        reduce power consumption during known periods of inactivity.

        Returns:
        tuple: A tuple containing two elements:
            - The first element is a Boolean indicating the success (True) or failure (False) of the operation.
            - The second element is either an error message detailing the failure or a success message,
              reflecting the broadcast command's attempt to set the bus to the specified idle time.
        """
        responses = self.controller.sync_submit([
            lambda id: self.driver.i3cBroadcastENTAS3(
                id,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
            )
        ])

        return self._process_response("ccc_broadcast_ENTAS3", responses)
