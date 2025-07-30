"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import ownership_access_pb2 as ownership__access__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16expression-group.proto\x1a\x16ownership-access.proto"O\n\x13ExpressionGroupItem\x12\x14\n\x0cexpressionId\x18\x01 \x01(\t\x12\x10\n\x08rangeMin\x18\x02 \x01(\x02\x12\x10\n\x08rangeMax\x18\x03 \x01(\x02"\xb3\x01\n\x0fExpressionGroup\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12(\n\ngroupItems\x18\x03 \x03(\x0b2\x14.ExpressionGroupItem\x12\x0c\n\x04tags\x18\x04 \x03(\t\x12\x17\n\x0fmodifiedUnixSec\x18\x05 \x01(\r\x12\x13\n\x0bdescription\x18\x07 \x01(\t\x12 \n\x05owner\x18\x06 \x01(\x0b2\x11.OwnershipSummaryB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'expression_group_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_EXPRESSIONGROUPITEM']._serialized_start = 50
    _globals['_EXPRESSIONGROUPITEM']._serialized_end = 129
    _globals['_EXPRESSIONGROUP']._serialized_start = 132
    _globals['_EXPRESSIONGROUP']._serialized_end = 311