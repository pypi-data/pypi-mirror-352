"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nuser.proto"\x9b\x01\n\x08UserInfo\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\r\n\x05email\x18\x03 \x01(\t\x12\x0f\n\x07iconURL\x18\x04 \x01(\t\x12\x1b\n\x13reviewerWorkspaceId\x18\x05 \x01(\t\x12\x1d\n\x15expirationDateUnixSec\x18\x06 \x01(\x03\x12\x19\n\x11nonSecretPassword\x18\x07 \x01(\t"Z\n\x0bUserDetails\x12\x17\n\x04info\x18\x01 \x01(\x0b2\t.UserInfo\x12\x1d\n\x15dataCollectionVersion\x18\x05 \x01(\t\x12\x13\n\x0bpermissions\x18\x08 \x03(\t">\n\rAuth0UserRole\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0bdescription\x18\x03 \x01(\t"\x82\x01\n\x10Auth0UserDetails\x12\x1c\n\tauth0User\x18\x01 \x01(\x0b2\t.UserInfo\x12\x1e\n\x0bpixliseUser\x18\x02 \x01(\x0b2\t.UserInfo\x12\x16\n\x0ecreatedUnixSec\x18\x03 \x01(\r\x12\x18\n\x10lastLoginUnixSec\x18\x04 \x01(\rB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_USERINFO']._serialized_start = 15
    _globals['_USERINFO']._serialized_end = 170
    _globals['_USERDETAILS']._serialized_start = 172
    _globals['_USERDETAILS']._serialized_end = 262
    _globals['_AUTH0USERROLE']._serialized_start = 264
    _globals['_AUTH0USERROLE']._serialized_end = 326
    _globals['_AUTH0USERDETAILS']._serialized_start = 329
    _globals['_AUTH0USERDETAILS']._serialized_end = 459