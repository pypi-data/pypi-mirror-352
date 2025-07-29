"""Test program how to use library without installing the library,
DO NOT USE THIS FILE, USE EXAMPLES INSTEAD"""

import logging
import sys
import asyncio

from science_mode_4.device_i24 import DeviceI24
from science_mode_4.dyscom.dyscom_get_file_by_name import PacketDyscomGetAckFileByName
from science_mode_4.dyscom.dyscom_get_operation_mode import PacketDyscomGetAckOperationMode
from science_mode_4.dyscom.dyscom_layer import LayerDyscom
from science_mode_4.dyscom.dyscom_send_file import PacketDyscomSendFile
from science_mode_4.dyscom.dyscom_types import DyscomGetType
from science_mode_4.protocol.commands import Commands
from science_mode_4.utils import logger
from science_mode_4.utils.serial_port_connection import SerialPortConnection



async def main() -> int:
    """Main function"""

    # logger().disabled = True
    logger().setLevel(logging.DEBUG)

    devices = SerialPortConnection.list_science_mode_device_ports()
    connection = SerialPortConnection(devices[0].device)
    # devices = UsbConnection.list_science_mode_devices()
    # connection = UsbConnection(devices[0])
    # connection = NullConnection()
    connection.open()

    device = DeviceI24(connection)
    await device.initialize()

    general = device.get_layer_general()
    await general.get_version()
    # get dyscom layer to call dyscom level commands
    dyscom = device.get_layer_dyscom()

    device_id = await dyscom.get_device_id()

    # await dyscom.power_module(DyscomPowerModuleType.MEMORY_CARD, DyscomPowerModulePowerType.SWITCH_ON)
    # await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_ON)
    # params = DyscomInitParams()
    # params.flags = [DyscomInitFlag.ENABLE_SD_STORAGE_MODE]
    # init_ack = await dyscom.init(params)

    # dyscom.send_start()
    # await asyncio.sleep(1)
    # dyscom.send_get_operation_mode()
    # await asyncio.sleep(4)
    # dyscom.send_stop()
    # await asyncio.sleep(5)
    # process_ack(dyscom)

    # mmi = await dyscom.get_list_of_measurement_meta_info()

    # # get calibration file
    calibration_filename = f"rehaingest_{device_id}.cal"
    await dyscom.get_file_info(calibration_filename)

    # p = PacketDyscomGetFileByName(calibration_filename)
    # dyscom.send_packet(p)
    await dyscom.get_file_by_name(calibration_filename)

    # dyscom.send_send_file(get_file_by_name_ack.block_offset)
    # for x in range(get_file_by_name_ack.number_of_blocks):
    #     dyscom.send_send_file(get_file_by_name_ack.block_offset + x)

    # meas_info = await dyscom.get_file_info(init_ack.measurement_file_id)
    # await dyscom.get_operation_mode()

    # p = PacketDyscomGetFileByName(init_ack.measurement_file_id)
    # dyscom.send_packet(p)
    # dyscom.send_get_operation_mode()
    # get_file_by_name_ack = await dyscom.get_file_by_name(init_ack.measurement_file_id)
    # await dyscom.get_operation_mode()

    await asyncio.sleep(5)
    offset = process_ack(dyscom)
    dyscom.send_send_file(offset)
    await asyncio.sleep(5)
    process_ack(dyscom)

    connection.close()

    return 0

def process_ack(dyscom: LayerDyscom) -> int:
    """Process all packets read from connection buffer"""
    offset = 0
    while True:
        # process all available packages
        ack = dyscom.packet_buffer.get_packet_from_buffer()
        print(ack)
        if ack:
            if ack.command == Commands.DL_SEND_FILE:
                send_file: PacketDyscomSendFile = ack
                data = send_file.data
                print(data)
            elif ack.command == Commands.DL_GET_ACK and ack.kind == DyscomGetType.OPERATION_MODE:
                op_mode: PacketDyscomGetAckOperationMode = ack
                print(op_mode.operation_mode.name)
            elif ack.command == Commands.DL_GET_ACK and ack.kind == DyscomGetType.FILE_BY_NAME:
                fbn: PacketDyscomGetAckFileByName = ack
                print(fbn.block_offset)
                offset = fbn.block_offset
        else:
            break

    return offset


if __name__ == "__main__":
    res = asyncio.run(main())
    sys.exit(res)
