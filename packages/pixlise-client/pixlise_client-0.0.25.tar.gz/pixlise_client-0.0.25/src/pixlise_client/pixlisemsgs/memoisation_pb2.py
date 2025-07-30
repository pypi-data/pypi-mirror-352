"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import expressions_pb2 as expressions__pb2
from . import roi_pb2 as roi__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11memoisation.proto\x1a\x11expressions.proto\x1a\troi.proto"\xbc\x01\n\x0cMemoisedItem\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x17\n\x0fmemoTimeUnixSec\x18\x02 \x01(\r\x12\x0c\n\x04data\x18\x03 \x01(\x0c\x12\x0e\n\x06scanId\x18\x04 \x01(\t\x12\x0f\n\x07quantId\x18\x05 \x01(\t\x12\x0e\n\x06exprId\x18\x06 \x01(\t\x12\x10\n\x08dataSize\x18\x07 \x01(\r\x12\x1b\n\x13lastReadTimeUnixSec\x18\x08 \x01(\r\x12\x18\n\x10memoWriterUserId\x18\t \x01(\t"Q\n\x0fMemPMCDataValue\x12\x0b\n\x03pmc\x18\x01 \x01(\r\x12\r\n\x05value\x18\x02 \x01(\x02\x12\x13\n\x0bisUndefined\x18\x03 \x01(\x08\x12\r\n\x05label\x18\x04 \x01(\t"{\n\x10MemPMCDataValues\x12\x10\n\x08minValue\x18\x01 \x01(\x02\x12\x10\n\x08maxValue\x18\x02 \x01(\x02\x12 \n\x06values\x18\x03 \x03(\x0b2\x10.MemPMCDataValue\x12\x10\n\x08isBinary\x18\x04 \x01(\x08\x12\x0f\n\x07warning\x18\x05 \x01(\t"v\n\x11MemRegionSettings\x12\x18\n\x06region\x18\x01 \x01(\x0b2\x08.ROIItem\x120\n\x0fdisplaySettings\x18\x02 \x01(\x0b2\x17.ROIItemDisplaySettings\x12\x15\n\rpixelIndexSet\x18\x03 \x03(\r"\x9a\x01\n\x12MemDataQueryResult\x12\'\n\x0cresultValues\x18\x01 \x01(\x0b2\x11.MemPMCDataValues\x12\x12\n\nisPMCTable\x18\x02 \x01(\x08\x12#\n\nexpression\x18\x03 \x01(\x0b2\x0f.DataExpression\x12"\n\x06region\x18\x04 \x01(\x0b2\x12.MemRegionSettingsB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'memoisation_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_MEMOISEDITEM']._serialized_start = 52
    _globals['_MEMOISEDITEM']._serialized_end = 240
    _globals['_MEMPMCDATAVALUE']._serialized_start = 242
    _globals['_MEMPMCDATAVALUE']._serialized_end = 323
    _globals['_MEMPMCDATAVALUES']._serialized_start = 325
    _globals['_MEMPMCDATAVALUES']._serialized_end = 448
    _globals['_MEMREGIONSETTINGS']._serialized_start = 450
    _globals['_MEMREGIONSETTINGS']._serialized_end = 568
    _globals['_MEMDATAQUERYRESULT']._serialized_start = 571
    _globals['_MEMDATAQUERYRESULT']._serialized_end = 725