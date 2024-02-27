from supernovacontroller.sequential import SupernovaDevice
from BinhoSupernova.commands.definitions import SpiControllerBitOrder

def main():
    """
    Basic example to illustrate SPI protocol usage with SupernovaController.

    In this example we initialize the SPI peripheral with the following parameters:
        Bit order: LSB first
        Mode: Mode 0 (default value)
        Data width: 8 bits data width (default value, can't be changed)
        Chip select: CS0 (default value)
        Chip select polarity: Active low (default value)
        Frequency: 10 MHz (default value)

    Then the bit order is changed to MSB first.
    With this configuration a FRAM memory (Adafruit MB85RS64V) is used to test the SPI controller interface, transferring data to the memory and reading it, verifying it's correct operation.
    """
    device = SupernovaDevice()

    print("Opening Supernova host adapter device and getting access to the SPI protocol interface...")
    info = device.open()
    spi_controller = device.create_interface("spi.controller")

    print("Initializing SPI peripheral.")
    (success, _) = spi_controller.set_bus_voltage(3300)
    if not success:
        print("Couldn't set the SPI bus voltage.")
        exit(1)

    (success, _) = spi_controller.init_bus(bit_order=SpiControllerBitOrder.LSB)
    if not success:
        print("Couldn't initialize SPI peripheral.")
        exit(1)

    (success, response) = spi_controller.get_parameters()
    if success:
        print(f"The configured parameters are:")
        print(f"Bit order: {response[0].name}, Mode: {response[1].name}, Data width: {response[2].name}, Chip select: {response[3].name}, Chip select polarity: {response[4].name}, Frequency: {response[5]}")
    else:
        print("Failed to retrieve SPI parameters.")

    ## From this part we are going to work with the FRAM memory connected to the Supernova

    # Change bit order to MSB first
    print("Changing the bit order to MSB first.")
    (success, response) = spi_controller.set_parameters(bit_order = SpiControllerBitOrder.MSB)
    if not success:
        print("Couldn't set the SPI parameters correctly.")
        exit(1)

    (success, response) = spi_controller.get_parameters()
    if success:
        print(f"The configured parameters are:")
        print(f"Bit order: {response[0].name}, Mode: {response[1].name}, Data width: {response[2].name}, Chip select: {response[3].name}, Chip select polarity: {response[4].name}, Frequency: {response[5]}")
    else:
        print("Failed to retrieve SPI parameters.")

    ## Transfer data over SPI
    
    # Read Manufacturer ID
    print("Reading manufacturer ID")
    READ_MANUFACTURER_ID_OPCODE = 0x9F
    data = [READ_MANUFACTURER_ID_OPCODE]                    # Read Manufacturer ID opcode
    read_length = 4                                         # Manufacturer ID consists of 4 bytes of data
    transfer_length = len(data) + read_length               # Transfer length is the total of instruction length and read length
    (success, response) = spi_controller.transfer(data, transfer_length)
    if success:
        printable = [f'{value:#04x}' for value in response]
        print(f"Received data: {printable}")
    else:
        print("Couldn't transfer data")
    
    # Enable write operation
    print("Enabling write operation")
    WREN_OPCODE = 0x06
    data = [WREN_OPCODE]                                    # Write Enable (WREN) opcode
    transfer_length = len(data)                             # In this case the length is just the length of the instruction
    (success, _) = spi_controller.transfer(data, transfer_length)
    if success:
        print(f"Write operation enable")
    else:
        print("Couldn't transfer data")

    # Write operation
    print("Writing [0x2A 0x2B] to 0x0000 memory address")
    WRITE_OPCODE = 0x02
    instruction = [WRITE_OPCODE, 0x00, 0x00]                # Write operation opcode and memory address
    data_to_write = [0x2A, 0x3B]                            # Data to be written in the memory
    data = instruction + data_to_write
    transfer_length = len(data)                              # Transfer length is the total of the instruction length and data to write length
    (success, _) = spi_controller.transfer(data, transfer_length)
    if success:
        print(f"Write operation completed successfully")
    else:
        print("Couldn't transfer data")

    # Read operation
    print("Reading 0x0000 memory address")
    READ_OPCODE = 0x03
    data = [READ_OPCODE, 0x00, 0x00]                        # Read operation opcode and memory address
    read_length = 2                                         # Length of byte to be read
    transfer_length = len(data) + read_length               # Transfer length is the total of the instruction length and read length
    (success, response) = spi_controller.transfer(data, transfer_length)
    if success:
        printable = [f'{value:#04x}' for value in response]
        print(f"Received data: {printable}")
    else:
        print("Couldn't transfer data")

    miso_idle = [0,0,0]                                     # The first 3 bytes in the miso line correspond to the instruction transfer so are in IDLE state
    expected_response = miso_idle + data_to_write           # The response consists of all the miso data since the start of the transfer
    if response == expected_response:
        print("Data written and read match correctly")
    else:
        print("Inconsistency between what was read and what was sent")

    device.close()

if __name__ == "__main__":
    main()