"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import scan_pb2 as scan__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19scan-entry-metadata.proto\x1a\nscan.proto"\x7f\n\x11ScanEntryMetadata\x12*\n\x04meta\x18\x01 \x03(\x0b2\x1c.ScanEntryMetadata.MetaEntry\x1a>\n\tMetaEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12 \n\x05value\x18\x02 \x01(\x0b2\x11.ScanMetaDataItem:\x028\x01B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'scan_entry_metadata_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SCANENTRYMETADATA_METAENTRY']._options = None
    _globals['_SCANENTRYMETADATA_METAENTRY']._serialized_options = b'8\x01'
    _globals['_SCANENTRYMETADATA']._serialized_start = 41
    _globals['_SCANENTRYMETADATA']._serialized_end = 168
    _globals['_SCANENTRYMETADATA_METAENTRY']._serialized_start = 106
    _globals['_SCANENTRYMETADATA_METAENTRY']._serialized_end = 168