"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import ownership_access_pb2 as ownership__access__pb2
from . import user_pb2 as user__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10user-group.proto\x1a\x16ownership-access.proto\x1a\nuser.proto"\xf3\x01\n\x0bUserGroupDB\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0bdescription\x18\x08 \x01(\t\x12\x16\n\x0ecreatedUnixSec\x18\x07 \x01(\r\x12\x1d\n\x15lastUserJoinedUnixSec\x18\t \x01(\r\x12\x10\n\x08joinable\x18\n \x01(\x08\x12\x14\n\x0cdefaultRoles\x18\x0b \x03(\t\x12\x1f\n\x07viewers\x18\x05 \x01(\x0b2\x0e.UserGroupList\x12\x1f\n\x07members\x18\x03 \x01(\x0b2\x0e.UserGroupList\x12\x14\n\x0cadminUserIds\x18\x04 \x03(\t"\xd1\x01\n\rUserGroupInfo\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0bdescription\x18\x05 \x01(\t\x12\x16\n\x0ecreatedUnixSec\x18\x03 \x01(\r\x12\x1d\n\x15lastUserJoinedUnixSec\x18\x06 \x01(\r\x12\x10\n\x08joinable\x18\x07 \x01(\x08\x12\x14\n\x0cdefaultRoles\x18\x08 \x03(\t\x122\n\x12relationshipToUser\x18\x04 \x01(\x0e2\x16.UserGroupRelationship"M\n\x11UserGroupInfoList\x12\x18\n\x05users\x18\x01 \x03(\x0b2\t.UserInfo\x12\x1e\n\x06groups\x18\x02 \x03(\x0b2\x0e.UserGroupInfo"\x92\x01\n\tUserGroup\x12\x1c\n\x04info\x18\x01 \x01(\x0b2\x0e.UserGroupInfo\x12#\n\x07viewers\x18\x05 \x01(\x0b2\x12.UserGroupInfoList\x12#\n\x07members\x18\x03 \x01(\x0b2\x12.UserGroupInfoList\x12\x1d\n\nadminUsers\x18\x04 \x03(\x0b2\t.UserInfo"\x9d\x01\n\x18UserGroupJoinSummaryInfo\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0bdescription\x18\x03 \x01(\t\x12!\n\x0eadministrators\x18\x04 \x03(\x0b2\t.UserInfo\x12\x10\n\x08datasets\x18\x05 \x01(\r\x12\x1d\n\x15lastUserJoinedUnixSec\x18\x06 \x01(\r"\x8f\x01\n\x16UserGroupJoinRequestDB\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06userId\x18\x02 \x01(\t\x12\x13\n\x0bjoinGroupId\x18\x03 \x01(\t\x12\x10\n\x08asMember\x18\x04 \x01(\x08\x12\x1a\n\x07details\x18\x05 \x01(\x0b2\t.UserInfo\x12\x16\n\x0ecreatedUnixSec\x18\x06 \x01(\r*W\n\x15UserGroupRelationship\x12\x0f\n\x0bUGR_UNKNOWN\x10\x00\x12\x0e\n\nUGR_VIEWER\x10\x01\x12\x0e\n\nUGR_MEMBER\x10\x02\x12\r\n\tUGR_ADMIN\x10\x03B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_group_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_USERGROUPRELATIONSHIP']._serialized_start = 1048
    _globals['_USERGROUPRELATIONSHIP']._serialized_end = 1135
    _globals['_USERGROUPDB']._serialized_start = 57
    _globals['_USERGROUPDB']._serialized_end = 300
    _globals['_USERGROUPINFO']._serialized_start = 303
    _globals['_USERGROUPINFO']._serialized_end = 512
    _globals['_USERGROUPINFOLIST']._serialized_start = 514
    _globals['_USERGROUPINFOLIST']._serialized_end = 591
    _globals['_USERGROUP']._serialized_start = 594
    _globals['_USERGROUP']._serialized_end = 740
    _globals['_USERGROUPJOINSUMMARYINFO']._serialized_start = 743
    _globals['_USERGROUPJOINSUMMARYINFO']._serialized_end = 900
    _globals['_USERGROUPJOINREQUESTDB']._serialized_start = 903
    _globals['_USERGROUPJOINREQUESTDB']._serialized_end = 1046