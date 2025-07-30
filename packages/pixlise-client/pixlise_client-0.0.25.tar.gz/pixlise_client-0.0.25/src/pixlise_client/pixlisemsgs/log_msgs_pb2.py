"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import log_pb2 as log__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0elog-msgs.proto\x1a\tlog.proto"!\n\nLogReadReq\x12\x13\n\x0blogStreamId\x18\x01 \x01(\t"(\n\x0bLogReadResp\x12\x19\n\x07entries\x18\x01 \x03(\x0b2\x08.LogLine"$\n\x0eLogSetLevelReq\x12\x12\n\nlogLevelId\x18\x01 \x01(\t"%\n\x0fLogSetLevelResp\x12\x12\n\nlogLevelId\x18\x01 \x01(\t"\x10\n\x0eLogGetLevelReq"%\n\x0fLogGetLevelResp\x12\x12\n\nlogLevelId\x18\x01 \x01(\tB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'log_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_LOGREADREQ']._serialized_start = 29
    _globals['_LOGREADREQ']._serialized_end = 62
    _globals['_LOGREADRESP']._serialized_start = 64
    _globals['_LOGREADRESP']._serialized_end = 104
    _globals['_LOGSETLEVELREQ']._serialized_start = 106
    _globals['_LOGSETLEVELREQ']._serialized_end = 142
    _globals['_LOGSETLEVELRESP']._serialized_start = 144
    _globals['_LOGSETLEVELRESP']._serialized_end = 181
    _globals['_LOGGETLEVELREQ']._serialized_start = 183
    _globals['_LOGGETLEVELREQ']._serialized_end = 199
    _globals['_LOGGETLEVELRESP']._serialized_start = 201
    _globals['_LOGGETLEVELRESP']._serialized_end = 238