"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import notification_pb2 as notification__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17notification-msgs.proto\x1a\x12notification.proto"\x11\n\x0fNotificationReq"7\n\x10NotificationResp\x12#\n\x0cnotification\x18\x01 \x03(\x0b2\r.Notification"6\n\x0fNotificationUpd\x12#\n\x0cnotification\x18\x02 \x01(\x0b2\r.Notification"$\n\x16NotificationDismissReq\x12\n\n\x02id\x18\x01 \x01(\t"\x19\n\x17NotificationDismissResp"a\n\x17SendUserNotificationReq\x12\x0f\n\x07userIds\x18\x01 \x03(\t\x12\x10\n\x08groupIds\x18\x02 \x03(\t\x12#\n\x0cnotification\x18\x03 \x01(\x0b2\r.Notification"\x1a\n\x18SendUserNotificationRespB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'notification_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_NOTIFICATIONREQ']._serialized_start = 47
    _globals['_NOTIFICATIONREQ']._serialized_end = 64
    _globals['_NOTIFICATIONRESP']._serialized_start = 66
    _globals['_NOTIFICATIONRESP']._serialized_end = 121
    _globals['_NOTIFICATIONUPD']._serialized_start = 123
    _globals['_NOTIFICATIONUPD']._serialized_end = 177
    _globals['_NOTIFICATIONDISMISSREQ']._serialized_start = 179
    _globals['_NOTIFICATIONDISMISSREQ']._serialized_end = 215
    _globals['_NOTIFICATIONDISMISSRESP']._serialized_start = 217
    _globals['_NOTIFICATIONDISMISSRESP']._serialized_end = 242
    _globals['_SENDUSERNOTIFICATIONREQ']._serialized_start = 244
    _globals['_SENDUSERNOTIFICATIONREQ']._serialized_end = 341
    _globals['_SENDUSERNOTIFICATIONRESP']._serialized_start = 343
    _globals['_SENDUSERNOTIFICATIONRESP']._serialized_end = 369