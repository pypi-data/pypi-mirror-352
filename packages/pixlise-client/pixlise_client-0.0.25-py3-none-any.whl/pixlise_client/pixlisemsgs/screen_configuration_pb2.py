"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import ownership_access_pb2 as ownership__access__pb2
from . import widget_data_pb2 as widget__data__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1ascreen-configuration.proto\x1a\x16ownership-access.proto\x1a\x11widget-data.proto"G\n\x16ScreenConfigurationCSS\x12\x17\n\x0ftemplateColumns\x18\x01 \x01(\t\x12\x14\n\x0ctemplateRows\x18\x02 \x01(\t"(\n\x16ScreenConfigurationRow\x12\x0e\n\x06height\x18\x01 \x01(\x05"*\n\x19ScreenConfigurationColumn\x12\r\n\x05width\x18\x01 \x01(\x05"\x9a\x01\n\x19WidgetLayoutConfiguration\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\x10\n\x08startRow\x18\x03 \x01(\x05\x12\x13\n\x0bstartColumn\x18\x04 \x01(\x05\x12\x0e\n\x06endRow\x18\x05 \x01(\x05\x12\x11\n\tendColumn\x18\x06 \x01(\x05\x12\x19\n\x04data\x18\x07 \x01(\x0b2\x0b.WidgetData"\xe9\x01\n\x10FullScreenLayout\x12\r\n\x05tabId\x18\x01 \x01(\t\x12\x0f\n\x07tabName\x18\x02 \x01(\t\x12\x16\n\x0etabDescription\x18\x03 \x01(\t\x12\x0c\n\x04tags\x18\x07 \x03(\t\x12\x0e\n\x06hidden\x18\x08 \x01(\x08\x12%\n\x04rows\x18\x04 \x03(\x0b2\x17.ScreenConfigurationRow\x12+\n\x07columns\x18\x05 \x03(\x0b2\x1a.ScreenConfigurationColumn\x12+\n\x07widgets\x18\x06 \x03(\x0b2\x1a.WidgetLayoutConfiguration"W\n\x1cScanCalibrationConfiguration\x12\x0f\n\x07eVstart\x18\x01 \x01(\x01\x12\x14\n\x0ceVperChannel\x18\x02 \x01(\x01\x12\x10\n\x08detector\x18\x03 \x01(\t"u\n\x11ScanConfiguration\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07quantId\x18\x02 \x01(\t\x123\n\x0ccalibrations\x18\x03 \x03(\x0b2\x1d.ScanCalibrationConfiguration\x12\x0e\n\x06colour\x18\x04 \x01(\t"\xf3\x03\n\x13ScreenConfiguration\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0bdescription\x18\x03 \x01(\t\x12\x17\n\x0fbrowseTabHidden\x18\x0b \x01(\x08\x12\x1b\n\x13codeEditorTabHidden\x18\x0c \x01(\x08\x12\x1c\n\x14elementMapsTabHidden\x18\r \x01(\x08\x12"\n\x07layouts\x18\x04 \x03(\x0b2\x11.FullScreenLayout\x12\x0c\n\x04tags\x18\x07 \x03(\t\x12\x17\n\x0fmodifiedUnixSec\x18\x08 \x01(\r\x12H\n\x12scanConfigurations\x18\t \x03(\x0b2,.ScreenConfiguration.ScanConfigurationsEntry\x12 \n\x05owner\x18\n \x01(\x0b2\x11.OwnershipSummary\x12\x18\n\x10snapshotParentId\x18\x0e \x01(\t\x12\x12\n\nreviewerId\x18\x0f \x01(\t\x12%\n\x1dreviewerExpirationDateUnixSec\x18\x06 \x01(\x03\x1aM\n\x17ScanConfigurationsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12!\n\x05value\x18\x02 \x01(\x0b2\x12.ScanConfiguration:\x028\x01B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'screen_configuration_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SCREENCONFIGURATION_SCANCONFIGURATIONSENTRY']._options = None
    _globals['_SCREENCONFIGURATION_SCANCONFIGURATIONSENTRY']._serialized_options = b'8\x01'
    _globals['_SCREENCONFIGURATIONCSS']._serialized_start = 73
    _globals['_SCREENCONFIGURATIONCSS']._serialized_end = 144
    _globals['_SCREENCONFIGURATIONROW']._serialized_start = 146
    _globals['_SCREENCONFIGURATIONROW']._serialized_end = 186
    _globals['_SCREENCONFIGURATIONCOLUMN']._serialized_start = 188
    _globals['_SCREENCONFIGURATIONCOLUMN']._serialized_end = 230
    _globals['_WIDGETLAYOUTCONFIGURATION']._serialized_start = 233
    _globals['_WIDGETLAYOUTCONFIGURATION']._serialized_end = 387
    _globals['_FULLSCREENLAYOUT']._serialized_start = 390
    _globals['_FULLSCREENLAYOUT']._serialized_end = 623
    _globals['_SCANCALIBRATIONCONFIGURATION']._serialized_start = 625
    _globals['_SCANCALIBRATIONCONFIGURATION']._serialized_end = 712
    _globals['_SCANCONFIGURATION']._serialized_start = 714
    _globals['_SCANCONFIGURATION']._serialized_end = 831
    _globals['_SCREENCONFIGURATION']._serialized_start = 834
    _globals['_SCREENCONFIGURATION']._serialized_end = 1333
    _globals['_SCREENCONFIGURATION_SCANCONFIGURATIONSENTRY']._serialized_start = 1256
    _globals['_SCREENCONFIGURATION_SCANCONFIGURATIONSENTRY']._serialized_end = 1333