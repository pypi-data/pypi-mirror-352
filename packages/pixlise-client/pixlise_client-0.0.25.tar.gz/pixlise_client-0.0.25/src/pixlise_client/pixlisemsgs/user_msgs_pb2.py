"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import user_pb2 as user__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fuser-msgs.proto\x1a\nuser.proto"\x10\n\x0eUserDetailsReq"0\n\x0fUserDetailsResp\x12\x1d\n\x07details\x18\x01 \x01(\x0b2\x0c.UserDetails"b\n\x13UserDetailsWriteReq\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05email\x18\x02 \x01(\t\x12\x0f\n\x07iconURL\x18\x03 \x01(\t\x12\x1d\n\x15dataCollectionVersion\x18\x04 \x01(\t"5\n\x14UserDetailsWriteResp\x12\x1d\n\x07details\x18\x01 \x01(\x0b2\x0c.UserDetails"%\n\rUserSearchReq\x12\x14\n\x0csearchString\x18\x01 \x01(\t"*\n\x0eUserSearchResp\x12\x18\n\x05users\x18\x01 \x03(\x0b2\t.UserInfoB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_USERDETAILSREQ']._serialized_start = 31
    _globals['_USERDETAILSREQ']._serialized_end = 47
    _globals['_USERDETAILSRESP']._serialized_start = 49
    _globals['_USERDETAILSRESP']._serialized_end = 97
    _globals['_USERDETAILSWRITEREQ']._serialized_start = 99
    _globals['_USERDETAILSWRITEREQ']._serialized_end = 197
    _globals['_USERDETAILSWRITERESP']._serialized_start = 199
    _globals['_USERDETAILSWRITERESP']._serialized_end = 252
    _globals['_USERSEARCHREQ']._serialized_start = 254
    _globals['_USERSEARCHREQ']._serialized_end = 291
    _globals['_USERSEARCHRESP']._serialized_start = 293
    _globals['_USERSEARCHRESP']._serialized_end = 335