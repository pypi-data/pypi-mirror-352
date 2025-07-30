"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n user-notification-settings.proto"\xaa\x01\n\x18UserNotificationSettings\x12C\n\rtopicSettings\x18\x01 \x03(\x0b2,.UserNotificationSettings.TopicSettingsEntry\x1aI\n\x12TopicSettingsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12"\n\x05value\x18\x02 \x01(\x0e2\x13.NotificationMethod:\x028\x01*S\n\x12NotificationMethod\x12\x0e\n\nNOTIF_NONE\x10\x00\x12\x0f\n\x0bNOTIF_EMAIL\x10\x01\x12\x0c\n\x08NOTIF_UI\x10\x02\x12\x0e\n\nNOTIF_BOTH\x10\x03B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_notification_settings_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_USERNOTIFICATIONSETTINGS_TOPICSETTINGSENTRY']._options = None
    _globals['_USERNOTIFICATIONSETTINGS_TOPICSETTINGSENTRY']._serialized_options = b'8\x01'
    _globals['_NOTIFICATIONMETHOD']._serialized_start = 209
    _globals['_NOTIFICATIONMETHOD']._serialized_end = 292
    _globals['_USERNOTIFICATIONSETTINGS']._serialized_start = 37
    _globals['_USERNOTIFICATIONSETTINGS']._serialized_end = 207
    _globals['_USERNOTIFICATIONSETTINGS_TOPICSETTINGSENTRY']._serialized_start = 134
    _globals['_USERNOTIFICATIONSETTINGS_TOPICSETTINGSENTRY']._serialized_end = 207