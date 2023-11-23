from .targetDevices.I3cTargetMemory import I3cTargetMemory
from .targetDevices.I2cTargetMemory import I2cTargetMemory
from .targetDevices.SimulatedP3T1085UK import SimulatedP3T1085UK


class BinhoSupernovaSimulator:
    def __init__(self):
        self.usbStrings = {
            "MANUFACTURER": "MN-Binho LLC",
            "PRODUCT_NAME": "PR-Binho Supernova",
            "SERIAL_NUMBER": "SN-00000000000000000000000000000",
            "HW_VERSION": "HW-6",
            "FW_VERSION": "FW-1.1.0",
            "BL_VERSION": "BL-1.0.1"
        }
        self.i2cTargets = {
            "80": I2cTargetMemory(address=80),
            "81": I2cTargetMemory(address=81),
            "82": I2cTargetMemory(address=82),
        }
        self.i3cTargets = {
            "80": I3cTargetMemory(staticAddress=80),
            "81": I3cTargetMemory(staticAddress=81),
            "82": I3cTargetMemory(staticAddress=82),
            "83": SimulatedP3T1085UK(staticAddress=83),
        }
        self.i3cTargetTable = {}

    def onEvent(self, callback):
        self.callback = callback

    def open(self, path, activateLogger):
        pass

    def close(self):
        pass

    def setI2cSpiUartBusVoltage(self, id, i2cSpiUartBusVolt):
        self.callback({
            "id": id,
            "command": 100,
            "name": "SET I2C-SPI-UART BUS VOLTAGE",
            "result": 0,
        }, None)

    # I2C management --------------------------------------------------------------------

    def i2cSetParameters(self, id: int, cancelTransfer = 0x00, baudrate = 0x00):
        self.callback({
            "id": id,
            "command": 33,
            "name": "I2C SET PARAMETERS",
            "completed": 0,
            "cancelTransfer": cancelTransfer,
            "baudrate": 32,
            "divider": 27
        }, None)

    def i2cWrite(self, id: int, slaveAddress : int, registerAddress: list, data: list):
        if len(registerAddress) == 0:
            self.i2cTargets[str(slaveAddress)].write(data)
        else:
            self.i2cTargets[str(slaveAddress)].write(registerAddress + data)
        self.callback({
            "id": id,
            "command": 34,
            "name": "I2C WRITE",
            "status": 0,
            "payloadLength": len(data),
            "payload": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }, None)

    def i2cWriteNonStop(self, id: int, slaveAddress : int, registerAddress: list, data: list):
        pass

    def i2cRead(self, id: int, slaveAddress: int, requestDataLength: int):
        data = self.i2cTargets[str(slaveAddress)].read(requestDataLength)
        self.callback({
            "id": id,
            "command": 35,
            "name": "I2C READ",
            "status": 0,
            "payloadLength": requestDataLength,
            "data": data
        }, None)


    def i2cReadFrom(self, id: int, slaveAddress: int, registerAddress: list, requestDataLength: int):
        self.i2cTargets[str(slaveAddress)].write(registerAddress)
        data = self.i2cTargets[str(slaveAddress)].read(requestDataLength)
        self.callback({
            "id": id,
            "command": 39,
            "name": "I2C READ FROM",
            "status": 0,
            "payloadLength": requestDataLength,
            "data": data
        }, None)

    # I3C management --------------------------------------------------------------------

    def helperGetStaticFromDynamicAddress(self, targetAddress):
        return self.i3cTargetTable[str(targetAddress)]["staticAddress"]
    
    def helperGetDeviceInfoFromDynamicAddress(self, targetAddress):
        staticAddress = self.helperGetStaticFromDynamicAddress(targetAddress)
        return self.i3cTargets[str(staticAddress)].getDeviceInfo()

    def getI3cTransferResponseTemplate(self, id, dataLength):
        return {
            "id": id,
            "command": 12,
            "name": "I3C TRANSFER",
            "header": {
                "tag": "RESPONSE_TO_REGULAR_REQUEST",
                "result": "I3C_TRANSFER_SUCCESS",
                "hasData": True
            },
            "descriptor": {
                "dataLength": dataLength,
                "errors": ["NO_TRANSFER_ERROR"]
            },
        }

    def setI3cBusVoltage(self, id, i3cBusVoltage):
        self.callback({
            "id": id,
            "command": 97,
            "name": "SET I3C BUS VOLTAGE",
            "result": 0
        }, None)

    def getUsbString(self, id, subCommand):
        subCommandName = str(subCommand.name)
        message = self.usbStrings[subCommandName]
        messageLength = len(message)
        self.callback({
            "id": id,
            "command": 96,
            "name": "GET USB STRING",
            "length": messageLength,
            "message": message
        }, None)

    def i3cInitBus(self, id, targetDeviceTable):
        dynamicAddress = 8
        for address, memory in self.i3cTargets.items():
            memory.setDynamicAddress(dynamicAddress)
            self.i3cTargetTable[str(dynamicAddress)] = memory.getDeviceInfo()
            dynamicAddress += 1

        self.callback({
            "id": id,
            "command": 5,
            "name": "I3C INIT BUS",
            "result": "I3C_BUS_INIT_SUCCESS",
            "errors": ["NO_TRANSFER_ERROR"]
        }, None)

    def i3cClearFeature(self, id, selector, targetAddress):
        if (targetAddress == 0x7E and selector.name == "I3C_BUS"):
            self.i3cTargetTable = {}
            self.callback({
                "id": id,
                "command": 1,
                "name": "I3C CLEAR FEATURE",
                "result": "I3C_CLEAR_FEATURE_SUCCESS",
                "errors": ["NO_TRANSFER_ERROR"]
            }, None)

    def i3cGetTargetDeviceTable(self, id):
        table = []
        for address, memory in self.i3cTargetTable.items():
            table.append(self.i3cTargetTable[address])
        self.callback({
            "id": id,
            "command": 6,
            "name": "I3C GET TARGET DEVICE TABLE",
            "numberOfTargets": len(table),
            "table": table
        }, None)

    def i3cWrite(self, id, targetAddress, mode, pushPullRate, openDrainRate, registerAddress, data):
        staticAddress = self.i3cTargetTable[str(targetAddress)]["staticAddress"]
        self.i3cTargets[str(staticAddress)].write(registerAddress + data)
        self.callback({
            "id": id,
            "command": 12,
            "name": "I3C TRANSFER",
            "header": {
                "tag": "RESPONSE_TO_REGULAR_REQUEST",
                "result": "I3C_TRANSFER_SUCCESS",
                "hasData": False
            },
            "descriptor": {
                "dataLength": 0,
                "errors": ["NO_TRANSFER_ERROR"]
            },
            "data": []
        }, None)

    def i3cRead(self, id, targetAddress, mode, pushPullRate, openDrainRate, registerAddress, length):
        staticAddress = self.i3cTargetTable[str(targetAddress)]["staticAddress"]
        if (len(registerAddress) > 0):
            self.i3cTargets[str(staticAddress)].write(registerAddress)
        data = self.i3cTargets[str(staticAddress)].read(length)
        self.callback({
            "id": id,
            "command": 12,
            "name": "I3C TRANSFER",
            "header": {
                "tag": "RESPONSE_TO_REGULAR_REQUEST",
                "result": "I3C_TRANSFER_SUCCESS",
                "hasData": True
            },
            "descriptor": {
                "dataLength": length,
                "errors": ["NO_TRANSFER_ERROR"]
            },
            "data": data
        }, None)

    def i3cGETPID(self, id, targetAddress, pushPullRate, openDrainRate):
        staticAddress = self.helperGetStaticFromDynamicAddress(targetAddress)
        deviceInfo = self.i3cTargets[str(staticAddress)].getDeviceInfo()
        pid = list(map(lambda num: hex(num), deviceInfo["pid"]))
        pidlen = len(pid)
        response = self.getI3cTransferResponseTemplate(id, pidlen)
        response["pid"] = pid
        self.callback(response, None)

    def i3cGETBCR(self, id, targetAddress, pushPullRate, openDrainRate):
        staticAddress = self.helperGetStaticFromDynamicAddress(targetAddress)
        deviceInfo = self.i3cTargets[str(staticAddress)].getDeviceInfo()
        bcr = deviceInfo["bcr"]
        bcrlen = 1
        response = self.getI3cTransferResponseTemplate(id, bcrlen)
        response["bcr"] = bcr
        self.callback(response, None)

    def i3cGETDCR(self, id, targetAddress, pushPullRate, openDrainRate):
        staticAddress = self.helperGetStaticFromDynamicAddress(targetAddress)
        deviceInfo = self.i3cTargets[str(staticAddress)].getDeviceInfo()
        dcr = hex(deviceInfo["dcr"])
        dcrlen = 1
        response = self.getI3cTransferResponseTemplate(id, dcrlen)
        response["dcr"] = dcr
        self.callback(response, None)

    def i3cGETMRL(self, id, targetAddress, pushPullRate, openDrainRate):
        staticAddress = self.helperGetStaticFromDynamicAddress(targetAddress)
        mrl = self.i3cTargets[str(staticAddress)].getMRL()
        response = self.getI3cTransferResponseTemplate(id, 2)
        response["maxReadLength"] = mrl
        self.callback(response, None)

    def i3cDirectSETMRL(self, id, targetAddress, pushPullRate, openDrainRate, mrl):
        staticAddress = self.helperGetStaticFromDynamicAddress(targetAddress)
        self.i3cTargets[str(staticAddress)].setMRL(mrl)
        response = self.getI3cTransferResponseTemplate(id, 2)
        response["data"] = [0, 0]
        self.callback(response, None)

    def i3cBroadcastSETMRL(self, id, pushPullRate, openDrainRate, mrl):
        [target.setMRL(mrl) for target in self.i3cTargets.values()]
        response = self.getI3cTransferResponseTemplate(id, 3)
        response["data"] = [0, 0, 0]
        self.callback(response, None)

    def i3cGETMWL(self, id, targetAddress, pushPullRate, openDrainRate):
        staticAddress = self.helperGetStaticFromDynamicAddress(targetAddress)
        mwl = self.i3cTargets[str(staticAddress)].getMWL()
        response = self.getI3cTransferResponseTemplate(id, 2)
        response["maxWriteLength"] = mwl
        self.callback(response, None)

    def i3cDirectSETMWL(self, id, targetAddress, pushPullRate, openDrainRate, mwl):
        staticAddress = self.helperGetStaticFromDynamicAddress(targetAddress)
        self.i3cTargets[str(staticAddress)].setMWL(mwl)
        response = self.getI3cTransferResponseTemplate(id, 2)
        response["data"] = [0, 0]
        self.callback(response, None)

    def i3cBroadcastSETMWL(self, id, pushPullRate, openDrainRate, mwl):
        [target.setMWL(mwl) for target in self.i3cTargets.values()]
        response = self.getI3cTransferResponseTemplate(id, 3)
        response["data"] = [0, 0, 0]
        self.callback(response, None)
