from BinhoSupernova.Supernova import Supernova
from BinhoSupernova.commands.definitions import *
from queue import SimpleQueue

responses = SimpleQueue()

def wait_for_response() -> dict:
  response = responses.get()
  return response

def callback_function(supernova_message: dict, system_message: dict) -> None:
  responses.put((supernova_message, system_message))

def id_gen(start=0):
  i = start
  while True:
    i += 1
    yield i

id = id_gen()

driver = Supernova()

result = driver.open()

driver.onEvent(callback_function)

driver.getUsbString(next(id), GetUsbStringSubCommand.FW_VERSION)
print(wait_for_response())

driver.setI3cBusVoltage(next(id), 3300)
print(wait_for_response())

driver.i3cInitBus(next(id))
print(wait_for_response())

driver.i3cGetTargetDeviceTable(next(id))
print(wait_for_response())
