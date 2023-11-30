from supernovacontroller.sequential import SupernovaDevice

# Function to find the first item with the matching PID
def find_matching_item(data, target_pid):
    for item in data:
        if item.get('pid') == target_pid:
            return item
    return None

def main():
    """
    Basic example to illustrate i3c protocol usage with SupernovaController.
    
    Sequence of commands:
    - Initialize the Device: Creates and opens a connection to Supernova host adapter.
    - Create I3C Interface: Creates an I3C interface for communication.
    - Set I3C Parameters and Initialize Bus: Sets transfer rates and initializes the I3C bus with a specific voltage level.
    - Discover Targets on I3C Bus: Fetches a list of devices present on the I3C bus.
    - Find Specific ICM Device: Uses find_matching_item to find a specific device based on its PID.
    - Perform CCC (Common Command Code) Transfers: Sends various CCC commands to the target device to get or set parameters.
    - Write/Read Transfers: Demonstrates write and read operations over the I3C bus.
    - Reset I3C Bus and Targets: Resets the bus and fetches the target list again.
    - Close Device Connection: Closes the connection to the Supernova device.
    """
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
    print(result[1])
    result = i3c.ccc_getbcr(target_address)
    print(result[1])
    result = i3c.ccc_getdcr(target_address)
    print(result[1])
    result = i3c.ccc_getcaps(target_address)
    print(result[1])
    result = i3c.ccc_getmxds(target_address)
    print(result[1])
    result = i3c.ccc_getmrl(target_address)
    print(result[1])
    result = i3c.ccc_unicast_setmrl(target_address, 1024)
    print(result[1])
    result = i3c.ccc_broadcast_setmrl(64)
    print(result[1])
    result = i3c.ccc_getmwl(target_address)
    print(result[1])
    result = i3c.ccc_unicast_setmwl(target_address, 80)
    print(result[1])
    result = i3c.ccc_broadcast_setmwl(256)
    print(result[1])

    # ---
    # Write/Read transfers
    # ---
    result = i3c.write(target_address, i3c.TransferMode.I3C_SDR, [0x16], [0x40])
    print(result[1])
    result = i3c.read(target_address, i3c.TransferMode.I3C_SDR, [0x16], 2)
    print(result[1])

    # ---
    # Target reset
    # ---
    result = i3c.reset_bus()
    print(result[1])
    result = i3c.targets()
    print(result[1])

    device.close()

if __name__ == "__main__":
    main()