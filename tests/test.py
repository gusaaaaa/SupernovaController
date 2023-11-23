import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from supernovacontroller.sequential import SupernovaDevice
from deviceSimulators.supernova import BinhoSupernovaSimulator

class TestSupernovaController(unittest.TestCase):
    def setUp(self):
        self.device = SupernovaDevice()
        self.device.driver = BinhoSupernovaSimulator()

    def test_open_any_device_and_close(self):
        info = self.device.open()

        self.assertEqual(info, {
            "hw_version": "6",
            "fw_version": "1.1.0",
            "bl_version": "1.0.1"
        })

        self.device.close()


if __name__ == "__main__":
    unittest.main()
