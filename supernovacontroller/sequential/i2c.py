from transfer_controller import TransferController
from BinhoSupernova.Supernova import Supernova


class SupernovaI2CBlockingInterface:
    def __init__(self, device: Supernova, controller: TransferController):
        self.device = device
        self.controller = controller

    def set_parameters(self, voltage: float, rate: int = 1000000):
        voltage_int = voltage * 1000
        result = self.controller.sync_submit([
            lambda transfer_id: self.device.setI2cSpiUartBusVoltage(transfer_id, voltage_int),
            lambda transfer_id: self.device.i2cSetParameters(transfer_id, baudrate=rate),
        ])

        return result

    def write(self, address, register, data):
        result = self.controller.sync_submit([
            lambda transfer_id: self.device.i2cWrite(transfer_id, address, register, data),
        ])

        return result

    def write_non_stop(self, address, register, data):
        responses = self.controller.sync_submit([
            lambda transfer_id: self.device.i2cWriteNonStop(transfer_id, address, register, data),
        ])

        return responses

    def read(self, address, length):
        responses = self.controller.sync_submit([
            lambda transfer_id: self.device.i2cRead(transfer_id, address, length),
        ])

        return responses

    def read_from(self, address, register, length):
        responses = self.controller.sync_submit([
            lambda transfer_id: self.device.i2cReadFrom(transfer_id, address, register, length),
        ])

        return responses
