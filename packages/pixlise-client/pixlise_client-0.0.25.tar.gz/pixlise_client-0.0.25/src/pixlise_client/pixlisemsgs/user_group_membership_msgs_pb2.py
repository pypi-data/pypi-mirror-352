"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import user_group_pb2 as user__group__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n user-group-membership-msgs.proto\x1a\x10user-group.proto"c\n\x15UserGroupAddMemberReq\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x17\n\rgroupMemberId\x18\x02 \x01(\tH\x00\x12\x16\n\x0cuserMemberId\x18\x03 \x01(\tH\x00B\x08\n\x06Member"3\n\x16UserGroupAddMemberResp\x12\x19\n\x05group\x18\x01 \x01(\x0b2\n.UserGroup"f\n\x18UserGroupDeleteMemberReq\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x17\n\rgroupMemberId\x18\x02 \x01(\tH\x00\x12\x16\n\x0cuserMemberId\x18\x03 \x01(\tH\x00B\x08\n\x06Member"6\n\x19UserGroupDeleteMemberResp\x12\x19\n\x05group\x18\x01 \x01(\x0b2\n.UserGroup"c\n\x15UserGroupAddViewerReq\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x17\n\rgroupViewerId\x18\x02 \x01(\tH\x00\x12\x16\n\x0cuserViewerId\x18\x03 \x01(\tH\x00B\x08\n\x06Viewer"3\n\x16UserGroupAddViewerResp\x12\x19\n\x05group\x18\x01 \x01(\x0b2\n.UserGroup"f\n\x18UserGroupDeleteViewerReq\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x17\n\rgroupViewerId\x18\x02 \x01(\tH\x00\x12\x16\n\x0cuserViewerId\x18\x03 \x01(\tH\x00B\x08\n\x06Viewer"6\n\x19UserGroupDeleteViewerResp\x12\x19\n\x05group\x18\x01 \x01(\x0b2\n.UserGroupB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_group_membership_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_USERGROUPADDMEMBERREQ']._serialized_start = 54
    _globals['_USERGROUPADDMEMBERREQ']._serialized_end = 153
    _globals['_USERGROUPADDMEMBERRESP']._serialized_start = 155
    _globals['_USERGROUPADDMEMBERRESP']._serialized_end = 206
    _globals['_USERGROUPDELETEMEMBERREQ']._serialized_start = 208
    _globals['_USERGROUPDELETEMEMBERREQ']._serialized_end = 310
    _globals['_USERGROUPDELETEMEMBERRESP']._serialized_start = 312
    _globals['_USERGROUPDELETEMEMBERRESP']._serialized_end = 366
    _globals['_USERGROUPADDVIEWERREQ']._serialized_start = 368
    _globals['_USERGROUPADDVIEWERREQ']._serialized_end = 467
    _globals['_USERGROUPADDVIEWERRESP']._serialized_start = 469
    _globals['_USERGROUPADDVIEWERRESP']._serialized_end = 520
    _globals['_USERGROUPDELETEVIEWERREQ']._serialized_start = 522
    _globals['_USERGROUPDELETEVIEWERREQ']._serialized_end = 624
    _globals['_USERGROUPDELETEVIEWERRESP']._serialized_start = 626
    _globals['_USERGROUPDELETEVIEWERRESP']._serialized_end = 680