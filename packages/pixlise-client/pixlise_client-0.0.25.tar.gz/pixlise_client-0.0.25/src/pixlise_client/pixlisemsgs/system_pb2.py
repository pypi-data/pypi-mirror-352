"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0csystem.proto"\r\n\x0bBackupDBReq"\x0e\n\x0cBackupDBResp"\r\n\x0bBackupDBUpd"\x0e\n\x0cRestoreDBReq"\x0f\n\rRestoreDBResp"\x15\n\x13DBAdminConfigGetReq"\x89\x01\n\x14DBAdminConfigGetResp\x12\x11\n\tcanBackup\x18\x01 \x01(\x08\x12\x19\n\x11backupDestination\x18\x02 \x01(\t\x12\x12\n\ncanRestore\x18\x03 \x01(\x08\x12\x13\n\x0brestoreFrom\x18\x04 \x01(\t\x12\x1a\n\x12impersonateEnabled\x18\x05 \x01(\x08B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'system_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_BACKUPDBREQ']._serialized_start = 16
    _globals['_BACKUPDBREQ']._serialized_end = 29
    _globals['_BACKUPDBRESP']._serialized_start = 31
    _globals['_BACKUPDBRESP']._serialized_end = 45
    _globals['_BACKUPDBUPD']._serialized_start = 47
    _globals['_BACKUPDBUPD']._serialized_end = 60
    _globals['_RESTOREDBREQ']._serialized_start = 62
    _globals['_RESTOREDBREQ']._serialized_end = 76
    _globals['_RESTOREDBRESP']._serialized_start = 78
    _globals['_RESTOREDBRESP']._serialized_end = 93
    _globals['_DBADMINCONFIGGETREQ']._serialized_start = 95
    _globals['_DBADMINCONFIGGETREQ']._serialized_end = 116
    _globals['_DBADMINCONFIGGETRESP']._serialized_start = 119
    _globals['_DBADMINCONFIGGETRESP']._serialized_end = 256