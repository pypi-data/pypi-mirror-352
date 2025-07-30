"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import ownership_access_pb2 as ownership__access__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bownership-access-msgs.proto\x1a\x16ownership-access.proto"D\n\x0fGetOwnershipReq\x12\x10\n\x08objectId\x18\x01 \x01(\t\x12\x1f\n\nobjectType\x18\x02 \x01(\x0e2\x0b.ObjectType"5\n\x10GetOwnershipResp\x12!\n\townership\x18\x01 \x01(\x0b2\x0e.OwnershipItem"\xde\x01\n\x13ObjectEditAccessReq\x12\x10\n\x08objectId\x18\x01 \x01(\t\x12\x1f\n\nobjectType\x18\x02 \x01(\x0e2\x0b.ObjectType\x12"\n\naddViewers\x18\x03 \x01(\x0b2\x0e.UserGroupList\x12%\n\rdeleteViewers\x18\x04 \x01(\x0b2\x0e.UserGroupList\x12"\n\naddEditors\x18\x05 \x01(\x0b2\x0e.UserGroupList\x12%\n\rdeleteEditors\x18\x06 \x01(\x0b2\x0e.UserGroupList"9\n\x14ObjectEditAccessResp\x12!\n\townership\x18\x01 \x01(\x0b2\x0e.OwnershipItemB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ownership_access_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_GETOWNERSHIPREQ']._serialized_start = 55
    _globals['_GETOWNERSHIPREQ']._serialized_end = 123
    _globals['_GETOWNERSHIPRESP']._serialized_start = 125
    _globals['_GETOWNERSHIPRESP']._serialized_end = 178
    _globals['_OBJECTEDITACCESSREQ']._serialized_start = 181
    _globals['_OBJECTEDITACCESSREQ']._serialized_end = 403
    _globals['_OBJECTEDITACCESSRESP']._serialized_start = 405
    _globals['_OBJECTEDITACCESSRESP']._serialized_end = 462