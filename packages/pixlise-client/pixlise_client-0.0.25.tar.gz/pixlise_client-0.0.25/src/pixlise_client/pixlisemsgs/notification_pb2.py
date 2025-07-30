"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12notification.proto"\xd7\x02\n\x0cNotification\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\ndestUserId\x18\x02 \x01(\t\x12\x17\n\x0fdestUserGroupId\x18\x03 \x01(\t\x12\x16\n\x0emaxSecToExpiry\x18\x04 \x01(\r\x12\x0f\n\x07subject\x18\x05 \x01(\t\x12\x10\n\x08contents\x18\x06 \x01(\t\x12\x0c\n\x04from\x18\x07 \x01(\t\x12\x18\n\x10timeStampUnixSec\x18\x08 \x01(\r\x12\x12\n\nactionLink\x18\t \x01(\t\x12+\n\x10notificationType\x18\n \x01(\x0e2\x11.NotificationType\x12\x0f\n\x07scanIds\x18\x0b \x03(\t\x12\x11\n\timageName\x18\x0c \x01(\t\x12\x0f\n\x07quantId\x18\r \x01(\t\x12\x17\n\x0frequestorUserId\x18\x0e \x01(\t\x12\r\n\x05roiId\x18\x0f \x01(\t\x12\r\n\x05mapId\x18\x10 \x01(\t*\x8f\x01\n\x10NotificationType\x12\x0e\n\nNT_UNKNOWN\x10\x00\x12\x17\n\x13NT_SYS_DATA_CHANGED\x10\x01\x12\x13\n\x0fNT_USER_MESSAGE\x10\x02\x12\x11\n\rNT_USER_MODAL\x10\x03\x12\x0f\n\x0bNT_NEW_USER\x10\x04\x12\x19\n\x15NT_JOIN_GROUP_REQUEST\x10\x05B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'notification_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_NOTIFICATIONTYPE']._serialized_start = 369
    _globals['_NOTIFICATIONTYPE']._serialized_end = 512
    _globals['_NOTIFICATION']._serialized_start = 23
    _globals['_NOTIFICATION']._serialized_end = 366