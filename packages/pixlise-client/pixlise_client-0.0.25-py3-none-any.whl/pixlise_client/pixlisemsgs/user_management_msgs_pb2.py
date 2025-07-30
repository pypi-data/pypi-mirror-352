"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import user_pb2 as user__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1auser-management-msgs.proto\x1a\nuser.proto"T\n\x0bUserListReq\x12\x10\n\x06roleId\x18\x01 \x01(\tH\x00\x12\x10\n\x06userId\x18\x02 \x01(\tH\x00\x12\x14\n\nsearchText\x18\x03 \x01(\tH\x00B\x0b\n\tQueryType"2\n\x0cUserListResp\x12"\n\x07details\x18\x01 \x03(\x0b2\x11.Auth0UserDetails"\x11\n\x0fUserRoleListReq"1\n\x10UserRoleListResp\x12\x1d\n\x05roles\x18\x01 \x03(\x0b2\x0e.Auth0UserRole""\n\x10UserRolesListReq\x12\x0e\n\x06userId\x18\x01 \x01(\t"2\n\x11UserRolesListResp\x12\x1d\n\x05roles\x18\x01 \x03(\x0b2\x0e.Auth0UserRole"0\n\x0eUserAddRoleReq\x12\x0e\n\x06userId\x18\x01 \x01(\t\x12\x0e\n\x06roleId\x18\x02 \x01(\t"\x11\n\x0fUserAddRoleResp"3\n\x11UserDeleteRoleReq\x12\x0e\n\x06userId\x18\x01 \x01(\t\x12\x0e\n\x06roleId\x18\x02 \x01(\t"\x14\n\x12UserDeleteRoleResp"$\n\x12UserImpersonateReq\x12\x0e\n\x06userId\x18\x01 \x01(\t"5\n\x13UserImpersonateResp\x12\x1e\n\x0bsessionUser\x18\x01 \x01(\x0b2\t.UserInfo"\x17\n\x15UserImpersonateGetReq"8\n\x16UserImpersonateGetResp\x12\x1e\n\x0bsessionUser\x18\x01 \x01(\x0b2\t.UserInfo"k\n\x1aReviewerMagicLinkCreateReq\x12\x14\n\x0caccessLength\x18\x01 \x01(\x03\x12\x13\n\x0bworkspaceId\x18\x02 \x01(\t\x12\x10\n\x08clientId\x18\x03 \x01(\t\x12\x10\n\x08audience\x18\x04 \x01(\t"0\n\x1bReviewerMagicLinkCreateResp\x12\x11\n\tmagicLink\x18\x01 \x01(\t"w\n\x19ReviewerMagicLinkLoginReq\x12\x11\n\tmagicLink\x18\x01 \x01(\t\x12\x10\n\x08clientId\x18\x02 \x01(\t\x12\x0e\n\x06domain\x18\x03 \x01(\t\x12\x10\n\x08audience\x18\x04 \x01(\t\x12\x13\n\x0bredirectURI\x18\x05 \x01(\t"e\n\x1aReviewerMagicLinkLoginResp\x12\x0e\n\x06userId\x18\x01 \x01(\t\x12\r\n\x05token\x18\x02 \x01(\t\x12\r\n\x05email\x18\x03 \x01(\t\x12\x19\n\x11nonSecretPassword\x18\x04 \x01(\tB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_management_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_USERLISTREQ']._serialized_start = 42
    _globals['_USERLISTREQ']._serialized_end = 126
    _globals['_USERLISTRESP']._serialized_start = 128
    _globals['_USERLISTRESP']._serialized_end = 178
    _globals['_USERROLELISTREQ']._serialized_start = 180
    _globals['_USERROLELISTREQ']._serialized_end = 197
    _globals['_USERROLELISTRESP']._serialized_start = 199
    _globals['_USERROLELISTRESP']._serialized_end = 248
    _globals['_USERROLESLISTREQ']._serialized_start = 250
    _globals['_USERROLESLISTREQ']._serialized_end = 284
    _globals['_USERROLESLISTRESP']._serialized_start = 286
    _globals['_USERROLESLISTRESP']._serialized_end = 336
    _globals['_USERADDROLEREQ']._serialized_start = 338
    _globals['_USERADDROLEREQ']._serialized_end = 386
    _globals['_USERADDROLERESP']._serialized_start = 388
    _globals['_USERADDROLERESP']._serialized_end = 405
    _globals['_USERDELETEROLEREQ']._serialized_start = 407
    _globals['_USERDELETEROLEREQ']._serialized_end = 458
    _globals['_USERDELETEROLERESP']._serialized_start = 460
    _globals['_USERDELETEROLERESP']._serialized_end = 480
    _globals['_USERIMPERSONATEREQ']._serialized_start = 482
    _globals['_USERIMPERSONATEREQ']._serialized_end = 518
    _globals['_USERIMPERSONATERESP']._serialized_start = 520
    _globals['_USERIMPERSONATERESP']._serialized_end = 573
    _globals['_USERIMPERSONATEGETREQ']._serialized_start = 575
    _globals['_USERIMPERSONATEGETREQ']._serialized_end = 598
    _globals['_USERIMPERSONATEGETRESP']._serialized_start = 600
    _globals['_USERIMPERSONATEGETRESP']._serialized_end = 656
    _globals['_REVIEWERMAGICLINKCREATEREQ']._serialized_start = 658
    _globals['_REVIEWERMAGICLINKCREATEREQ']._serialized_end = 765
    _globals['_REVIEWERMAGICLINKCREATERESP']._serialized_start = 767
    _globals['_REVIEWERMAGICLINKCREATERESP']._serialized_end = 815
    _globals['_REVIEWERMAGICLINKLOGINREQ']._serialized_start = 817
    _globals['_REVIEWERMAGICLINKLOGINREQ']._serialized_end = 936
    _globals['_REVIEWERMAGICLINKLOGINRESP']._serialized_start = 938
    _globals['_REVIEWERMAGICLINKLOGINRESP']._serialized_end = 1039