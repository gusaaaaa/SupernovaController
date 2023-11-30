from supernovacontroller.sequential import SupernovaDevice


def main():
    device = SupernovaDevice()

    device.open()

    i2c = device.create_interface("i2c")

    (success, result) = i2c.set_parameters(3300, 400000)

    (success, _) = i2c.write(0x50, [0x00,0x00], [0xDE, 0xAD, 0xBE, 0xEF])
    print(success)
    value = i2c.read_from(0x50, [0x00,0x00], 4)
    print(success)
    print(value)

    i3c = device.create_interface("i3c.controller")

    i3c.set_parameters(i3c.I3cPushPullTransferRate.PUSH_PULL_12_5_MHZ, i3c.I3cOpenDrainTransferRate.OPEN_DRAIN_4_17_MHZ)
    (success, _) = i3c.init_bus(3300)

    if not success:
        print("I couldn't initialize the bus. Are you sure there's any target connected?")
        exit(1)

    (_, targets) = i3c.targets()

    print(targets)

    device.close()


if __name__ == "__main__":
    main()
