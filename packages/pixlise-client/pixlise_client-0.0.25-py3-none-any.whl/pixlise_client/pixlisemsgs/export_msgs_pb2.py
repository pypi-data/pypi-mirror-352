"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import export_pb2 as export__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11export-msgs.proto\x1a\x0cexport.proto"\x7f\n\x0eExportFilesReq\x12$\n\x0bexportTypes\x18\x01 \x03(\x0e2\x0f.ExportDataType\x12\x0e\n\x06scanId\x18\x02 \x01(\t\x12\x0f\n\x07quantId\x18\x03 \x01(\t\x12\x0e\n\x06roiIds\x18\x04 \x03(\t\x12\x16\n\x0eimageFileNames\x18\x05 \x03(\t"-\n\x0fExportFilesResp\x12\x1a\n\x05files\x18\x01 \x03(\x0b2\x0b.ExportFile*4\n\x0eExportDataType\x12\x0f\n\x0bEDT_UNKNOWN\x10\x00\x12\x11\n\rEDT_QUANT_CSV\x10\x01B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'export_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_EXPORTDATATYPE']._serialized_start = 211
    _globals['_EXPORTDATATYPE']._serialized_end = 263
    _globals['_EXPORTFILESREQ']._serialized_start = 35
    _globals['_EXPORTFILESREQ']._serialized_end = 162
    _globals['_EXPORTFILESRESP']._serialized_start = 164
    _globals['_EXPORTFILESRESP']._serialized_end = 209