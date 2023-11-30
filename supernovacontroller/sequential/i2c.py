from transfer_controller import TransferController
from BinhoSupernova.Supernova import Supernova
from supernovacontroller.errors import BackendError
from supernovacontroller.errors import BusVoltageError
from supernovacontroller.errors import BusNotInitializedError


class SupernovaI2CBlockingInterface:
    def __init__(self, driver: Supernova, controller: TransferController):
        self.driver = driver
        self.controller = controller

        self.bus_voltage = None
        self.baud_rate = 1000000

    def set_parameters(self, baud_rate: int = 1000000):
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.i2cSetParameters(transfer_id, baudrate=baud_rate),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_ok = responses[0]["name"] == "I2C SET PARAMETERS" and responses[0]["completed"] == 0
        if response_ok:
            result = (True, baud_rate)
        else:
            result = (False, "Set parameters failed")

        return result

    def get_parameters(self):
        return (True, self.baud_rate)

    def set_bus_voltage(self, voltage: int):
        responses = None
        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.setI2cSpiUartBusVoltage(transfer_id, voltage),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_ok = responses[0]["name"] == "SET I2C-SPI-UART BUS VOLTAGE" and responses[0]["result"] == 0
        if response_ok:
            result = (True, voltage)
            self.bus_voltage = voltage
        else:
            result = (False, "Set bus voltage failed")
            self.bus_voltage = None

        return result

    def init_bus(self, voltage: int=None):
        if voltage is None:
            if self.bus_voltage is None:
                raise BusVoltageError()
            voltage = self.bus_voltage
        else:
            (success, set_bus_voltage_result) = self.set_bus_voltage(voltage)
            if not success:
                return (False, set_bus_voltage_result)

        return (True, self.bus_voltage)

    def write(self, address, register, data):
        if self.bus_voltage is None:
            raise BusNotInitializedError()

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

    def read(self, address, length):
        if self.bus_voltage is None:
            raise BusNotInitializedError()

        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.i2cRead(transfer_id, address, length),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_ok = responses[0]["name"] == "I2C READ" and responses[0]["status"] == 0
        if response_ok:
            result = (True, responses[0]["data"])
        else:
            result = (False, None)

        return result

    def read_from(self, address, register, length):
        if self.bus_voltage is None:
            raise BusNotInitializedError()

        try:
            responses = self.controller.sync_submit([
                lambda transfer_id: self.driver.i2cReadFrom(transfer_id, address, register, length),
            ])
        except Exception as e:
            raise BackendError(original_exception=e) from e

        response_ok = responses[0]["name"] == "I2C READ FROM" and responses[0]["status"] == 0
        if response_ok:
            result = (True, responses[0]["data"])
        else:
            result = (False, None)

        return result
