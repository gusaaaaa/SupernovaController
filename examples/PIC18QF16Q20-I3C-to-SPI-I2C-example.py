import queue
from threading import Event
import time

from supernovacontroller.sequential import SupernovaDevice
from supernovacontroller.sequential.i3c import SupernovaI3CBlockingInterface

caught_ibis = queue.SimpleQueue()
caught_hot_join = Event()
pic_hot_joined_info = {}

# PIC Specific commands
PIC_I2C_WRITE_COMMAND = 0x40
PIC_I2C_READ_COMMAND = 0x20
PIC_SPI_WRITE_READ_COMMAND = 0x60
PIC_SPI_READ_COMMAND = 0x21
PIC_SPI_WRITE_COMMAND = 0x41

def main():
    # ---
    # Supernova & I3C Set Up
    # ---

    device = SupernovaDevice()
    print("Opening Supernova host adapter device")
    device.open()

    # IBI configuration
    def is_ibi(name, message):
        return message['name'].strip() == "I3C IBI NOTIFICATION" and message['header']['type'] == "IBI_NORMAL" and message['MDB']['value'] != 2

    def handle_ibi(name, message):
        global caught_ibis
        ibi_info = {'dynamic_address': message['header']['address'],  'controller_response': message['header']['response'], 'mdb':message['payload'][0], 'payload':message['payload'][1:]}
        caught_ibis.put(ibi_info)

    device.on_notification(name="ibi", filter_func=is_ibi, handler_func=handle_ibi)

    def is_hot_join_ibi(name, message):
        return message['name'].strip() == "I3C IBI NOTIFICATION" and message['header']['type'] == "IBI_HOT_JOIN"

    def handle_hot_join_ibi(name, message):
        global caught_hot_join
        global pic_hot_joined_info
        pic_hot_joined_info = {'dynamic_address': message['header']['address'], 'bcr': message['bcr'], 'dcr': message['dcr'], 'pid': message['pid']}
        caught_hot_join.set()

    device.on_notification(name="hot_join", filter_func=is_hot_join_ibi, handler_func=handle_hot_join_ibi)

    # I3C Initialization
    i3c : SupernovaI3CBlockingInterface = device.create_interface("i3c.controller")

    print("Initializing the bus...\n")
    i3c.set_parameters(i3c.I3cPushPullTransferRate.PUSH_PULL_3_75_MHZ, i3c.I3cOpenDrainTransferRate.OPEN_DRAIN_500_KHZ)
    i3c.set_bus_voltage(1200)
    i3c.init_bus()

    print("Awaiting PIC Hot Join")
    successful_hotjoin = caught_hot_join.wait(15)

    if not successful_hotjoin:
        print("Could not hot join PIC, timeout exceeded")
        exit(1)


    pic_dynamic_address = int(pic_hot_joined_info['dynamic_address'])

    print(i3c.targets())
    time.sleep(0.5)

    # ---
    # I2C
    # ---
    ADDRESS_TO_WRITE_READ = 0x50
    SHIFTED_ADDRESS = ADDRESS_TO_WRITE_READ << 1
    REGISTER_TO_WRITE_READ = [0x00, 0x00]
    DATA_TO_WRITE = [0x06, 0x07, 0x08, 0x09, 0x0A]
    BYTES_TO_READ = 0x05

    (success, _) = i3c.write(pic_dynamic_address, i3c.TransferMode.I3C_SDR, [], [PIC_I2C_WRITE_COMMAND, SHIFTED_ADDRESS] + REGISTER_TO_WRITE_READ + DATA_TO_WRITE)
    print("Write at Register 00 00 data 06 07 08 09 0A :", "SUCCESS" if success else "FAIL")
    time.sleep(0.5)

    (success, _) = i3c.write(pic_dynamic_address, i3c.TransferMode.I3C_SDR, [], [PIC_I2C_WRITE_COMMAND, SHIFTED_ADDRESS] + REGISTER_TO_WRITE_READ)
    print("Reset data pointer to 00 00", "SUCCESS" if success else "FAIL")
    time.sleep(0.5)

    (success, _) = i3c.write(pic_dynamic_address, i3c.TransferMode.I3C_SDR, [], [PIC_I2C_READ_COMMAND, SHIFTED_ADDRESS, BYTES_TO_READ])
    print("Read 5 bytes", "SUCCESS" if success else "FAIL")
    time.sleep(0.5)

    try:
        reading_ibi = caught_ibis.get(timeout=3)
    except queue.Empty:
        print("Did not catch any IBI readings, is everything properly connected?")
        exit(1)
    
    print("Read from I2C target:", reading_ibi)

    # ---
    # SPI
    # ---
    
    # SPI Commands
    SPI_WRITE_ENABLE_COMMAND = 0x06
    SPI_READ_STATUS_REGISTER1_COMMAND = 0x05
    SPI_GET_JEDEC_COMMAND = 0x9F
    SPI_STATUS_REGISTER1 = 0x01

    DATA_TO_WRITE = 0x60
    BYTES_TO_READ = 0x03

    (success, _) = i3c.write(pic_dynamic_address, i3c.TransferMode.I3C_SDR, [], [PIC_SPI_WRITE_READ_COMMAND, BYTES_TO_READ, SPI_GET_JEDEC_COMMAND])
    print("Read JEDEC ID:", "SUCCESS" if success else "FAIL")

    try:
        reading_ibi = caught_ibis.get(timeout=3)
    except queue.Empty:
        print("Did not catch any new IBI readings, is everything properly connected?")
        exit(1)

    print("Read from SPI target:", reading_ibi)
    time.sleep(0.5)   

    (success, _) = i3c.write(pic_dynamic_address, i3c.TransferMode.I3C_SDR, [], [PIC_SPI_WRITE_COMMAND, SPI_WRITE_ENABLE_COMMAND])
    print("Enable writing in the Memory via Write Enable", "SUCCESS" if success else "FAIL")
    time.sleep(0.5)

    (success, _) = i3c.write(pic_dynamic_address, i3c.TransferMode.I3C_SDR, [], [PIC_SPI_WRITE_COMMAND, SPI_STATUS_REGISTER1, DATA_TO_WRITE])
    print("Write in SPI Status Register data", "SUCCESS" if success else "FAIL")
    time.sleep(0.5)

    (success, _) = i3c.write(pic_dynamic_address, i3c.TransferMode.I3C_SDR, [], [PIC_SPI_WRITE_READ_COMMAND, SPI_STATUS_REGISTER1, SPI_READ_STATUS_REGISTER1_COMMAND])
    print("Read in SPI Memory", "SUCCESS" if success else "FAIL")
    time.sleep(0.5)

    try:
        reading_ibi = caught_ibis.get(timeout=3)
    except queue.Empty:
        print("Did not catch any new IBI readings, is everything properly connected?")
        exit(1)

    print("Read from SPI target:", reading_ibi)

if __name__ == "__main__":
    main()