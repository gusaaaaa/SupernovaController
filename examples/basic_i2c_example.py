from supernovacontroller.sequential import SupernovaDevice

def main():

    device = SupernovaDevice()
    print("Opening Supernova host adapter device and getting access to the I2C protocol interface...")
    info = device.open()
    i2c = device.create_interface("i2c")
    print(info)

    print("Initializing the bus...")
    (success, _) = i2c.init_bus(3300)
    if not success:
        print("I couldn't initialize the bus. Are you sure there's any target connected?")
        exit(1)

    success, result = i2c.set_parameters(400000)
    if not success:
        print(f"Operation failed with error: {result}")
    print(f"Frequency set in: {result} Hz")

    # Write data
    success, result = i2c.write(0x50, [0x00, 0x00], [33 for i in range(1,129)])
    if not success:
        print(f"Operation failed with error: {result}")
    print(f"Write operation result: {result} ")

    # Write sub-address before reading
    success, result = i2c.write(0x50, [0x00, 0x00], [0x00, 0x00]) 
    if not success:
        print(f"Operation failed with error: {result}")
    print(f"Write operation result: {result} ")

    # Read data
    success, result = i2c.read(0x50, 20)
    if not success:
        print(f"Operation failed with error: {result}")
    print(f"Read operation result: {result} ")

    # Read data specifying register
    success, result = i2c.read_from(0x50, [0x00, 0x00], 20)
    if not success:
        print(f"Operation failed with error: {result}")
    print(f"Read from operation result: {result} ")

    # Write non-stop to address
    success, result = i2c.write_non_stop(0x50, [0x01, 0x00], [255 for i in range(0,20)])
    if not success:
        print(f"Operation failed with error: {result}")
    print(f"Write Non-Stop from operation result: {result} ")

    # Read data specifying register
    success, result = i2c.read_from(0x50, [0x01, 0x00], 20)
    if not success:
        print(f"Operation failed with error: {result}")
    print(f"Read from operation result: {result} ")

    device.close()

if __name__ == "__main__":
    main()
