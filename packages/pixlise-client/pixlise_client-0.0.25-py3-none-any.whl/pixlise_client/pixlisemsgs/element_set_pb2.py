"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import ownership_access_pb2 as ownership__access__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11element-set.proto\x1a\x16ownership-access.proto"F\n\x0bElementLine\x12\t\n\x01Z\x18\x01 \x01(\x05\x12\t\n\x01K\x18\x02 \x01(\x08\x12\t\n\x01L\x18\x03 \x01(\x08\x12\t\n\x01M\x18\x04 \x01(\x08\x12\x0b\n\x03Esc\x18\x05 \x01(\x08"~\n\nElementSet\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x1b\n\x05lines\x18\x03 \x03(\x0b2\x0c.ElementLine\x12\x17\n\x0fmodifiedUnixSec\x18\x04 \x01(\r\x12 \n\x05owner\x18\x05 \x01(\x0b2\x11.OwnershipSummary"\x7f\n\x11ElementSetSummary\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x15\n\ratomicNumbers\x18\x03 \x03(\x05\x12\x17\n\x0fmodifiedUnixSec\x18\x04 \x01(\r\x12 \n\x05owner\x18\x05 \x01(\x0b2\x11.OwnershipSummaryB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'element_set_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_ELEMENTLINE']._serialized_start = 45
    _globals['_ELEMENTLINE']._serialized_end = 115
    _globals['_ELEMENTSET']._serialized_start = 117
    _globals['_ELEMENTSET']._serialized_end = 243
    _globals['_ELEMENTSETSUMMARY']._serialized_start = 245
    _globals['_ELEMENTSETSUMMARY']._serialized_end = 372