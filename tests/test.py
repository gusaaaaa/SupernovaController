import unittest
from unittest import mock
import sys
import os
from supernovacontroller.sequential import SupernovaDevice
from supernovacontroller.errors import DeviceOpenError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from deviceSimulators.supernova import BinhoSupernovaSimulator

class TestSupernovaController(unittest.TestCase):
    def setUp(self):
        self.device = SupernovaDevice()
        # self.device.driver = BinhoSupernovaSimulator()

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

if __name__ == "__main__":
    unittest.main()
