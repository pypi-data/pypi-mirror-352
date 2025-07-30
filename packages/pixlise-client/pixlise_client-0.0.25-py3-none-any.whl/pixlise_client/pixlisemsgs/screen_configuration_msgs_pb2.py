"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import search_params_pb2 as search__params__pb2
from . import screen_configuration_pb2 as screen__configuration__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fscreen-configuration-msgs.proto\x1a\x13search-params.proto\x1a\x1ascreen-configuration.proto"[\n\x1aScreenConfigurationListReq\x12#\n\x0csearchParams\x18\x01 \x01(\x0b2\r.SearchParams\x12\x18\n\x10snapshotParentId\x18\x02 \x01(\t"Q\n\x1bScreenConfigurationListResp\x122\n\x14screenConfigurations\x18\x01 \x03(\x0b2\x14.ScreenConfiguration"7\n\x19ScreenConfigurationGetReq\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06scanId\x18\x02 \x01(\t"O\n\x1aScreenConfigurationGetResp\x121\n\x13screenConfiguration\x18\x01 \x01(\x0b2\x14.ScreenConfiguration"`\n\x1bScreenConfigurationWriteReq\x12\x0e\n\x06scanId\x18\x02 \x01(\t\x121\n\x13screenConfiguration\x18\x01 \x01(\x0b2\x14.ScreenConfiguration"Q\n\x1cScreenConfigurationWriteResp\x121\n\x13screenConfiguration\x18\x01 \x01(\x0b2\x14.ScreenConfiguration"T\n\x1cScreenConfigurationDeleteReq\x12\n\n\x02id\x18\x01 \x01(\t\x12(\n preserveDanglingWidgetReferences\x18\x02 \x01(\x08"+\n\x1dScreenConfigurationDeleteResp\x12\n\n\x02id\x18\x01 \x01(\tB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'screen_configuration_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SCREENCONFIGURATIONLISTREQ']._serialized_start = 84
    _globals['_SCREENCONFIGURATIONLISTREQ']._serialized_end = 175
    _globals['_SCREENCONFIGURATIONLISTRESP']._serialized_start = 177
    _globals['_SCREENCONFIGURATIONLISTRESP']._serialized_end = 258
    _globals['_SCREENCONFIGURATIONGETREQ']._serialized_start = 260
    _globals['_SCREENCONFIGURATIONGETREQ']._serialized_end = 315
    _globals['_SCREENCONFIGURATIONGETRESP']._serialized_start = 317
    _globals['_SCREENCONFIGURATIONGETRESP']._serialized_end = 396
    _globals['_SCREENCONFIGURATIONWRITEREQ']._serialized_start = 398
    _globals['_SCREENCONFIGURATIONWRITEREQ']._serialized_end = 494
    _globals['_SCREENCONFIGURATIONWRITERESP']._serialized_start = 496
    _globals['_SCREENCONFIGURATIONWRITERESP']._serialized_end = 577
    _globals['_SCREENCONFIGURATIONDELETEREQ']._serialized_start = 579
    _globals['_SCREENCONFIGURATIONDELETEREQ']._serialized_end = 663
    _globals['_SCREENCONFIGURATIONDELETERESP']._serialized_start = 665
    _globals['_SCREENCONFIGURATIONDELETERESP']._serialized_end = 708