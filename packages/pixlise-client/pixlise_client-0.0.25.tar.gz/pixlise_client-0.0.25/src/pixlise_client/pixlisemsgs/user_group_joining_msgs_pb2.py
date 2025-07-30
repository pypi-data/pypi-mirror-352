"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import user_group_pb2 as user__group__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1duser-group-joining-msgs.proto\x1a\x10user-group.proto"5\n\x10UserGroupJoinReq\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x10\n\x08asMember\x18\x02 \x01(\x08"\x13\n\x11UserGroupJoinResp"<\n\x16UserGroupIgnoreJoinReq\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x11\n\trequestId\x18\x02 \x01(\t"\x19\n\x17UserGroupIgnoreJoinResp"\'\n\x14UserGroupJoinListReq\x12\x0f\n\x07groupId\x18\x01 \x01(\t"B\n\x15UserGroupJoinListResp\x12)\n\x08requests\x18\x01 \x03(\x0b2\x17.UserGroupJoinRequestDBB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_group_joining_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_USERGROUPJOINREQ']._serialized_start = 51
    _globals['_USERGROUPJOINREQ']._serialized_end = 104
    _globals['_USERGROUPJOINRESP']._serialized_start = 106
    _globals['_USERGROUPJOINRESP']._serialized_end = 125
    _globals['_USERGROUPIGNOREJOINREQ']._serialized_start = 127
    _globals['_USERGROUPIGNOREJOINREQ']._serialized_end = 187
    _globals['_USERGROUPIGNOREJOINRESP']._serialized_start = 189
    _globals['_USERGROUPIGNOREJOINRESP']._serialized_end = 214
    _globals['_USERGROUPJOINLISTREQ']._serialized_start = 216
    _globals['_USERGROUPJOINLISTREQ']._serialized_end = 255
    _globals['_USERGROUPJOINLISTRESP']._serialized_start = 257
    _globals['_USERGROUPJOINLISTRESP']._serialized_end = 323