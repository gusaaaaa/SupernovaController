import unittest
from unittest import mock
import sys
import os
from supernovacontroller.sequential import SupernovaDevice
from supernovacontroller.errors import DeviceOpenError
from supernovacontroller.errors import BusVoltageError
from supernovacontroller.errors import BusNotInitializedError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from deviceSimulators.supernova import BinhoSupernovaSimulator

class TestSupernovaController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Initializes the testing class. Determines whether to use the simulator or real device
        based on the 'USE_REAL_DEVICE' environment variable. Default is to use the simulator.
        """
        cls.use_simulator = not os.getenv('USE_REAL_DEVICE', 'False') == 'True'

    def setUp(self):
        self.device = SupernovaDevice()
        if self.use_simulator:
            self.device.driver = BinhoSupernovaSimulator()

    def test_open_device_with_wrong_address(self):
        with self.assertRaises(DeviceOpenError):
            self.device.open("whatever")

    def test_open_device_and_close(self):
        info = self.device.open()

        self.assertRegex(info['hw_version'], r'^[A-Za-z0-9]$', "Invalid hw_version format")
        self.assertRegex(info['fw_version'], r'^\d+\.\d+\.\d+$', "Invalid fw_version format")
        self.assertRegex(info['serial_number'], r'^[A-Fa-f0-9]+$', "Invalid serial_number format")

        self.device.close()

    def test_set_i3c_bus_voltage_attribute(self):
        self.device.open()

        (success, result) = self.device.i3c.set_bus_voltage(3300)

        self.assertTupleEqual((success, result), (True, 3300))
        self.assertEqual(self.device.i3c.bus_voltage, 3300)

        self.device.close()

    def test_set_i3c_bus_voltage_attribute_error(self):
        self.device.open()

        # Mock the controller's sync_submit method to simulate a failure response.
        # It's important to note that this approach makes the test somewhat dependent
        # on the internal implementation of the device class.
        with mock.patch.object(self.device.controller, 'sync_submit') as mock_sync_submit:
            mock_sync_submit.return_value = [{"name": "SET I3C BUS VOLTAGE", "result": 1}]  # Simulate an error response

            # Call the method under test
            (success, result) = self.device.i3c.set_bus_voltage(3300)

            # Assert that the method correctly returns an error
            self.assertTupleEqual((success, result), (False, "Set bus voltage failed"))
            self.assertEqual(self.device.i3c.bus_voltage, None)

        self.device.close()

    def test_i3c_init_bus_with_no_targets_connected(self):
        # This test assumes that the are no devices connected to the bus.

        if self.use_simulator:
            self.skipTest("For real device only")

        self.device.open()

        (success, result) = self.device.i3c.init_bus(1500)

        self.assertEqual(success, False)
        self.assertTrue("errors" in result)
        self.assertEqual(self.device.i3c.bus_voltage, None)

        self.device.close()

    def test_i3c_reset_bus(self):
        if not self.use_simulator:
            self.skipTest("For simulator only")

        self.device.open()

        self.device.i3c.init_bus(2000)
        (success, result) = self.device.i3c.reset_bus()

        self.assertTupleEqual((success, result), (True, 2000))

        self.device.close()

    def test_i3c_reset_bus_before_init(self):
        if not self.use_simulator:
            self.skipTest("For simulator only")

        self.device.open()

        with self.assertRaises(BusNotInitializedError):
            self.device.i3c.reset_bus()

        self.device.close()

    def test_i3c_targets(self):
        if not self.use_simulator:
            self.skipTest("For simulator only")

        self.device.open()

        self.device.i3c.init_bus(3300)
        (success, targets) = self.device.i3c.targets()

        self.assertEqual(success, True)
        self.assertEqual(len(targets), 4)
        self.assertDictEqual(targets[0], {
            'bcr': 0x10,
            'dcr': 0xC3,
            'dynamic_address': 0x08,
            'pid': [0x65, 0x64, 0x00, 0x00, 0x00, 0x00],
            'static_address': 0x50
        })
        self.assertDictEqual(targets[1], {
            'bcr': 0x10,
            'dcr': 0xC3,
            'dynamic_address': 0x09,
            'pid': [0x65, 0x64, 0x00, 0x00, 0x00, 0x00],
            'static_address': 0x51
        })
        self.assertDictEqual(targets[2], {
            'bcr': 0x10,
            'dcr': 0xC3,
            'dynamic_address': 0x0A,
            'pid': [0x65, 0x64, 0x00, 0x00, 0x00, 0x00],
            'static_address': 0x52
        })
        self.assertDictEqual(targets[3], {
            'bcr': 0x03,
            'dcr': 0x63,
            'dynamic_address': 0x0B,
            'pid': [0x5A, 0x00, 0x1D, 0x0F, 0x17, 0x02],
            'static_address': 0x53
        })

        self.device.close()

    def test_i3c_targets_when_bus_not_initialized(self):
        if not self.use_simulator:
            self.skipTest("For simulator only")

        self.device.open()

        with self.assertRaises(BusNotInitializedError):
            self.device.i3c.targets()

        self.device.close()

    def test_i3c_successful_write_operation_on_target_should_return_none(self):
        if not self.use_simulator:
            self.skipTest("For simulator only")

        self.device.open()

        self.device.i3c.init_bus(3300)

        subaddress = [0x00, 0x00]

        (success, result) = self.device.i3c.write(
            0x08,
            self.device.i3c.TransferMode.I3C_SDR,
            subaddress,
            [0xDE, 0xAD, 0xBE, 0xEF]
        )

        self.assertTupleEqual((success, result), (True, None))

        self.device.close()

    def test_i3c_successful_write_read_operations_on_target(self):
        if not self.use_simulator:
            self.skipTest("For simulator only")

        self.device.open()

        self.device.i3c.init_bus(3300)

        subaddress = [0x00, 0x00]

        (success, result) = self.device.i3c.write(
            0x08,
            self.device.i3c.TransferMode.I3C_SDR,
            subaddress,
            [0xDE, 0xAD, 0xBE, 0xEF]
        )

        (success, result) = self.device.i3c.read(
            0x08,
            self.device.i3c.TransferMode.I3C_SDR,
            subaddress,
            4
        )

        self.assertTupleEqual((success, result), (True, [0xDE, 0xAD, 0xBE, 0xEF]))

        self.device.close()

    def test_ccc_getpid(self):
        if not self.use_simulator:
            self.skipTest("For simulator only")

        self.device.open()

        self.device.i3c.init_bus(3300)

        (success, result) = self.device.i3c.ccc_getpid(0x08)

        self.assertTupleEqual((success, result), (True, [0x00, 0x00, 0x00, 0x00, 0x64, 0x65]))

        self.device.close()

if __name__ == "__main__":
    unittest.main()
