from supernovacontroller.sequential import SupernovaDevice
from BinhoSupernova.commands.definitions import UartControllerBaudRate
from BinhoSupernova.commands.definitions import UartControllerParity
from BinhoSupernova.commands.definitions import UartControllerDataSize
from BinhoSupernova.commands.definitions import UartControllerStopBit

def main():
    """
    Basic example to illustrate UART protocol usage with SupernovaController.

    In this example we initialize the UART peripheral with the following parameters:
        Baudrate: 9600 bps
        Parity: No Parity
        Data size: 8 bit data
        Stop bit for framing: 1 stop bit
        Hardware handshake (RTS/CTS): disabled

    Then the baudrate is changed to 115200bps
    With this configuration a data package is sent and then it starts an echo mode. You can use any serial UART device to write
    to the Supernova and it will echo it back.
    """
    device = SupernovaDevice()

    print("Opening Supernova host adapter device and getting access to the UART protocol interface...")
    info = device.open()
    uart = device.create_interface("uart")

    print("Initializing UART peripheral.")
    (success, _) = uart.set_bus_voltage(3300)
    if not success:
        print("Couldn't set the UART bus voltage.")
        exit(1)

    (success, _) = uart.init_bus()
    if not success:
        print("Couldn't initialize UART peripheral.")
        exit(1)

    # Change baudrate to 115200bps
    print("Changing the baudrate to 115200bps.")
    (success, response) = uart.set_parameters(baudrate = UartControllerBaudRate.UART_BAUD_115200)
    if not success:
        print("Couldn't set the UART parameters correctly.")
        exit(1)

    (success, response) = uart.get_parameters()
    if success:
        print(f"The configured parameters are:")
        print(f"Baudrate: {response[0].name}, Parity: {response[1].name}, Data Size: {response[2].name}, Stop Bit: {response[3].name}, Hardware Handshake: {response[4]}")
    else:
        print("Failed to retrieve UART parameters.")

    # Send data over UART
    data = [0x00, 0x01, 0x02, 0x3, 0x04, 0x05, 0x06]
    uart.send(data)
    print(f"Sent data: {data}")

    # Send 0x00 to end data transmission
    print("Entering echo mode, send 0x00 to end.")
    while (data != [0x00]):
        (success, data) = uart.wait_for_notification(None)
        print(f"Received data: {data}")
        uart.send(data)
        print(f"Sent data: {data}")

if __name__ == "__main__":
    main()