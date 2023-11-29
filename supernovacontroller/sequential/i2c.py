from transfer_controller import TransferController
from BinhoSupernova.Supernova import Supernova
from supernovacontroller.errors import BackendError


class SupernovaI2CBlockingInterface:
    def __init__(self, driver: Supernova, controller: TransferController):
        self.driver = driver
        self.controller = controller

    def set_parameters(self, voltage: int, rate: int = 1000000):
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.setI2cSpiUartBusVoltage(transfer_id, voltage),
                lambda transfer_id: self.driver.i2cSetParameters(transfer_id, baudrate=rate),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_ok = responses[0]["name"] == "SET I2C-SPI-UART BUS VOLTAGE" and responses[0]["result"] == 0 and responses[1]["name"] == "I2C SET PARAMETERS" and responses[1]["completed"] == 0
        if response_ok:
            result = (True, (voltage, rate))
        else:
            result = (False, "Set bus voltage or  failed")

        return result

    def write(self, address, register, data):
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

    def write_non_stop(self, address, register, data):
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.i2cWriteNonStop(transfer_id, address, register, data),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_ok = responses[0]["name"] == "I2C WRITE WITHOUT STOP" and responses[0]["status"] == 0
        if response_ok:
            result = (True, None)
        else:
            result = (False, None)

        return result

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
