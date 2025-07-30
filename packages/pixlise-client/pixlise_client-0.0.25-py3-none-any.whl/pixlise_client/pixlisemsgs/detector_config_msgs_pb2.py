"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import detector_config_pb2 as detector__config__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1adetector-config-msgs.proto\x1a\x15detector-config.proto"\x1f\n\x11DetectorConfigReq\x12\n\n\x02id\x18\x01 \x01(\t"T\n\x12DetectorConfigResp\x12\x1f\n\x06config\x18\x01 \x01(\x0b2\x0f.DetectorConfig\x12\x1d\n\x15piquantConfigVersions\x18\x02 \x03(\t"#\n\x15DetectorConfigListReq\x12\n\n\x02id\x18\x01 \x01(\t")\n\x16DetectorConfigListResp\x12\x0f\n\x07configs\x18\x01 \x03(\tB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'detector_config_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_DETECTORCONFIGREQ']._serialized_start = 53
    _globals['_DETECTORCONFIGREQ']._serialized_end = 84
    _globals['_DETECTORCONFIGRESP']._serialized_start = 86
    _globals['_DETECTORCONFIGRESP']._serialized_end = 170
    _globals['_DETECTORCONFIGLISTREQ']._serialized_start = 172
    _globals['_DETECTORCONFIGLISTREQ']._serialized_end = 207
    _globals['_DETECTORCONFIGLISTRESP']._serialized_start = 209
    _globals['_DETECTORCONFIGLISTRESP']._serialized_end = 250