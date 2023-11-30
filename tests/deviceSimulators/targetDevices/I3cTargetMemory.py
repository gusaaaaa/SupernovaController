from deviceSimulators.targetDevices.simpleSimulatedMemory import simpleSimulatedMemory


class I3cTargetMemory:
    def __init__(self, staticAddress):
        self.subaddressSize = 2
        self.memModule = simpleSimulatedMemory(subaddressSize = self.subaddressSize)
        self.staticAddress = staticAddress
        self.deviceInfo = {
            'staticAddress': staticAddress,
            'bcr': {
                'value': [
                    '0b00010000',
                    16,
                    '0x10'
                ],
                'description': {
                    'deviceRole': 'I3C Target.',
                    'advancedCapabilities': 'Does not support optional advanced capabilities.',
                    'virtualTargetSupport': 'Is not a Virtual Target and does not expose other downstream Device(s).',
                    'offlineCapable': 'Device retains the Dynamic Address and will always respond to I3C Bus commands.',
                    'ibiPayload': 'No data bytes follow the accepted IBI.',
                    'ibiRequestCapable': 'Not Capable.',
                    'maxDataSpeedLimitation': 'No Limitation.'
                }
            },
            'dcr': 195,
            'pid': [
                0,
                0,
                0,
                0,
                100,
                101
            ],
            'maxIbiPayloadSize': 1944,
            'i3cFeatures': {
                'targetInterruptRequest': 'ACCEPT_INTERRUPT_REQUEST',
                'controlerRoleRequest': 'ACCEPT_CRR',
                'ibiTimestamp': 'DISABLE_IBIT',
                'assignmentFromStaticAddress': 'I3C_TARGET_DOES_NOT_HAVE_STATIC_ADDR',
                'assignmentFromENTDAA': 'DISABLE_ENTDAA',
                'targetType': 'I3C_DEVICE',
                'pendingReadCapability': 'NOT_SUPPORT_IBI_READ_CAPABILITY',
                'validPid': 'HAS_NOT_VALID_PID'
            }
        }
        self.mrl = 16
        self.mwl = 8

    def setDynamicAddress(self, dynamicAddress):
        self.deviceInfo["dynamicAddress"] = dynamicAddress

    def setMRL(self, mrl):
        self.mrl = mrl

    def getMRL(self):
        return self.mrl

    def setMWL(self, mwl):
        self.mwl = mwl

    def getMWL(self):
        return self.mwl

    def getDeviceInfo(self):
       return self.deviceInfo

    def write(self, writeBuffer, forceSetSubaddres=False):
        if len(writeBuffer) - self.subaddressSize > self.mwl:
            writeBuffer = writeBuffer[:self.mwl+self.subaddressSize]
        self.memModule.write(writeBuffer, forceSetSubaddres)

    def read(self, bytesToRead):
        if bytesToRead > self.mrl:
            bytesToRead = self.mrl
        return self.memModule.read(bytesToRead)
