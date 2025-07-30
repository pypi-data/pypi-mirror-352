"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0erestmsgs.proto".\n\x19BeginWSConnectionResponse\x12\x11\n\tconnToken\x18\x01 \x01(\t"l\n\x0fVersionResponse\x12*\n\x08versions\x18\x01 \x03(\x0b2\x18.VersionResponse.Version\x1a-\n\x07Version\x12\x11\n\tcomponent\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\tB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'restmsgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_BEGINWSCONNECTIONRESPONSE']._serialized_start = 18
    _globals['_BEGINWSCONNECTIONRESPONSE']._serialized_end = 64
    _globals['_VERSIONRESPONSE']._serialized_start = 66
    _globals['_VERSIONRESPONSE']._serialized_end = 174
    _globals['_VERSIONRESPONSE_VERSION']._serialized_start = 129
    _globals['_VERSIONRESPONSE_VERSION']._serialized_end = 174