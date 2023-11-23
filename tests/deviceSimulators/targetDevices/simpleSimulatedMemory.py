
class simpleSimulatedMemory:
    
    def __init__(self, subaddressSize):
        self.subaddressSize = subaddressSize
        self.memSize = pow(2, 8*self.subaddressSize)
        self.memory = [0]*self.memSize
        self.subaddress = 0
        self.subaddressIsSet = False

    def subaddressToInt(self, subaddress):
        subaddressInt = sum(byte << 8 * i for i, byte in enumerate(reversed(subaddress)))
        return subaddressInt

    def write(self, writeBuffer, forceSetSubaddres = False):
        if (forceSetSubaddres):
            self.subaddress = self.subaddressToInt(writeBuffer)
            self.subaddressIsSet = True
            return

        if ((len(writeBuffer) > self.subaddressSize) and (not(self.subaddressIsSet))): 
            self.subaddress = self.subaddressToInt(writeBuffer[0:self.subaddressSize])
            writeBuffer = writeBuffer[self.subaddressSize:]
            self.subaddressIsSet = True
            
        if (self.subaddressIsSet):
            if (self.subaddress + len(writeBuffer) > self.memSize):
                remainingSpace = self.memSize - self.subaddress 
                writeBufferUp = writeBuffer[0:remainingSpace]
                writeBufferDown = writeBuffer[remainingSpace:]
                for i in range(len(writeBufferUp)):
                    self.memory[self.subaddress + i] = writeBufferUp[i]
                for i in range(len(writeBufferDown)):
                    self.memory[i] = writeBufferDown[i]
            else:
                for i in range(len(writeBuffer)):
                    self.memory[self.subaddress + i] = writeBuffer[i]
            self.subaddressIsSet = forceSetSubaddres
        else:
            self.subaddress = self.subaddressToInt(writeBuffer)
            self.subaddressIsSet = True
    
    def read(self, bytesToRead):
        if (self.subaddressIsSet):
            self.subaddressIsSet = False
            if (self.subaddress + bytesToRead > self.memSize):
                remainingSpace = self.memSize - self.subaddress 
                return self.memory[self.subaddress : self.subaddress + remainingSpace] + self.memory[0 : bytesToRead - remainingSpace]
            else:
                return self.memory[self.subaddress : self.subaddress + bytesToRead]
        else:
            return [255]*bytesToRead

