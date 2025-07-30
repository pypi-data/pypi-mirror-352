"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import scan_entry_pb2 as scan__entry__pb2
from . import scan_pb2 as scan__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15scan-entry-msgs.proto\x1a\x10scan-entry.proto\x1a\nscan.proto"@\n\x0cScanEntryReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12 \n\x07entries\x18\x02 \x01(\x0b2\x0f.ScanEntryRange",\n\rScanEntryResp\x12\x1b\n\x07entries\x18\x01 \x03(\x0b2\n.ScanEntryB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'scan_entry_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SCANENTRYREQ']._serialized_start = 55
    _globals['_SCANENTRYREQ']._serialized_end = 119
    _globals['_SCANENTRYRESP']._serialized_start = 121
    _globals['_SCANENTRYRESP']._serialized_end = 165