"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import tags_pb2 as tags__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0etag-msgs.proto\x1a\ntags.proto"\x0c\n\nTagListReq"!\n\x0bTagListResp\x12\x12\n\x04tags\x18\x01 \x03(\x0b2\x04.Tag":\n\x0cTagCreateReq\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\x0e\n\x06scanId\x18\x03 \x01(\t""\n\rTagCreateResp\x12\x11\n\x03tag\x18\x01 \x01(\x0b2\x04.Tag"\x1d\n\x0cTagDeleteReq\x12\r\n\x05tagId\x18\x01 \x01(\t"\x0f\n\rTagDeleteRespB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tag_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_TAGLISTREQ']._serialized_start = 30
    _globals['_TAGLISTREQ']._serialized_end = 42
    _globals['_TAGLISTRESP']._serialized_start = 44
    _globals['_TAGLISTRESP']._serialized_end = 77
    _globals['_TAGCREATEREQ']._serialized_start = 79
    _globals['_TAGCREATEREQ']._serialized_end = 137
    _globals['_TAGCREATERESP']._serialized_start = 139
    _globals['_TAGCREATERESP']._serialized_end = 173
    _globals['_TAGDELETEREQ']._serialized_start = 175
    _globals['_TAGDELETEREQ']._serialized_end = 204
    _globals['_TAGDELETERESP']._serialized_start = 206
    _globals['_TAGDELETERESP']._serialized_end = 221