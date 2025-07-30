"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import user_group_pb2 as user__group__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1cuser-group-admins-msgs.proto\x1a\x10user-group.proto"<\n\x14UserGroupAddAdminReq\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x13\n\x0badminUserId\x18\x02 \x01(\t"2\n\x15UserGroupAddAdminResp\x12\x19\n\x05group\x18\x01 \x01(\x0b2\n.UserGroup"?\n\x17UserGroupDeleteAdminReq\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x13\n\x0badminUserId\x18\x02 \x01(\t"5\n\x18UserGroupDeleteAdminResp\x12\x19\n\x05group\x18\x01 \x01(\x0b2\n.UserGroupB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_group_admins_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_USERGROUPADDADMINREQ']._serialized_start = 50
    _globals['_USERGROUPADDADMINREQ']._serialized_end = 110
    _globals['_USERGROUPADDADMINRESP']._serialized_start = 112
    _globals['_USERGROUPADDADMINRESP']._serialized_end = 162
    _globals['_USERGROUPDELETEADMINREQ']._serialized_start = 164
    _globals['_USERGROUPDELETEADMINREQ']._serialized_end = 227
    _globals['_USERGROUPDELETEADMINRESP']._serialized_start = 229
    _globals['_USERGROUPDELETEADMINRESP']._serialized_end = 282