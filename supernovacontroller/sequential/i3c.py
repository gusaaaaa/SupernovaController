from transfer_controller import TransferController
from BinhoSupernova.Supernova import Supernova
from BinhoSupernova.commands.definitions import TransferMode
from BinhoSupernova.commands.definitions import I3cCommandType
from BinhoSupernova.commands.definitions import TransferDirection


class SupernovaI3CBlockingInterface:
    # TODO: Replicate definitions (TransferMode, I3cCommandType, TransferDirection)

    def __init__(self, device: Supernova, controller: TransferController):
        self.device = device
        self.controller = controller

    def set_parameters(self, push_pull_clock_freq_mhz: float, open_drain_clock_freq_mhz: float):
        self.push_pull_clock_freq_mhz = push_pull_clock_freq_mhz
        self.open_drain_clock_freq_mhz = open_drain_clock_freq_mhz

    def set_bus_voltage(self, voltage: float):
        voltage_int = int(1000 * voltage)
        pass

    def init_bus(voltage: float):
        pass

    def reset_bus(self):
        pass

    def enter_boot_mode(self):
        pass

    def targets(self):
        pass

    def get_capability(self):
        # TODO: consider renaming
        pass

    def clear_feature(self, selector, address):
        # TODO: consider renaming
        pass

    def set_feature(self, selector_address):
        # TODO: consider renaming
        pass

    def target_update_address(self, current_address, new_address):
        pass

    def target_config(self, address, config):
        pass

    def target_reset(self, address, def_byte, rw: TransferDirection):
        # Get parameters from self.push_pull_clock_freq_mhz and self.open_drain_clock_freq_mhz
        pass

    def write(self, target_address, mode: TransferMode, subaddress: [], buffer: list):
        # Get parameters from self.push_pull_clock_freq_mhz and self.open_drain_clock_freq_mhz
        pass

    def read(self, address, mode: TransferMode, subaddress: [], length):
        # Get parameters from self.push_pull_clock_freq_mhz and self.open_drain_clock_freq_mhz
        pass

    # Continue...