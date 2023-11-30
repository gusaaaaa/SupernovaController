from supernovacontroller.sequential import SupernovaDevice

# Function to find the first item with the matching PID
def find_matching_item(data, target_pid):
    for item in data:
        if item.get('pid') == target_pid:
            return item
    return None

def main():
    device = SupernovaDevice()

    info = device.open()

    i3c = device.create_interface("i3c.controller")

    i3c.set_parameters(i3c.I3cPushPullTransferRate.PUSH_PULL_12_5_MHZ, i3c.I3cOpenDrainTransferRate.OPEN_DRAIN_4_17_MHZ)
    (success, _) = i3c.init_bus(3300)

    if not success:
        print("I couldn't initialize the bus. Are you sure there's any target connected?")
        exit(1)

    (_, targets) = i3c.targets()

    # Target PID in hexadecimal format
    target_pid = [0x04, 0x6A, 0x00, 0x00, 0x00, 0x00]

    icm_device = find_matching_item(targets, target_pid)

    if icm_device is None:
        print("ICM device not found in the I3C bus")
        exit(1)

    print(icm_device)

    target_address = icm_device["dynamic_address"]
    print("Address: ", target_address)

    # ---
    # CCC Transfers
    # ---
    result = i3c.ccc_getpid(target_address)
    print(result)
    result = i3c.ccc_getbcr(target_address)
    print(result)
    result = i3c.ccc_getdcr(target_address)
    print(result)
    result = i3c.ccc_getcaps(target_address)
    print(result)
    result = i3c.ccc_getmxds(target_address)
    print(result)
    result = i3c.ccc_getmrl(target_address)
    print(result)
    result = i3c.ccc_unicast_setmrl(target_address, 1024)
    print(result)
    result = i3c.ccc_broadcast_setmrl(64)
    print(result)
    result = i3c.ccc_getmwl(target_address)
    print(result)
    result = i3c.ccc_unicast_setmwl(target_address, 80)
    print(result)
    result = i3c.ccc_broadcast_setmwl(256)
    print(result)

    # ---
    # Write/Read transfers
    # ---
    result = i3c.write(target_address, i3c.TransferMode.I3C_SDR, [0x16], [0x40])
    result = i3c.read(target_address, i3c.TransferMode.I3C_SDR, [0x16], 2)

    device.close()


if __name__ == "__main__":
    main()