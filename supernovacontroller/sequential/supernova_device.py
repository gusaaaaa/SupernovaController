from transfer_controller import TransferController
from BinhoSupernova.Supernova import Supernova
from BinhoSupernova.commands.definitions import GetUsbStringSubCommand
from supernovacontroller.errors import DeviceOpenError
import queue
import threading
from .i2c import SupernovaI2CBlockingInterface
from .i3c import SupernovaI3CBlockingInterface

def id_gen(start=0):
    i = start
    while True:
        i += 1
        yield i


class SupernovaDevice:
    def __init__(self, start_id=0):
      self.controller = TransferController(id_gen(start_id))
      self.response_queue = queue.SimpleQueue()
      self.notification_queue = queue.SimpleQueue()

      self.process_response_thread = threading.Thread(target=self._pull_sdk_response, daemon=True)
      self.running = True
      self.process_response_thread.start()
      self.driver = Supernova()

      self.i2c = None
      self.i3c = None

    def open(self, usb_address=None):
        result = self.driver.open(path=usb_address, activateLogger=False)
        if result["code"] == "OPEN_CONNECTION_FAIL":
            raise DeviceOpenError(result["message"])

        self.driver.onEvent(self._push_sdk_response)

        self.i2c = SupernovaI2CBlockingInterface(self.driver, self.controller)
        self.i3c = SupernovaI3CBlockingInterface(self.driver, self.controller)

        responses = self.controller.sync_submit([
            lambda id: self.driver.getUsbString(id, getattr(GetUsbStringSubCommand, 'HW_VERSION')),
            lambda id: self.driver.getUsbString(id, getattr(GetUsbStringSubCommand, 'FW_VERSION')),
            lambda id: self.driver.getUsbString(id, getattr(GetUsbStringSubCommand, 'SERIAL_NUMBER')),
        ])

        def _process_device_info(responses):
            hw_version = responses[0]['message'][3:]
            fw_version = responses[1]['message'][3:]
            serial_number = responses[2]['message'][3:]

            return {
                "hw_version": hw_version,
                "fw_version": fw_version,
                "serial_number": serial_number
            }

        return _process_device_info(responses)

    def _push_sdk_response(self, supernova_response, system_message):
        self.response_queue.put((supernova_response, system_message))

    def _pull_sdk_response(self):
        while self.running:
            try:
                supernova_response, system_message = self.response_queue.get(timeout=1)
                self._process_sdk_response(supernova_response, system_message)
            except queue.Empty:
                continue

    def _process_sdk_response(self, supernova_response, system_message):
        if supernova_response == None:
            return

        is_handled = self.controller.handle_response(
            transfer_id=supernova_response['id'], response=supernova_response)

        if is_handled:
            return

        if supernova_response["name"] == "I3C TRANSFER":
            self.notification_queue.put((supernova_response, system_message))

        # Process non-sequenced responses
        # ...

    def invoke_sync(self, sequence):
        result = None

        def collect_responses(responses):
            nonlocal result
            result = responses

        sequence_id = self.controller.submit(
            sequence=sequence,
            on_ready=collect_responses
        )

        self.controller.wait_for(sequence_id)

        return result

    def close(self):
        self.driver.close()
        self.running = False


