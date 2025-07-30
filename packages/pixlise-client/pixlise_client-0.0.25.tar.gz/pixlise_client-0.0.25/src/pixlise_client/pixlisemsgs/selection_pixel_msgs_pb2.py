"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import scan_pb2 as scan__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1aselection-pixel-msgs.proto\x1a\nscan.proto"\'\n\x16SelectedImagePixelsReq\x12\r\n\x05image\x18\x01 \x01(\t"@\n\x17SelectedImagePixelsResp\x12%\n\x0cpixelIndexes\x18\x01 \x01(\x0b2\x0f.ScanEntryRange"S\n\x1bSelectedImagePixelsWriteReq\x12\r\n\x05image\x18\x01 \x01(\t\x12%\n\x0cpixelIndexes\x18\x02 \x01(\x0b2\x0f.ScanEntryRange"\x1e\n\x1cSelectedImagePixelsWriteRespB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'selection_pixel_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SELECTEDIMAGEPIXELSREQ']._serialized_start = 42
    _globals['_SELECTEDIMAGEPIXELSREQ']._serialized_end = 81
    _globals['_SELECTEDIMAGEPIXELSRESP']._serialized_start = 83
    _globals['_SELECTEDIMAGEPIXELSRESP']._serialized_end = 147
    _globals['_SELECTEDIMAGEPIXELSWRITEREQ']._serialized_start = 149
    _globals['_SELECTEDIMAGEPIXELSWRITEREQ']._serialized_end = 232
    _globals['_SELECTEDIMAGEPIXELSWRITERESP']._serialized_start = 234
    _globals['_SELECTEDIMAGEPIXELSWRITERESP']._serialized_end = 264