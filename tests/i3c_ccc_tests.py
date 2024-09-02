import os
import unittest
from supernovacontroller.sequential.supernova_device import SupernovaDevice
from supernovacontroller.sequential.i3c import SupernovaI3CBlockingInterface

from binhosimulators import BinhoSupernovaSimulator

BMM350_PID = {"asString": ["0x07", "0x70", "0x10", "0x33", "0x00", "0x00"], "asInt": [7, 112, 16, 51, 0, 0]}

class TestSupernovaController(unittest.TestCase):
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
        (deviceFound, bmm350) = self.i3c.find_target_device_by_pid(BMM350_PID["asString"])
        if not deviceFound:
            self.skipTest("For BMM350")

        (success, response) = self.i3c.ccc_getpid(0x08)
        self.assertTupleEqual((True, BMM350_PID["asInt"]), (success, response))

        self.i3c.ccc_rstdaa()

        (success, response) = self.i3c.ccc_setaasa([0x14])
        self.assertTupleEqual((True, None), (success, response))

        (success, response) = self.i3c.ccc_getpid(0x14)
        self.assertTupleEqual((True, BMM350_PID["asInt"]), (success, response))

    def test_i3c_ccc_setaasa_errors(self):
        if self.use_simulator:
            self.skipTest("For real device only")
        self.i3c.init_bus(3300)
        (deviceFound, bmm350) = self.i3c.find_target_device_by_pid(BMM350_PID["asString"])
        if not deviceFound:
            self.skipTest("For BMM350")

        self.i3c.ccc_rstdaa()
        (res, msg) = self.i3c.ccc_setaasa([0x00])
        self.assertTupleEqual((res, msg), 
                              (False,
                               {'error': 'INVALID_ADDRESS', 'error_data': [{'address': '0x00', 'error': 'ADDRESS_RESERVED'}]}))

        (res, msg) = self.i3c.ccc_setaasa([0x14]) # Correctly set DA
        self.assertTupleEqual((True, None), (res, msg))

        (res, msg) = self.i3c.ccc_setaasa([0x14])
        self.assertTupleEqual((res, msg), 
                              (False,
                               {'error': 'INVALID_ADDRESS', 'error_data': [{'address': '0x14', 'error': 'ADDRESS_ALREADY_ASSIGNED_TO_I3C_DEVICE'}]}))

    def test_i3c_ccc_setdasa_errors(self):
        if self.use_simulator:
            self.skipTest("For real device only")
        self.i3c.init_bus(3300)
        (deviceFound, bmm350) = self.i3c.find_target_device_by_pid(BMM350_PID["asString"])
        if not deviceFound:
            self.skipTest("For BMM350")

        self.i3c.ccc_rstdaa()
        (res, msg) = self.i3c.ccc_setdasa(0x14, 0x00)
        self.assertTupleEqual((res, msg), 
                              (False,
                               {'error': 'INVALID_ADDRESS', 'error_data': [{'address': '0x00', 'error': 'ADDRESS_RESERVED'}]}))

        (res, msg) = self.i3c.ccc_setdasa(0x14, 0x08) # Correctly set DA
        self.assertTupleEqual((True, None), (res, msg))

        (res, msg) = self.i3c.ccc_setdasa(0x14, 0x08)
        self.assertTupleEqual((res, msg), 
                              (False,
                               {'error': 'INVALID_ADDRESS', 'error_data': [{'address': '0x08', 'error': 'ADDRESS_ALREADY_ASSIGNED_TO_I3C_DEVICE'}]}))

if __name__ == "__main__":
    unittest.main()