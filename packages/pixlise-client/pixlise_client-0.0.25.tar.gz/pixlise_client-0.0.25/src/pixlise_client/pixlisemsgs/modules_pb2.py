"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import ownership_access_pb2 as ownership__access__pb2
from . import version_pb2 as version__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rmodules.proto\x1a\x16ownership-access.proto\x1a\rversion.proto"u\n\x0cDataModuleDB\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08comments\x18\x03 \x01(\t\x12\x17\n\x0fmodifiedUnixSec\x18\x04 \x01(\r\x12 \n\x05owner\x18\x05 \x01(\x0b2\x11.OwnershipSummary"\xa4\x01\n\x13DataModuleVersionDB\x12\n\n\x02id\x18\x01 \x01(\t\x12\x10\n\x08moduleId\x18\x02 \x01(\t\x12!\n\x07version\x18\x03 \x01(\x0b2\x10.SemanticVersion\x12\x0c\n\x04tags\x18\x04 \x03(\t\x12\x10\n\x08comments\x18\x05 \x01(\t\x12\x18\n\x10timeStampUnixSec\x18\x06 \x01(\r\x12\x12\n\nsourceCode\x18\x07 \x01(\t"\x84\x01\n\x11DataModuleVersion\x12!\n\x07version\x18\x01 \x01(\x0b2\x10.SemanticVersion\x12\x0c\n\x04tags\x18\x02 \x03(\t\x12\x10\n\x08comments\x18\x03 \x01(\t\x12\x18\n\x10timeStampUnixSec\x18\x04 \x01(\r\x12\x12\n\nsourceCode\x18\x05 \x01(\t"\x9b\x01\n\nDataModule\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08comments\x18\x03 \x01(\t\x12\x17\n\x0fmodifiedUnixSec\x18\x04 \x01(\r\x12"\n\x07creator\x18\x05 \x01(\x0b2\x11.OwnershipSummary\x12$\n\x08versions\x18\x06 \x03(\x0b2\x12.DataModuleVersionB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'modules_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_DATAMODULEDB']._serialized_start = 56
    _globals['_DATAMODULEDB']._serialized_end = 173
    _globals['_DATAMODULEVERSIONDB']._serialized_start = 176
    _globals['_DATAMODULEVERSIONDB']._serialized_end = 340
    _globals['_DATAMODULEVERSION']._serialized_start = 343
    _globals['_DATAMODULEVERSION']._serialized_end = 475
    _globals['_DATAMODULE']._serialized_start = 478
    _globals['_DATAMODULE']._serialized_end = 633