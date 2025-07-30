"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import scan_entry_metadata_pb2 as scan__entry__metadata__pb2
from . import scan_pb2 as scan__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1escan-entry-metadata-msgs.proto\x1a\x19scan-entry-metadata.proto\x1a\nscan.proto"H\n\x14ScanEntryMetadataReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12 \n\x07entries\x18\x02 \x01(\x0b2\x0f.ScanEntryRange"<\n\x15ScanEntryMetadataResp\x12#\n\x07entries\x18\x01 \x03(\x0b2\x12.ScanEntryMetadataB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'scan_entry_metadata_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SCANENTRYMETADATAREQ']._serialized_start = 73
    _globals['_SCANENTRYMETADATAREQ']._serialized_end = 145
    _globals['_SCANENTRYMETADATARESP']._serialized_start = 147
    _globals['_SCANENTRYMETADATARESP']._serialized_end = 207