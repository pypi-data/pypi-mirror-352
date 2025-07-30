"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import user_pb2 as user__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16ownership-access.proto\x1a\nuser.proto"2\n\rUserGroupList\x12\x0f\n\x07userIds\x18\x01 \x03(\t\x12\x10\n\x08groupIds\x18\x02 \x03(\t"\xad\x01\n\rOwnershipItem\x12\n\n\x02id\x18\x01 \x01(\t\x12\x1f\n\nobjectType\x18\x02 \x01(\x0e2\x0b.ObjectType\x12\x15\n\rcreatorUserId\x18\x03 \x01(\t\x12\x16\n\x0ecreatedUnixSec\x18\x04 \x01(\r\x12\x1f\n\x07viewers\x18\x05 \x01(\x0b2\x0e.UserGroupList\x12\x1f\n\x07editors\x18\x06 \x01(\x0b2\x0e.UserGroupList"\xdb\x01\n\x10OwnershipSummary\x12\x1e\n\x0bcreatorUser\x18\x01 \x01(\x0b2\t.UserInfo\x12\x16\n\x0ecreatedUnixSec\x18\x02 \x01(\r\x12\x17\n\x0fviewerUserCount\x18\x03 \x01(\r\x12\x18\n\x10viewerGroupCount\x18\x04 \x01(\r\x12\x17\n\x0feditorUserCount\x18\x05 \x01(\r\x12\x18\n\x10editorGroupCount\x18\x06 \x01(\r\x12\x18\n\x10sharedWithOthers\x18\x07 \x01(\x08\x12\x0f\n\x07canEdit\x18\x08 \x01(\x08*\xb6\x01\n\nObjectType\x12\x0e\n\nOT_UNKNOWN\x10\x00\x12\n\n\x06OT_ROI\x10\x01\x12\x12\n\x0eOT_ELEMENT_SET\x10\x02\x12\x11\n\rOT_EXPRESSION\x10\x03\x12\x17\n\x13OT_EXPRESSION_GROUP\x10\x04\x12\x12\n\x0eOT_DATA_MODULE\x10\x05\x12\x0b\n\x07OT_SCAN\x10\x06\x12\x15\n\x11OT_QUANTIFICATION\x10\x07\x12\x14\n\x10OT_SCREEN_CONFIG\x10\x08B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ownership_access_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_OBJECTTYPE']._serialized_start = 489
    _globals['_OBJECTTYPE']._serialized_end = 671
    _globals['_USERGROUPLIST']._serialized_start = 38
    _globals['_USERGROUPLIST']._serialized_end = 88
    _globals['_OWNERSHIPITEM']._serialized_start = 91
    _globals['_OWNERSHIPITEM']._serialized_end = 264
    _globals['_OWNERSHIPSUMMARY']._serialized_start = 267
    _globals['_OWNERSHIPSUMMARY']._serialized_end = 486