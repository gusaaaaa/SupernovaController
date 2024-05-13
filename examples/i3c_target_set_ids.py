from supernovacontroller.sequential import SupernovaDevice
from BinhoSupernova.commands.definitions import DdrOk
from BinhoSupernova.commands.definitions import (I3cTargetMemoryLayout_t, I3cTargetMaxDataSpeedLimit_t, I3cTargetIbiCapable_t, I3cTargetIbiPayload_t, 
                                                 I3cTargetOfflineCap_t, I3cTargetVirtSupport_t, I3cTargetDeviceRole_t, I3cTargetDcr_t, I3cBcrRegister_t,
                                                 IgnoreTE0TE1Errors, MatchStartStop, AlwaysNack)

def main():
    """
    Example to test setting of IDs for the Supernova as an I3C target  with SupernovaController.
    With two Supernovas connected between them via the HV bus, one is initalized as an I3C controller and the other
    one as an I3C target. The target acts as a memory with 1024 registers of 1 bytes size
    
    Sequence of commands:
    - Initialize the Devices and create its interfaces: 
      Create and open a connection to the Supernova host adapter for both the I3C controller and the I3C target.
      Create an I3C interface for communication with both the I3C controller and the I3C target.
    - Initialize the I3C peripheral of the target: 
      Init the peripheral of one Supernova as an I3C target with a memory layout of 1024 registers of 1 byte size.
    - Set the target PID, BCR, DCR and static address.
    - Initialize the I3C peripheral of the controller. 
    - Set I3C Parameters and initialize the Bus: Set transfer rates and initialize the I3C bus with a specific voltage level.
      For this specific example, the bus initialization assigns the dynamic addresses using an RSTDAA + ENTDAA.
    - Discover Targets on I3C Bus: Fetch a list of devices present on the I3C bus.
    - Assign dynamic addresses using RSTDAA and SETDASA.
    - Close Device Connection: Close the connection to the Supernova devices.
    """

    print("-----------------------")
    print("Initialize Supernovas")
    print("-----------------------")

    target_device = SupernovaDevice()
    info = target_device.open(usb_address ="\\\\?\\HID#VID_1FC9&PID_82FC#6&bb45e52&1&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}")
    i3c_target = target_device.create_interface("i3c.target")

    controller_device = SupernovaDevice()
    info = controller_device.open(usb_address ="\\\\?\\HID#VID_1FC9&PID_82FC#7&f321146&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}")
    i3c_controller = controller_device.create_interface("i3c.controller")

    print("--------------------------------------------------------------------------------------------------------")
    print("Initialize the target peripheral as a memory of 1024 registers of 1 byte size")
    print("--------------------------------------------------------------------------------------------------------")

    MEMORY_LAYOUT               = I3cTargetMemoryLayout_t.MEM_1_BYTE
    USECONDS_TO_WAIT_FOR_IBI    = 0x69
    MRL                         = 0x100
    MWL                         = 0x100
    TARGET_CONF                 = DdrOk.ALLOWED_DDR.value |  \
                                  IgnoreTE0TE1Errors.IGNORE_ERRORS.value |  \
                                  MatchStartStop.NOT_MATCH.value |  \
                                  AlwaysNack.NOT_ALWAYS_NACK.value    
    
    success, status = i3c_target.target_init(MEMORY_LAYOUT, USECONDS_TO_WAIT_FOR_IBI, MRL, MWL, TARGET_CONF)
    print("Target initialized correctly" if success else "Could not initialize the target")

    print("--------------------------------------------------------------------------------------------------------")
    print("Set the target Supernova PID, BCR, DCR and static address")
    print("--------------------------------------------------------------------------------------------------------")

    PID_TO_SET = [0x02, 0x03, 0x04, 0x05, 0x06, 0x07]
    success, status = i3c_target.set_pid(PID_TO_SET)
    print(f"PID {PID_TO_SET} assigned successfully." if success else "Could not assign the PID")

    success, status = i3c_target.set_bcr(I3cTargetMaxDataSpeedLimit_t.MAX_DATA_SPEED_LIMIT, I3cTargetIbiCapable_t.NOT_IBI_CAPABLE, 
                                         I3cTargetIbiPayload_t.IBI_WITH_PAYLOAD, I3cTargetOfflineCap_t.OFFLINE_CAPABLE, 
                                         I3cTargetVirtSupport_t.VIRTUAL_TARGET_SUPPORT, I3cTargetDeviceRole_t.I3C_TARGET)
    
    BCR_TO_SET = I3cBcrRegister_t() 
    BCR_TO_SET.bits.maxDataSpeedLimitation = I3cTargetMaxDataSpeedLimit_t.MAX_DATA_SPEED_LIMIT.value
    BCR_TO_SET.bits.ibiRequestCapable = I3cTargetIbiCapable_t.NOT_IBI_CAPABLE.value
    BCR_TO_SET.bits.ibiPayload = I3cTargetIbiPayload_t.IBI_WITH_PAYLOAD.value
    BCR_TO_SET.bits.offlineCapable = I3cTargetOfflineCap_t.OFFLINE_CAPABLE.value
    BCR_TO_SET.bits.virtualTargetSupport = I3cTargetVirtSupport_t.VIRTUAL_TARGET_SUPPORT.value
    BCR_TO_SET.bits.deviceRole = I3cTargetDeviceRole_t.I3C_TARGET.value
    # Shift value to set BCR[5] based on ddrOk field from I3cTargetFeatures_t 
    # (BCR[5] indicates if HDR is activated, this flag is set during initialization when the target configuration is modified)
    SHIFT_CONVERSION = 3
    BCR_TO_SET = BCR_TO_SET.byte | ((TARGET_CONF & DdrOk.ALLOWED_DDR.value) << SHIFT_CONVERSION)
    print(f"BCR {BCR_TO_SET} assigned successfully" if success else "Could not assign the BCR")

    DCR_TO_SET = I3cTargetDcr_t.I3C_TARGET_MEMORY
    success, status = i3c_target.set_dcr(DCR_TO_SET)
    print(f"DCR {DCR_TO_SET.value} assigned successfully" if success else "Could not assign the DCR")

    STATIC_ADDR_TO_SET = 0x73
    success, status = i3c_target.set_static_address(STATIC_ADDR_TO_SET)
    print(f"Static address {STATIC_ADDR_TO_SET} assigned successfully" if success else "Could not assign the Static address")

    print("--------------------------------------------------------------------------------------------------------")
    print("Initialize controller peripheral")
    print("--------------------------------------------------------------------------------------------------------")

    success, status = i3c_controller.controller_init()
    print("Controller initialized correctly" if success else "Could not initialize the controller")

    print("------------------------------------")
    print("Bus initialization with ENTDAA")
    print("------------------------------------")

    i3c_controller.set_parameters(i3c_controller.I3cPushPullTransferRate.PUSH_PULL_5_MHZ, i3c_controller.I3cOpenDrainTransferRate.OPEN_DRAIN_1_25_MHZ)
    (success, _) = i3c_controller.init_bus(3300)
    if success:
        print("Bus successfully initialized with ENTDAA")
    else:
        print("Bus initialization fail. Make sure that there is at least one target connected")
        exit(1)

    (_, targets) = i3c_controller.targets()
    
    print("Targets found during intialization:",targets)

    print("------------------------------------")
    print("Bus initialization with SETDASA")
    print("------------------------------------")

    (success, _) = i3c_controller.reset_bus()
    print("Bus reset correctly" if success else "Could not reset the bus")

    (success, _) = i3c_controller.ccc_setdasa(0x73, 0x0A)
    print("SETDASA run successfully" if success else "SETDASA could not run successfully")

    print("-------------------------------------------------------")
    print("CLOSE CONNECTION TO SUPERNOVAS")
    print("-------------------------------------------------------")

    controller_device.close()
    target_device.close()

if __name__ == "__main__":
    main()
