import os
import unittest
from BinhoSupernova.commands.definitions import I3cTargetResetDefByte, TransferDirection
from supernovacontroller.sequential.supernova_device import SupernovaDevice
from supernovacontroller.sequential.i3c import SupernovaI3CBlockingInterface

from binhosimulators import BinhoSupernovaSimulator

BMM350_PID_DATA = {"asString": ["0x07", "0x70", "0x10", "0x33", "0x00", "0x00"], "asInt": [7, 112, 16, 51, 0, 0]}
BMI323_PID_DATA = {"asString": ["0x07", "0x70", "0x10", "0x43", "0x10", "0x00"], "asInt": [7, 112, 16, 67, 16, 0]}
LMS6DSV_PID_DATA = {"asString": ["0x02", "0x08", "0x00", "0x70", "0x92", "0x0b"], "asInt": [2, 8, 0, 112, 146, 11]}

class TestCCCSupernovaController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Initializes the testing class. Determines whether to use the simulator or real device
        based on the "USE_REAL_DEVICE" environment variable. Default is to use the simulator.
        """
        cls.use_simulator = not os.getenv("USE_REAL_DEVICE", "False") == "True"

    def setUp(self):
        self.device = SupernovaDevice()

        if self.use_simulator:
            self.device.driver = BinhoSupernovaSimulator()

        self.device_info = self.device.open()
        self.i3c : SupernovaI3CBlockingInterface = self.device.create_interface("i3c.controller")

    def tearDown(self):
        self.device.close()

    def test_i3c_ccc_setaasa(self):
        if self.use_simulator:
            self.skipTest("For real device only")

        self.i3c.init_bus(3300)
        (deviceFound, bmm350) = self.i3c.find_target_device_by_pid(BMM350_PID_DATA["asString"])
        if not deviceFound:
            self.skipTest("For BMM350")

        (success, response) = self.i3c.ccc_getpid(0x08)
        self.assertTupleEqual((True, BMM350_PID_DATA["asInt"]), (success, response))

        self.i3c.ccc_rstdaa()

        (success, response) = self.i3c.ccc_setaasa([0x14])
        self.assertTupleEqual((True, None), (success, response))

        (success, response) = self.i3c.ccc_getpid(0x14)
        self.assertTupleEqual((True, BMM350_PID_DATA["asInt"]), (success, response))

    def test_i3c_ccc_setaasa_errors(self):
        if self.use_simulator:
            self.skipTest("For real device only")
        self.i3c.init_bus(3300)
        (deviceFound, bmm350) = self.i3c.find_target_device_by_pid(BMM350_PID_DATA["asString"])
        if not deviceFound:
            self.skipTest("For BMM350")

        self.i3c.ccc_rstdaa()
        (res, msg) = self.i3c.ccc_setaasa([0x00])
        self.assertTupleEqual((res, msg), 
                              (False,
                               {"error": "INVALID_ADDRESS", "error_data": [{"address": "0x00", "error": "ADDRESS_RESERVED"}]}))

        (res, msg) = self.i3c.ccc_setaasa([0x14]) # Correctly set DA
        self.assertTupleEqual((True, None), (res, msg))

        (res, msg) = self.i3c.ccc_setaasa([0x14])
        self.assertTupleEqual((res, msg), 
                              (False,
                               {"error": "INVALID_ADDRESS", "error_data": [{"address": "0x14", "error": "ADDRESS_ALREADY_ASSIGNED_TO_I3C_DEVICE"}]}))

    def test_i3c_ccc_setdasa_errors(self):
        if self.use_simulator:
            self.skipTest("For real device only")
        self.i3c.init_bus(3300)
        (deviceFound, bmm350) = self.i3c.find_target_device_by_pid(BMM350_PID_DATA["asString"])
        if not deviceFound:
            self.skipTest("For BMM350")

        self.i3c.ccc_rstdaa()
        (res, msg) = self.i3c.ccc_setdasa(0x14, 0x00)
        self.assertTupleEqual((res, msg), 
                              (False,
                               {"error": "INVALID_ADDRESS", "error_data": [{"address": "0x00", "error": "ADDRESS_RESERVED"}]}))

        (res, msg) = self.i3c.ccc_setdasa(0x14, 0x08) # Correctly set DA
        self.assertTupleEqual((True, None), (res, msg))

        (res, msg) = self.i3c.ccc_setdasa(0x14, 0x08)
        self.assertTupleEqual((res, msg), 
                              (False,
                               {"error": "INVALID_ADDRESS", "error_data": [{"address": "0x08", "error": "ADDRESS_ALREADY_ASSIGNED_TO_I3C_DEVICE"}]}))

    def test_i3c_ccc_entdaa(self):
        if self.use_simulator:
            self.skipTest("For real device only")

        self.i3c.init_bus(3300)
        (deviceFound, bmi323) = self.i3c.find_target_device_by_pid(BMI323_PID_DATA["asString"])
        if not deviceFound:
            self.skipTest("For BMI323")

        entdaa_target_dict = {
            "bmi323" : {
            "staticAddress" : 0x14,
            "dynamicAddress" : 0x09,
            "i3cFeatures": 11,
            "maxIbiPayloadLength": 233,
            "bcr" : 6,
            "dcr" : 239,
            "pid" : [7, 112, 16, 67, 16, 0]
            },
        }

        (success, response) = self.i3c.ccc_getpid(bmi323["dynamic_address"])
        self.assertTupleEqual((True, BMI323_PID_DATA["asInt"]), (success, response))

        (res, msg) = self.i3c.reset_bus()
        self.assertTupleEqual((True, 3300), (res, msg))

        (res, msg) = self.i3c.ccc_entdaa(entdaa_target_dict)
        self.assertTupleEqual((True, None), (res, msg))
        
        (success, response) = self.i3c.ccc_getpid(0x09)
        self.assertTupleEqual((True, BMI323_PID_DATA["asInt"]), (success, response))

        (deviceFound, bmi323) = self.i3c.find_target_device_by_pid(BMI323_PID_DATA["asString"])
        self.assertTupleEqual((True, {
                "static_address" : 0x14,
                "dynamic_address" : 0x09,
                "bcr" : 6,
                "dcr" : 239,
                "pid" : ["0x07", "0x70", "0x10", "0x43", "0x10", "0x00"]
                },), (deviceFound, bmi323))
    
    def test_i3c_ccc_entdaa_invalid_address(self):
        if self.use_simulator:
            self.skipTest("For real device only")

        self.i3c.init_bus(3300)
        (deviceFound, bmi323) = self.i3c.find_target_device_by_pid(BMI323_PID_DATA["asString"])
        if not deviceFound:
            self.skipTest("For BMI323")

        entdaa_target_dict = {
            "bmi323" : {
            "staticAddress" : 0x14,
            "dynamicAddress" : 0x00,
            "i3cFeatures": 11,
            "maxIbiPayloadLength": 233,
            "bcr" : 6,
            "dcr" : 239,
            "pid" : [7, 112, 16, 67, 16, 0]
            },
        }

        (res, msg) = self.i3c.reset_bus()
        self.assertTupleEqual((True, 3300), (res, msg))

        (res, msg) = self.i3c.ccc_entdaa(entdaa_target_dict)
        self.assertTupleEqual((False, 
                               {"error": "INVALID_ADDRESS", "error_data": [{"address": "0x00", "error": "ADDRESS_RESERVED"}]}), 
                               (res, msg))

    def test_i3c_ccc_broadcast_setxtime(self):
        if self.use_simulator:
            self.skipTest("For real device only")

        self.i3c.init_bus(3300)

        (success, response) = self.i3c.ccc_broadcast_setxtime(0xDF)
        self.assertTupleEqual((True, None), (success, response))

        # Once getxtime is updated to return the current state, use it here to check the setxtime works (BMC2-1663)
        # print(self.i3c.ccc_getxtime(0x08))

        (success, response) = self.i3c.ccc_broadcast_setxtime(0x00, [0xAA, 0xBB])
        self.assertTupleEqual((True, None), (success, response))

        # Idem (BMC2-1663)
        # print(self.i3c.ccc_getxtime(0x08)) 
        
    def test_ccc_getpid(self):
        if not self.use_simulator:
            self.skipTest("For simulator only")

        i3c = self.device.create_interface("i3c.controller")

        i3c.init_bus(3300)

        (success, result) = i3c.ccc_getpid(0x08)

        self.assertTupleEqual((success, result), (True, [0x00, 0x00, 0x00, 0x00, 0x64, 0x65]))

    def test_ccc_rstdaa(self):
        if self.use_simulator:
            self.skipTest("For real device only")

        i3c = self.device.create_interface("i3c.controller")

        i3c.init_bus(3300)

        (success, result) = i3c.ccc_rstdaa()

        self.assertTupleEqual((success, result), (True, None))

        (success, result) = i3c.ccc_getpid(0x08)

        self.assertTupleEqual((success, result), (False, "NACK_ERROR"))

    def test_ccc_get_and_set_mrl(self):
        if not self.use_simulator:
            self.skipTest("For simulator only")

        i3c = self.device.create_interface("i3c.controller")

        i3c.init_bus(3300)

        (success, result) = i3c.ccc_getmrl(0x08)

        self.assertTupleEqual((success, result), (True, 16))

        (success, _) = i3c.ccc_unicast_setmrl(0x08, 10)

        self.assertEqual(success, True)

        (success, result) = i3c.ccc_getmrl(0x08)

        self.assertTupleEqual((success, result), (True, 10))

    def test_ccc_set_mwl_real_device(self):
        if self.use_simulator:
            self.skipTest("For real device only")

        i3c = self.device.create_interface("i3c.controller")

        i3c.init_bus(3300)

        (_, connectedDevices) = i3c.targets()

        if len(connectedDevices) == 0:
            self.fail("Test requires a connected target")

        (deviceFound, lms6dsv) = self.i3c.find_target_device_by_pid(LMS6DSV_PID_DATA["asString"])
        if not deviceFound:
            self.skipTest("For LMS6DSV")

        (success, _) = i3c.ccc_broadcast_setmwl(10)

        self.assertEqual(success, True)

        (success, result) = i3c.ccc_getmwl(lms6dsv["dynamic_address"])

        self.assertTupleEqual((success, result), (True, 10))

    def test_direct_rstact_read(self):
        if self.use_simulator:
            self.skipTest("For real device only")

        i3c = self.device.create_interface("i3c.controller")

        i3c.init_bus(3300)

        (success, result) = i3c.ccc_direct_rstact(0x08, I3cTargetResetDefByte.RESET_I3C_PERIPHERAL, TransferDirection.READ)

        self.assertTupleEqual((success, result), (True, [0x00]))

    def test_direct_rstact_write(self):
        if self.use_simulator:
            self.skipTest("For real device only")

        i3c = self.device.create_interface("i3c.controller")

        i3c.init_bus(3300)

        (success, result) = i3c.ccc_direct_rstact(0x08, I3cTargetResetDefByte.RESET_I3C_PERIPHERAL, TransferDirection.WRITE)

        self.assertTupleEqual((success, result), (True, None))

    def test_broadcast_rstact(self):
        if self.use_simulator:
            self.skipTest("For real device only")

        i3c = self.device.create_interface("i3c.controller")

        i3c.init_bus(3300)

        (success, result) = i3c.ccc_broadcast_rstact(I3cTargetResetDefByte.RESET_I3C_PERIPHERAL)

        self.assertTupleEqual((success, result), (True, None))

if __name__ == "__main__":
    unittest.main()