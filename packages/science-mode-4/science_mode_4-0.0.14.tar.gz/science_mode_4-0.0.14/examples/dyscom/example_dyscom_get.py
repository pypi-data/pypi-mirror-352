"""Provides an example how to use dyscom layer get commands"""

import sys
import asyncio

from science_mode_4 import SerialPortConnection
from science_mode_4 import DeviceI24
from examples.utils.example_utils import ExampleUtils


async def main() -> int:
    """Main function"""

    # get comport from command line argument
    com_port = ExampleUtils.get_comport_from_commandline_argument()
    # create serial port connection
    connection = SerialPortConnection(com_port)
    # open connection, now we can read and write data
    connection.open()

    # create science mode device
    device = DeviceI24(connection)
    # call initialize to get basic information (serial, versions) and stop any active stimulation/measurement
    # to have a defined state
    await device.initialize()

    # get general layer to access general commands
    general = device.get_layer_general()
    # get dyscom layer to access dyscom commands
    dyscom = device.get_layer_dyscom()

    #####
    # dyscom layer provides a get command for device id, it is redundant to general layer device id
    # both values should be identical
    device_id = await dyscom.get_device_id()
    print(f"Device id from general layer: {general.device_id}, from dyscom layer: {device_id}")

    #####
    # dyscom layer provides a get command for firmware version, it is redundant to general layer firmware verion
    # both values should be identical
    firmware_version = await dyscom.get_firmware_version()
    print(f"Firmware version from general layer: {general.firmware_version}, from dyscom layer: {firmware_version}")

    #####
    # get command for file system status
    file_system_status = await dyscom.get_file_system_status()
    print(file_system_status)

    ####
    calibration_filename = f"rehaingest_{device_id}.cal"
    # get calibration file info
    await dyscom.get_file_info(calibration_filename)
    # get calibration file -> does not work
    # there should be DL_Send_File commands afterwards
    await dyscom.get_file_by_name(calibration_filename)

    # close serial port connection
    connection.close()
    return 0


if __name__ == "__main__":
    res = asyncio.run(main())
    sys.exit(res)
