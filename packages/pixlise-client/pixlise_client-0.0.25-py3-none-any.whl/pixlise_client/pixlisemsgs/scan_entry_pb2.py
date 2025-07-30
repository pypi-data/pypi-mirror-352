"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10scan-entry.proto"\xcb\x01\n\tScanEntry\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x11\n\ttimestamp\x18\x02 \x01(\r\x12\x0e\n\x06images\x18\x03 \x01(\r\x12\x0c\n\x04meta\x18\x05 \x01(\x08\x12\x10\n\x08location\x18\x06 \x01(\x08\x12\x19\n\x11pseudoIntensities\x18\x07 \x01(\x08\x12\x15\n\rnormalSpectra\x18\x08 \x01(\r\x12\x14\n\x0cdwellSpectra\x18\t \x01(\r\x12\x13\n\x0bbulkSpectra\x18\n \x01(\r\x12\x12\n\nmaxSpectra\x18\x0b \x01(\rB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'scan_entry_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SCANENTRY']._serialized_start = 21
    _globals['_SCANENTRY']._serialized_end = 224