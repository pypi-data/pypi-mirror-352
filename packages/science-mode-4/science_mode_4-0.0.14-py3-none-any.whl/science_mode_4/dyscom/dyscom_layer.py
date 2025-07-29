"""Provides low level layer"""

from science_mode_4.layer import Layer
from science_mode_4.utils.logger import logger
from .dyscom_types import DyscomGetOperationModeType, DyscomPowerModuleType, DyscomPowerModulePowerType, DyscomSysType
from .dyscom_init import DyscomInitResult, PacketDyscomInit, PacketDyscomInitAck, DyscomInitParams
from .dyscom_get_file_system_status import PacketDyscomGetFileSystemStatus, PacketDyscomGetAckFileSystemStatus,\
    DyscomGetFileSystemStatusResult
from .dyscom_get_file_by_name import PacketDyscomGetFileByName, PacketDyscomGetAckFileByName, DyscomGetFileByNameResult
from .dyscom_get_firmware_version import PacketDyscomGetFirmwareVersion, PacketDyscomGetAckFirmwareVersion
from .dyscom_get_operation_mode import PacketDyscomGetOperationMode, PacketDyscomGetAckOperationMode
from .dyscom_start import PacketDyscomStart, PacketDyscomStartAck
from .dyscom_stop import PacketDyscomStop, PacketDyscomStopAck
from .dyscom_power_module import PacketDyscomPowerModule, PacketDyscomPowerModuleAck, DyscomPowerModuleResult
from .dyscom_get_list_of_measurement_meta_info import PacketDyscomGetAckListOfMeasurementMetaInfo, PacketDyscomGetListOfMeasurementMetaInfo
from .dyscom_get_device_id import PacketDyscomGetAckDeviceId, PacketDyscomGetDeviceId
from .dyscom_get_file_info import DyscomGetFileInfoResult, PacketDyscomGetAckFileInfo, PacketDyscomGetFileInfo
from .dyscom_get_battery_status import DyscomGetBatteryResult, PacketDyscomGetAckBatteryStatus, PacketDyscomGetBatteryStatus
from .dyscom_sys import DyscomSysResult, PacketDyscomSys, PacketDyscomSysAck
from .dyscom_send_file import PacketDyscomSendFile


class LayerDyscom(Layer):
    """
    Class for dyscom layer
    """


    async def init(self, params: DyscomInitParams) -> DyscomInitResult:
        """Send dyscom init command and waits for response"""
        p = PacketDyscomInit(params)
        ack: PacketDyscomInitAck = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomInit")
        logger().info("Dyscom init, measurement_file_id: %s, state: %s, frequency: %s",\
                      ack.measurement_file_id, ack.init_state.name, ack.frequency_out.name)
        return DyscomInitResult(ack.register_map_ads129x, ack.measurement_file_id, ack.init_state, ack.frequency_out)


    async def get_file_system_status(self) -> DyscomGetFileSystemStatusResult:
        """Sends dyscom get type file system status and waits for response, returns file system ready, used size and free size"""
        p = PacketDyscomGetFileSystemStatus()
        ack: PacketDyscomGetAckFileSystemStatus = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetFileSystemStatus")
        logger().info("Dyscom get file system status, ready: %s, used size: %d, free size: %s",\
                      ack.file_system_ready, ack.used_size, ack.free_size)
        return DyscomGetFileSystemStatusResult(ack.file_system_ready, ack.used_size, ack.free_size)


    async def get_list_of_measurement_meta_info(self) -> int:
        """Sends dyscom get type list of measurement meta info and waits for response, returns number of measurements"""
        p = PacketDyscomGetListOfMeasurementMetaInfo()
        ack: PacketDyscomGetAckListOfMeasurementMetaInfo = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetListOfMeasurementMetaInfo")
        logger().info("Dyscom get list of mmi, number of measurements: %d", ack.number_of_measurements)
        return ack.number_of_measurements


    async def get_file_by_name(self, filename: str) -> DyscomGetFileByNameResult:
        """Sends dyscom get type file by name and waits for response, returns filename, block offset,
        filesize, number of blocks and mode"""
        p = PacketDyscomGetFileByName(filename)
        ack: PacketDyscomGetAckFileByName = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetFileByName")
        logger().info("Dyscom get file by name, filename: %s, block offset: %d, filesize: %d, number of blocks: %d, mode: %s",\
                      ack.filename, ack.block_offset, ack.filesize, ack.number_of_blocks, ack.mode.name)
        return DyscomGetFileByNameResult(ack.filename, ack.block_offset, ack.filesize, ack.number_of_blocks, ack.mode)


    async def get_device_id(self) -> str:
        """Sends dyscom get type device id and waits for response, returns device id"""
        p = PacketDyscomGetDeviceId()
        ack: PacketDyscomGetAckDeviceId = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetDeviceId")
        logger().info("Dyscom get device id: %s", ack.device_id)
        return ack.device_id


    async def get_firmware_version(self) -> str:
        """Sends dyscom get type firmware version and waits for response, returns firmware version"""
        p = PacketDyscomGetFirmwareVersion()
        ack: PacketDyscomGetAckFirmwareVersion = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetFirmwareVersion")
        logger().info("Dyscom get firmware version: %s", ack.firmware_version)
        return ack.firmware_version


    async def get_file_info(self, filename: str) -> DyscomGetFileInfoResult:
        """Sends dyscom get type file by name and waits for response, returns filename, block offset, filesize and number of blocks"""
        p = PacketDyscomGetFileInfo(filename)
        ack: PacketDyscomGetAckFileInfo = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetFileInfo")
        logger().info("Dyscom get file info, filename: %s, filesize: %d, checksum: %d",\
                      ack.filename, ack.filesize, ack.checksum)
        return DyscomGetFileInfoResult(ack.filename, ack.filesize, ack.checksum)


    async def get_battery(self) -> DyscomGetBatteryResult:
        """Sends dyscom get type batter and waits for response, returns voltage, current, percentage, temperature and energy state"""
        p = PacketDyscomGetBatteryStatus()
        ack: PacketDyscomGetAckBatteryStatus = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetBatteryStatus")
        logger().info("Dyscom get battery, voltage: %d, current: %d, percentage: %d, temperature: %d, energy state: %s",\
                      ack.voltage, ack.current, ack.percentage, ack.temperature, ack.energy_state)
        return DyscomGetBatteryResult(ack.voltage, ack.current, ack.percentage, ack.temperature, ack.energy_state)


    async def get_operation_mode(self) -> DyscomGetOperationModeType:
        """Sends dyscom get type operation mode and waits for response, returns operation mode"""
        p = PacketDyscomGetOperationMode()
        ack: PacketDyscomGetAckOperationMode = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetFirmwareVersion")
        logger().info("Dyscom get operation mode: %s", ack.operation_mode.name)
        return ack.operation_mode


    def send_get_operation_mode(self):
        """Sends dyscom get type operation mode and returns immediately without waiting for response"""
        p = PacketDyscomGetOperationMode()
        logger().info("Dyscom send get operation mode")
        self.send_packet(p)


    async def power_module(self, module: DyscomPowerModuleType, power: DyscomPowerModulePowerType) -> DyscomPowerModuleResult:
        """Sends dyscom power module and waits for response, returns module and power"""
        p = PacketDyscomPowerModule(module, power)
        ack: PacketDyscomPowerModuleAck = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomStart")
        logger().info("Dyscom power module, module: %s, power: %s", ack.module.name, ack.power.name)
        return DyscomPowerModuleResult(ack.module, ack.power)


    async def sys(self, sys_type: DyscomSysType, filename: str = "") -> DyscomSysResult:
        """Sends dyscom sys and waits for response, returns type, state and filename"""
        p = PacketDyscomSys(sys_type, filename)
        ack: PacketDyscomSysAck = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomSys")
        logger().info("Dyscom sys, type: %s, state: %s, filename: %s", ack.sys_type.name, ack.state.name, ack.filename)
        return DyscomSysResult(ack.sys_type, ack.state, ack.filename)


    def send_send_file(self, block_number: int):
        """Sends dyscom send file ack and returns immediately without waiting for response"""
        logger().info("Dyscom send file ack, block_number: %d", block_number)
        p = PacketDyscomSendFile(block_number)
        self.send_packet(p)


    async def start(self):
        """Sends dyscom start and waits for response"""
        p = PacketDyscomStart()
        ack: PacketDyscomStartAck = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomStart")
        logger().info("Dyscom start")


    async def stop(self):
        """Sends dyscom stop and waits for response"""
        p = PacketDyscomStop()
        ack: PacketDyscomStopAck = await self.send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomStop")
        logger().info("Dyscom stop")


    def send_start(self):
        """Sends dyscom start and returns immediately without waiting for response"""
        logger().info("Dyscom start")
        p = PacketDyscomStart()
        self.send_packet(p)


    def send_stop(self):
        """Sends dyscom stop and returns immediately without waiting for response"""
        logger().info("Dyscom stop")
        p = PacketDyscomStop()
        self.send_packet(p)
