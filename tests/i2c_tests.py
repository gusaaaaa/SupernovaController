import os
import unittest

from binhosimulators import BinhoSupernovaSimulator
from supernovacontroller.sequential.i2c import SupernovaI2CBlockingInterface
from supernovacontroller.sequential.supernova_device import SupernovaDevice

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
        self.i2c : SupernovaI2CBlockingInterface = self.device.create_interface("i2c")

    def tearDown(self):
        self.device.close()
        

    def test_i2c_set_parameters(self):
        (success, result) = self.i2c.set_parameters(500000)

        self.assertEqual(success, True)
        self.assertEqual(result, (500000))

    def test_i2c_should_not_throw_error_if_bus_voltage_is_not_set(self):
        (success, _) = self.i2c.read_from(0x50, [0x00,0x00], 4)

        self.assertEqual(success, True)

    def test_i2c_set_bus_voltage_or_init_bus_are_equivalent(self):
        self.i2c.set_bus_voltage(3300)
        self.i2c.set_parameters(500000)

        try:
            self.i2c.read_from(0x50, [0x00,0x00], 1)
        except Exception as e:
            self.fail(f"self.i2c read raised an exception {e}")

    def test_i2c_write(self):
        self.i2c.init_bus(3300)
        self.i2c.set_parameters(500000)
        (success, result) = self.i2c.write(0x50, [0x00,0x00], [0xDE, 0xAD, 0xBE, 0xEF])

        self.assertEqual(success, True)
        self.assertEqual(result, None)

    def test_i2c_write_non_stop(self):
        if self.use_simulator:
            self.skipTest("For real device only")

        self.i2c.init_bus(3300)
        self.i2c.set_parameters(500000)
        
        data_length = 70
        data_to_write = [55 for i in range(0, data_length)]
        
        (success, result) = self.i2c.write_non_stop(0x50, [0x01,0x00], data_to_write)
        self.assertEqual(success, True)
        self.assertEqual(result, None)
        
        (success, result) = self.i2c.read_from(0x50, [0x01,0x00], data_length)
        self.assertTupleEqual((success, result), (True, data_to_write))

    def test_i2c_write_non_stop_should_nack(self):
        if self.use_simulator:
            self.skipTest("For real device only")

        self.i2c.init_bus(3300)
        self.i2c.set_parameters(500000)
        
        data_length = 70
        data_to_write = [55 for i in range(0, data_length)]
        
        (success, result) = self.i2c.write_non_stop(0x56, [0x01,0x00], data_to_write)
        self.assertTupleEqual((success, result), (False, "NACK_ERROR"))

    def test_i2c_write_read_from(self):
        self.i2c.init_bus(3300)
        self.i2c.set_parameters(500000)

        self.i2c.write(0x50, [0x00,0x00], [0xDE, 0xAD, 0xBE, 0xEF])
        (success, data) = self.i2c.read_from(0x50, [0x00,0x00], 4)

        self.assertEqual(success, True)
        self.assertEqual(data, [0xDE, 0xAD, 0xBE, 0xEF])

    def test_i2c_write_continuous_read(self):
        self.i2c.init_bus(3300)
        self.i2c.set_parameters(500000)

        self.i2c.write(0x50, [0x00, 0x00], [0x01, 0x02, 0x03, 0x04])
        self.i2c.write(0x50, [], [0x00, 0x00])
        (success, a) = self.i2c.read(0x50, 1)
        (success, b) = self.i2c.read(0x50, 1)
        (success, cd) = self.i2c.read(0x50, 2)

        self.assertEqual(success, True)
        self.assertEqual(a, [0x01])
        self.assertEqual(b, [0x02])
        self.assertEqual(cd, [0x03, 0x04])
        
if __name__ == "__main__":
    unittest.main()
