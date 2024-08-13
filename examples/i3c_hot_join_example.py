from supernovacontroller.sequential import SupernovaDevice
from threading import Event

hot_join_event = Event()

def main():
    device = SupernovaDevice()

    print("Connecting to Supernova device")
    info = device.open()

    print("Initializing and setting up the I3C peripheral")
    i3c = device.create_interface("i3c.controller")
    i3c.set_parameters(i3c.I3cPushPullTransferRate.PUSH_PULL_12_5_MHZ, i3c.I3cOpenDrainTransferRate.OPEN_DRAIN_4_17_MHZ)
    (success, _) = i3c.init_bus(1200)

    if success == False:
        print("No targets joined the I3C bus via the ENTDAA CCC")
    else:
        (_, targets) = i3c.targets()
        print(f"The targets added via the ENTDAA CCC are: {targets}")

    # Add hot-join procedure filter and handler
    def is_hot_join(name, message):
        return message['name'].strip() == "I3C IBI NOTIFICATION" and message['header']['type'] == "IBI_HOT_JOIN"
    
    def handle_hot_join(name, message): 
        new_target = {'dynamic_address': message['header']['address'], 'bcr': message['bcr'], 'dcr': message['dcr'], 'pid': message['pid']}
        print(f"NOTIFICATION: New device added via hot-join procedure -> {new_target}")
        hot_join_event.set()

    device.on_notification(name="hot-join", filter_func=is_hot_join, handler_func=handle_hot_join)

    # Wait for hot-join procedure
    # This approach eliminates the need for an infinite loop. If you prefer an alternative method that allows you to perform other tasks concurrently 
    # while waiting for the hot-join procedure, you can replace the usage of "hot_join_event" with your custom code to achieve non-blocking behavior. 
    hot_join_event.wait()
    
    # Show the device table after the hot-join
    (_, targets) = i3c.targets()
    print(f"The target table is: {targets}")


if __name__ == "__main__":
    main()