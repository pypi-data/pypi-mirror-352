"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16memoisation-msgs.proto"\x1f\n\x10MemoiseDeleteReq\x12\x0b\n\x03key\x18\x01 \x01(\t"$\n\x11MemoiseDeleteResp\x12\x0f\n\x07success\x18\x01 \x01(\x08"*\n\x17MemoiseDeleteByRegexReq\x12\x0f\n\x07pattern\x18\x01 \x01(\t".\n\x18MemoiseDeleteByRegexResp\x12\x12\n\nnumDeleted\x18\x01 \x01(\rB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'memoisation_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_MEMOISEDELETEREQ']._serialized_start = 26
    _globals['_MEMOISEDELETEREQ']._serialized_end = 57
    _globals['_MEMOISEDELETERESP']._serialized_start = 59
    _globals['_MEMOISEDELETERESP']._serialized_end = 95
    _globals['_MEMOISEDELETEBYREGEXREQ']._serialized_start = 97
    _globals['_MEMOISEDELETEBYREGEXREQ']._serialized_end = 139
    _globals['_MEMOISEDELETEBYREGEXRESP']._serialized_start = 141
    _globals['_MEMOISEDELETEBYREGEXRESP']._serialized_end = 187