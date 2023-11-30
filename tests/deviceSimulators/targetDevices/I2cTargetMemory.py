       
from deviceSimulators.targetDevices.simpleSimulatedMemory import simpleSimulatedMemory

class I2cTargetMemory:
    def __init__(self, address):
        self.memModule = simpleSimulatedMemory(subaddressSize = 2)
        self.address = address

    def write(self, writeBuffer, forceSetSubaddres = False):
        self.memModule.write(writeBuffer, forceSetSubaddres)

    def read(self, bytesToRead):
        return self.memModule.read(bytesToRead)
