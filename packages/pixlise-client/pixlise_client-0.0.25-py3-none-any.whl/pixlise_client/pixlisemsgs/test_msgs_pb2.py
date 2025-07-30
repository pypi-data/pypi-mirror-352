"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ftest-msgs.proto"6\n\nRunTestReq\x12\x10\n\x08testType\x18\x01 \x01(\t\x12\x16\n\x0etestParameters\x18\x02 \x01(\t"\r\n\x0bRunTestRespB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'test_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_RUNTESTREQ']._serialized_start = 19
    _globals['_RUNTESTREQ']._serialized_end = 73
    _globals['_RUNTESTRESP']._serialized_start = 75
    _globals['_RUNTESTRESP']._serialized_end = 88