"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import user_group_pb2 as user__group__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fuser-group-retrieval-msgs.proto\x1a\x10user-group.proto"\x12\n\x10UserGroupListReq"7\n\x11UserGroupListResp\x12"\n\ngroupInfos\x18\x01 \x03(\x0b2\x0e.UserGroupInfo"\x1a\n\x18UserGroupListJoinableReq"F\n\x19UserGroupListJoinableResp\x12)\n\x06groups\x18\x01 \x03(\x0b2\x19.UserGroupJoinSummaryInfo"\x1f\n\x0cUserGroupReq\x12\x0f\n\x07groupId\x18\x01 \x01(\t"*\n\rUserGroupResp\x12\x19\n\x05group\x18\x01 \x01(\x0b2\n.UserGroupB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_group_retrieval_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_USERGROUPLISTREQ']._serialized_start = 53
    _globals['_USERGROUPLISTREQ']._serialized_end = 71
    _globals['_USERGROUPLISTRESP']._serialized_start = 73
    _globals['_USERGROUPLISTRESP']._serialized_end = 128
    _globals['_USERGROUPLISTJOINABLEREQ']._serialized_start = 130
    _globals['_USERGROUPLISTJOINABLEREQ']._serialized_end = 156
    _globals['_USERGROUPLISTJOINABLERESP']._serialized_start = 158
    _globals['_USERGROUPLISTJOINABLERESP']._serialized_end = 228
    _globals['_USERGROUPREQ']._serialized_start = 230
    _globals['_USERGROUPREQ']._serialized_end = 261
    _globals['_USERGROUPRESP']._serialized_start = 263
    _globals['_USERGROUPRESP']._serialized_end = 305