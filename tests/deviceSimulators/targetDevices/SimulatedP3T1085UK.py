import random

# Helpers:
def setBit(num, pos, bitValue):
    mask = 1 << pos
    return num | mask if bitValue else num & ~mask

def getBit(num, pos):
    mask = 1 << pos
    return (num & mask) >> pos

def intListToInt(num):
    return num[1] + (num[0] << 8)

def intToListInt(num):
	return [num >> 8, num % 256]

def binIntToTwosComplementInt(num, bit_num):
    return int(bin(num & (2 ** bit_num - 1)), 2)

def twosComplementIntToBinInt(num, bit_num):
    result = binIntToTwosComplementInt(num, bit_num)
    if num >> (bit_num - 1): result -= 2 ** bit_num
    return result

def twosComplementToFloat(twoCompInteger, resolution):
    twoCompIntegerList = intToListInt(twoCompInteger)
    integer_part = twosComplementIntToBinInt(twoCompIntegerList[0], 8)
    decimal_part = twoCompIntegerList[1] >> 4
    floatResult = integer_part + (decimal_part * resolution)
    return floatResult

# Sensor:
class SimulatedP3T1085UK:

	class TemperatureGenerator:
		def __init__(self):
			self.resolution = 0.0625
			self.sigma = 0.5 # in °C
			self.previousTemperature = self.generateRandomTemperature(correlates = False) 
			self.sensedTemperature = self.previousTemperature

		def readTemperature(self):
			self.previousTemperature = self.sensedTemperature
			self.sensedTemperature = self.generateRandomTemperature()
			return self.sensedTemperature

		def generateRandomTemperature(self, correlates = True):
			if correlates:
				mu = twosComplementToFloat(self.previousTemperature, self.resolution) # Correlates with previous Temp
			else: # First measurement is chosen to be near 20°C
				mu = 20  		 
			newTemperatureMesurement = self.randomTemperature(self.resolution, mu, self.sigma) 
			newTemperatureMesurement = max(newTemperatureMesurement, -40) if newTemperatureMesurement < 0 else min(newTemperatureMesurement, 125) # Ensure operating range
			# Split into integer and decimal parts to construct the final 12 bit (the 12 MSB of a 16 bits word)
			newTemperatureMesurementIntegerPart = binIntToTwosComplementInt(int(newTemperatureMesurement), 8) << 8
			newTemperatureMesurementDecimalPart = int((newTemperatureMesurement % 1)/self.resolution) << 4
			return newTemperatureMesurementIntegerPart + newTemperatureMesurementDecimalPart

		def randomTemperature(self, prec, mu, sigma):
			return round(random.gauss(mu, sigma)/prec)*prec
	
	# SimulatedP3T1085UK Class Constructor
	def __init__(self, staticAddress):
		self.staticAddress = staticAddress
		self.dynamicAddress = self.staticAddress
		self.pointerRegister = 0          # POR value: 00h
		self.sensedTemperature = 0        # POR value: 0000h
		self.lowTemperatureLimit = 46336  # POR value: B500h
		self.highTemperatureLimit = 32752 # POR value: 7FF0h
		self.configurationRegister = 8720 # POR value: 2210h
		self.temperatureGenerator = self.TemperatureGenerator()
		self.deviceInfo = {
				"staticAddress":staticAddress,
				"bcr":{
					"value":[
					"0b00000011",
					3,
					"0x03"
					],
					"description":{
					"deviceRole":"I3C Target.",
					"advancedCapabilities":" Does not supports optional advanced capabilities.",
					"virtualTargetSupport":"Is not a Virtual Target and does not expose other downstream Device(s).",
					"offlineCapable":"Device will always react to I3C bus commands.",
					"ibiPayload":"No data byte follow the accepted IBI.",
					"ibiRequestCapable":"Capable.",
					"maxDataSpeedLimitation":"Limitation."
					}
				},
				"dcr":99,
				"pid":[
					2,
					23,
					15,
					29,
					00,
					90,
				],
				"maxIbiPayloadSize":0,
				"i3cFeatures":{
					"targetInterruptRequest":"ACCEPT_INTERRUPT_REQUEST",
					"controlerRoleRequest":"ACCEPT_CRR",
					"ibiTimestamp":"DISABLE_IBIT",
					"assignmentFromStaticAddress":"I3C_TARGET_DOES_NOT_HAVE_STATIC_ADDR",
					"assignmentFromENTDAA":"DISABLE_ENTDAA",
					"targetType":"I3C_DEVICE",
					"pendingReadCapability":"NOT_SUPPORT_IBI_READ_CAPABILITY",
					"validPid":"HAS_NOT_VALID_PID"
				}
			}

	def getDeviceInfo(self):
		return self.deviceInfo

	def read(self, bytesToRead = 2): #  subaddress = 0,
		#self.pointerRegister = subaddress # if subaddress else None
		#print('***SUBADDRESS:', subaddress)
		match self.pointerRegister:
			case 0:
				result = intToListInt(self.readTemperature())
			case 1:
				result = intToListInt(self.configurationRegister)
			case 2:
				result = intToListInt(self.lowTemperatureLimit)
			case 3:
				result = intToListInt(self.highTemperatureLimit)
			case _:
				pass
		result = result[0:bytesToRead] if bytesToRead <= 2 else result + (bytesToRead-2)*[255]
		return result

	def write(self, data):
		self.pointerRegister = data[0]
		if len(data) > 1:
			match self.pointerRegister:
				case 1:
					self.configurationRegister = intListToInt(data[1:])
				case 2:
					self.lowTemperatureLimit = intListToInt(data[1:])
				case 3:
					self.highTemperatureLimit = intListToInt(data[1:])
				case _:
					pass

	def readTemperature(self):
		temperatureResult = self.temperatureGenerator.readTemperature()
		# Convert two complement's integers to floats:
		HighLimitTemperature = twosComplementToFloat(self.highTemperatureLimit, self.temperatureGenerator.resolution)
		LowLimitTemperature = twosComplementToFloat(self.lowTemperatureLimit, self.temperatureGenerator.resolution)
		temperature = twosComplementToFloat(temperatureResult, self.temperatureGenerator.resolution)
		# Check if temperature is in the allowed temperature range:
		self.configurationRegister = setBit(self.configurationRegister, 12, 1) if (temperature > HighLimitTemperature) else setBit(self.configurationRegister, 12, 0)
		self.configurationRegister = setBit(self.configurationRegister, 11, 1) if (temperature < LowLimitTemperature) else setBit(self.configurationRegister, 11, 0)
		return temperatureResult

	def setDynamicAddress(self, dynamicAddress): # Should modify deviceInfo?
		self.dynamicAddress = dynamicAddress
		self.deviceInfo["dynamicAddress"] = dynamicAddress
		return
