from deviceSimulators.targetDevices.I2cTargetMemory import I2cTargetMemory

class BinhoNovaSimulator:
    def __init__(self, port):
        self.inBootloaderMode = False
        self.inDAPLinkMode = False
        self.deviceID = "BINHONOVASIM001"
        self.commPort = "NovaSimulatedPort"
        self.productName = "Binho Nova"
        self.firmwareVersion = "0.2.8"
        self.hardwareVersion = "1.0"
        self.operationMode = ""
        self.useInternalPullUps = False
        self.frequency = "0"
        self.gpio_pins = {
            "IO0": self.gpio.gpioPin(0),
            "IO1": self.gpio.gpioPin(1),
            "IO2": self.gpio.gpioPin(2),
            "IO3": self.gpio.gpioPin(3),
            "IO4": self.gpio.gpioPin(4),
        }
        self.gpio = self.gpio()
        self.i2c = self.i2c()
        self.spi = self.spi()
        self.oneWire = self.oneWire()

    def close(self):
        self.releaseAllPins()
        return {}
    
    def releaseAllPins(self):
        # Used before changing operationMode to neutralize
        # the logic of operationMode that tries to mark
        # some pins as used and throws an error
        # See:
        # - https://github.com/binhollc/MissionControl2/issues/241
        # - https://github.com/binhollc/binho-python-package/blob/21ea73b03755c4205e93525ed24b4becba23c93e/binho/devices/nova.py#L73
        self.gpio.markPinAsUnused("IO0")
        self.gpio.markPinAsUnused("IO1")
        self.gpio.markPinAsUnused("IO2")
        self.gpio.markPinAsUnused("IO3")
        self.gpio.markPinAsUnused("IO4")

    class gpio:
        def __init__(self):
            self.pinsInUse = [False, False, False, False, False]

        def markPinAsUnused(self, pinString):
            if pinString[0:2] == "IO":
                pinNumber = int(pinString[2])
                self.pinsInUse[pinNumber] = False

        class gpioPin:
            def __init__(self, pinID):
                self.mode = ""
                self._value = "0"
                self.pwmFreq = 0
                self.pin = pinID
            
            @property
            def value(self):
                if self.mode == "DIN":
                    self._value = 1 if (self.pin % 2) else 0
                if self.mode == "AIN":
                    self._value = 3.3 if (self.pin % 2) else 0
                return self._value
            
            @value.setter
            def value(self, newval):
                pass

    class i2c:
        def __init__(self):
            self.availableAdresses = list([80, 81, 82, 83])
            self.mems = {
                "80" : I2cTargetMemory(80),
                "81" : I2cTargetMemory(81),
                "82" : I2cTargetMemory(82),
                "83" : I2cTargetMemory(83)}

        def scan(self):
            return self.availableAdresses
        
        def write(self, address, writeBuffer):
            self.mems[str(address)].write(writeBuffer)
            pass

        def read(self, address, bytesToRead):
            return self.mems[str(address)].read(bytesToRead)
        
        def transfer(self, address, subaddress, bytesToRead):
            self.mems[str(address)].write(subaddress, forceSetSubaddres = True)
            return self.mems[str(address)].read(bytesToRead)

    class spi:
        def __init__(self):
            self.mode = 0
            self.frequency = 2000000
            self.bitOrder = "MSBFIRST"
            self.bitsPerTransfer = 8

        def autoCSConfig(self, cs_pin, polarity, pre_delay, post_delay):
            return
        
        def transfer(self, writeBuffer, bytesToRead):
            if bytesToRead > len(writeBuffer):
                result = [0]*bytesToRead
                for i in range(len(writeBuffer)):
                    result[i] = writeBuffer[i]
            else:
                result = writeBuffer[0:bytesToRead]
            return bytes(result)
        
    class oneWire:
        def __init__(self):
            self.channel = 0
            self.internalPullUpResistors = False
            self.availableDeviceId = [45, 92, 29, 206, 176, 7, 16, 173]
            self.oneWireDevice = self.oneWireDevice(self.availableDeviceId, 200)

        def begin(self, channel, internalPullUpResistors):
            self.channel = channel
            self.internalPullUpResistors = internalPullUpResistors

        def search(self):
            return self.availableDeviceId
        
        def write(self, writeBuffer, command):
            self.oneWireDevice.write(writeBuffer)
        
        def read(self, bytesToRead, command):
            return self.oneWireDevice.read(bytesToRead)

        def transfer(self, writeBuffer, bytesToRead, command):
            self.oneWireDevice.write(writeBuffer)
            return self.oneWireDevice.read(bytesToRead)

        class oneWireDevice:
            def __init__(self, address, memSize):
                self.address = address
                self.memSize = memSize
                self.memory = [0]*memSize

            def write(self, writeBuffer):
                for i in range(len(writeBuffer)):
                    self.memory[i] = writeBuffer[i]
            
            def read(self, bytesToRead):
                if bytesToRead > self.memSize:
                    return [0]
                return self.memory[0 : bytesToRead]
