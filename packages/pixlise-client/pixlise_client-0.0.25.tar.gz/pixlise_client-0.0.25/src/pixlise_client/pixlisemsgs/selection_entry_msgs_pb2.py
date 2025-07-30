"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import scan_pb2 as scan__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1aselection-entry-msgs.proto\x1a\nscan.proto")\n\x16SelectedScanEntriesReq\x12\x0f\n\x07scanIds\x18\x01 \x03(\t"\xb3\x01\n\x17SelectedScanEntriesResp\x12L\n\x12scanIdEntryIndexes\x18\x01 \x03(\x0b20.SelectedScanEntriesResp.ScanIdEntryIndexesEntry\x1aJ\n\x17ScanIdEntryIndexesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1e\n\x05value\x18\x02 \x01(\x0b2\x0f.ScanEntryRange:\x028\x01"\xbb\x01\n\x1bSelectedScanEntriesWriteReq\x12P\n\x12scanIdEntryIndexes\x18\x01 \x03(\x0b24.SelectedScanEntriesWriteReq.ScanIdEntryIndexesEntry\x1aJ\n\x17ScanIdEntryIndexesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1e\n\x05value\x18\x02 \x01(\x0b2\x0f.ScanEntryRange:\x028\x01"\x1e\n\x1cSelectedScanEntriesWriteRespB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'selection_entry_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SELECTEDSCANENTRIESRESP_SCANIDENTRYINDEXESENTRY']._options = None
    _globals['_SELECTEDSCANENTRIESRESP_SCANIDENTRYINDEXESENTRY']._serialized_options = b'8\x01'
    _globals['_SELECTEDSCANENTRIESWRITEREQ_SCANIDENTRYINDEXESENTRY']._options = None
    _globals['_SELECTEDSCANENTRIESWRITEREQ_SCANIDENTRYINDEXESENTRY']._serialized_options = b'8\x01'
    _globals['_SELECTEDSCANENTRIESREQ']._serialized_start = 42
    _globals['_SELECTEDSCANENTRIESREQ']._serialized_end = 83
    _globals['_SELECTEDSCANENTRIESRESP']._serialized_start = 86
    _globals['_SELECTEDSCANENTRIESRESP']._serialized_end = 265
    _globals['_SELECTEDSCANENTRIESRESP_SCANIDENTRYINDEXESENTRY']._serialized_start = 191
    _globals['_SELECTEDSCANENTRIESRESP_SCANIDENTRYINDEXESENTRY']._serialized_end = 265
    _globals['_SELECTEDSCANENTRIESWRITEREQ']._serialized_start = 268
    _globals['_SELECTEDSCANENTRIESWRITEREQ']._serialized_end = 455
    _globals['_SELECTEDSCANENTRIESWRITEREQ_SCANIDENTRYINDEXESENTRY']._serialized_start = 191
    _globals['_SELECTEDSCANENTRIESWRITEREQ_SCANIDENTRYINDEXESENTRY']._serialized_end = 265
    _globals['_SELECTEDSCANENTRIESWRITERESP']._serialized_start = 457
    _globals['_SELECTEDSCANENTRIESWRITERESP']._serialized_end = 487