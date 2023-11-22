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

    def init_bus(self, voltage: float):
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

    def target_config(self, target_address, config):
        pass

    def target_reset(self, target_address, def_byte, rw: TransferDirection):
        # Get parameters from self.push_pull_clock_freq_mhz and self.open_drain_clock_freq_mhz
        pass

    def write(self, target_address, mode: TransferMode, subaddress: [], buffer: list):
        # Get parameters from self.push_pull_clock_freq_mhz and self.open_drain_clock_freq_mhz
        pass

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

