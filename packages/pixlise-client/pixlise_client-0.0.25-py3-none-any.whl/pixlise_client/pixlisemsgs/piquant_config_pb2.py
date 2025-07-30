"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14piquant-config.proto"\x85\x01\n\rPiquantConfig\x12\x13\n\x0bdescription\x18\x01 \x01(\t\x12\x12\n\nconfigFile\x18\x02 \x01(\t\x12\x1b\n\x13opticEfficiencyFile\x18\x03 \x01(\t\x12\x17\n\x0fcalibrationFile\x18\x04 \x01(\t\x12\x15\n\rstandardsFile\x18\x05 \x01(\t"^\n\x0ePiquantVersion\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\x12\x17\n\x0fmodifiedUnixSec\x18\x03 \x01(\r\x12\x16\n\x0emodifierUserId\x18\x04 \x01(\tB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'piquant_config_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_PIQUANTCONFIG']._serialized_start = 25
    _globals['_PIQUANTCONFIG']._serialized_end = 158
    _globals['_PIQUANTVERSION']._serialized_start = 160
    _globals['_PIQUANTVERSION']._serialized_end = 254