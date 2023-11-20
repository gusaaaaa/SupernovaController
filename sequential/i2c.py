from transfer_controller import TransferController
from BinhoSupernova.Supernova import Supernova


class SupernovaI2CBlockingInterface:
    def __init__(self, device: Supernova, controller: TransferController):
        self.device = device
        self.controller = controller

    def set_parameters(self):
        result = self.controller.sync_submit([
            lambda transfer_id: self.device.setI2cSpiUartBusVoltage(transfer_id, 3300),
            lambda transfer_id: self.device.i2cSetParameters(transfer_id, baudrate=1000000),
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
