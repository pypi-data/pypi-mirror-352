"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import user_pb2 as user__pb2
from . import user_notification_settings_pb2 as user__notification__settings__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13user-db-items.proto\x1a\nuser.proto\x1a user-notification-settings.proto"\x89\x01\n\nUserDBItem\x12\n\n\x02id\x18\x01 \x01(\t\x12\x17\n\x04info\x18\x02 \x01(\x0b2\t.UserInfo\x12\x1d\n\x15dataCollectionVersion\x18\x03 \x01(\t\x127\n\x14notificationSettings\x18\x05 \x01(\x0b2\x19.UserNotificationSettingsB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_db_items_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_USERDBITEM']._serialized_start = 70
    _globals['_USERDBITEM']._serialized_end = 207