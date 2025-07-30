"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import user_pb2 as user__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ntags.proto\x1a\nuser.proto"W\n\x03Tag\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04type\x18\x03 \x01(\t\x12\x0e\n\x06scanId\x18\x04 \x01(\t\x12\x18\n\x05owner\x18\x05 \x01(\x0b2\t.UserInfo"P\n\x05TagDB\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04type\x18\x03 \x01(\t\x12\x0e\n\x06scanId\x18\x04 \x01(\t\x12\x0f\n\x07ownerId\x18\x05 \x01(\t"#\n\rClientTagList\x12\x12\n\x04tags\x18\x01 \x03(\x0b2\x04.TagB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tags_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_TAG']._serialized_start = 26
    _globals['_TAG']._serialized_end = 113
    _globals['_TAGDB']._serialized_start = 115
    _globals['_TAGDB']._serialized_end = 195
    _globals['_CLIENTTAGLIST']._serialized_start = 197
    _globals['_CLIENTTAGLIST']._serialized_end = 232