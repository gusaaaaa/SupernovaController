from transfer_controller import TransferController
from BinhoSupernova.Supernova import Supernova
from supernovacontroller.errors import BackendError


class SupernovaI2CBlockingInterface:
    def __init__(self, driver: Supernova, controller: TransferController):
        self.driver = driver
        self.controller = controller

    def set_parameters(self, voltage: float, rate: int = 1000000):
        voltage_int = voltage * 1000
        try:
            result = self.controller.sync_submit([
                lambda transfer_id: self.driver.setI2cSpiUartBusVoltage(transfer_id, voltage_int),
                lambda transfer_id: self.driver.i2cSetParameters(transfer_id, baudrate=rate),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        return result

    def write(self, address, register, data):
        try:
            result = self.controller.sync_submit([
                lambda transfer_id: self.driver.i2cWrite(transfer_id, address, register, data),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        return result

    def write_non_stop(self, address, register, data):
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.i2cWriteNonStop(transfer_id, address, register, data),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        return responses

    def read(self, address, length):
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.i2cRead(transfer_id, address, length),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        return responses

    def read_from(self, address, register, length):
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.i2cReadFrom(transfer_id, address, register, length),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        return responses
