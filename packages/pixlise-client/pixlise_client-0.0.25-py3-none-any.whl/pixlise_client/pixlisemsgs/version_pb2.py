"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rversion.proto">\n\x0fSemanticVersion\x12\r\n\x05major\x18\x01 \x01(\x05\x12\r\n\x05minor\x18\x02 \x01(\x05\x12\r\n\x05patch\x18\x03 \x01(\x05*H\n\x0cVersionField\x12\x0e\n\nMV_UNKNOWN\x10\x00\x12\x0c\n\x08MV_MAJOR\x10\x01\x12\x0c\n\x08MV_MINOR\x10\x02\x12\x0c\n\x08MV_PATCH\x10\x03B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'version_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_VERSIONFIELD']._serialized_start = 81
    _globals['_VERSIONFIELD']._serialized_end = 153
    _globals['_SEMANTICVERSION']._serialized_start = 17
    _globals['_SEMANTICVERSION']._serialized_end = 79