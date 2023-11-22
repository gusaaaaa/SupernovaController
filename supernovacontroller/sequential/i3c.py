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

    def __init__(self, device: Supernova, controller: TransferController):
        self.device = device
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
            - The second element is either the string "OK" indicating success, or an error message
                detailing the failure, obtained from the device's response.

        Note:
        - The method assumes that the input voltage value is valid and does not perform any validation.
        Users of this method should ensure that the provided voltage value is within acceptable limits.
        """
        responses = self.controller.sync_submit([
            lambda id: self.device.setI3cBusVoltage(id, voltage)
        ])

        status = responses[0]["errors"][0]
        if status == "NO_TRANSFER_ERROR":
            result = (True, "OK")
            # We want to set the bus_voltage when we know the operation was successful
            self.bus_voltage = voltage
        else:
            result = (False, responses[0]["errors"])
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
            lambda id: self.device.i3cInitBus(id, None)
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
            lambda id: self.device.i3cClearFeature(id, I3cClearFeatureSelector.I3C_BUS, self.BROADCAST_ADDRESS)
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
                - 'pid':  Unique ID containing a manufacturer ID, a part ID and an instance ID.
        """

        responses = self.controller.sync_submit([
            lambda id: self.device.i3cGetTargetDeviceTable(id, None)
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
                lambda id: self.device.i3cSetFeature(id, I3cSetFeatureSelector.REGULAR_IBI, target_address)
            ])
        else:
            responses = self.controller.sync_submit([
                lambda id: self.device.i3cClearFeature(id, I3cClearFeatureSelector.REGULAR_IBI, target_address)
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
            lambda id: self.device.i3cChangeDynamicAddress(id, current_address, new_address)
        ])

        status = responses[0]["errors"][0]
        if status == "NO_TRANSFER_ERROR":
            result = (True, "OK")
        else:
            result = (False, responses[0]["errors"])

        return result

    def write(self, target_address, mode: TransferMode, subaddress: [], buffer: list):
        responses = self.controller.sync_submit([
            lambda id: self.device.i3cWrite(
                id,
                target_address,
                mode,
                self.push_pull_clock_freq_mhz,
                self.push_pull_clock_freq_mhz,
                subaddress,
                buffer,
            )
        ])

        response = responses[0]

        if response["header"]["result"] == "I3C_TRANSFER_SUCCESS":
            result = (True, { "data": response["data"], "length": response["descriptor"]["dataLength"] })
        else:
            result = (False, response["errors"])
        
        return result

    def read(self, target_address, mode: TransferMode, subaddress: [], length):
        # Get parameters from self.push_pull_clock_freq_mhz and self.open_drain_clock_freq_mhz
        pass

    def ccc_GETBCR(self, target_address):
        pass

    def ccc_GETDCR(self, target_address):
        pass

    def ccc_GETPID(self, target_address):
        pass

    def ccc_GETACCCR(self, target_address):
        pass

    def ccc_GETMXDS(self, target_address):
        pass

    def ccc_GETMRL(self, target_address):
        pass

    def ccc_GETMWL(self, target_address):
        pass

    def ccc_GETXTIME(self, target_address):
        pass

    def ccc_GETCAPS(self, target_address):
        pass

    def ccc_RSTDAA(self, target_address):
        pass

    def ccc_broadcast_ENEC(self):
        pass

    def ccc_broadcast_DISEC(self):
        pass

    def ccc_unicast_ENEC(self, target_address):
        pass

    def ccc_unicast_DISEC(self, target_address):
        pass

    def ccc_SETDASA(self, static_address, dynamic_address):
        pass

    def ccc_SETNEWDA(self, current_address, new_address):
        pass

    def ccc_unicast_SETGRPA(self, target_address):
        pass

    def ccc_unicast_RSTGRPA(self):
        pass

    def ccc_unicast_SETMRL(self, target_address):
        pass

    def ccc_unicast_SETMWL(self, target_address):
        pass

    def ccc_broadcast_SETMWL(self):
        pass

    def ccc_broadcast_SETMRL(self):
        pass

    def ccc_SETAASA(self):
        pass

    def ccc_broadcast_ENDXFED(self):
        pass

    def ccc_unicast_ENDXFER(self, target_address):
        pass

    def ccc_broadcast_SETXTIME(self):
        pass

    def ccc_unicast_SETXTIME(self, target_address):
        pass

    def ccc_broadcast_SETBUSCON(self):
        pass

    def ccc_broadcast_ENTAS0(self):
        pass

    def ccc_broadcast_ENTAS1(self):
        pass

    def ccc_broadcast_ENTAS2(self):
        pass

    def ccc_broadcast_ENTAS3(self):
        pass


