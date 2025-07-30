"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import modules_pb2 as modules__pb2
from . import version_pb2 as version__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11module-msgs.proto\x1a\rmodules.proto\x1a\rversion.proto"\x13\n\x11DataModuleListReq"\x84\x01\n\x12DataModuleListResp\x121\n\x07modules\x18\x01 \x03(\x0b2 .DataModuleListResp.ModulesEntry\x1a;\n\x0cModulesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1a\n\x05value\x18\x02 \x01(\x0b2\x0b.DataModule:\x028\x01"A\n\x10DataModuleGetReq\x12\n\n\x02id\x18\x01 \x01(\t\x12!\n\x07version\x18\x02 \x01(\x0b2\x10.SemanticVersion"0\n\x11DataModuleGetResp\x12\x1b\n\x06module\x18\x01 \x01(\x0b2\x0b.DataModule"p\n\x12DataModuleWriteReq\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08comments\x18\x03 \x01(\t\x12\x19\n\x11initialSourceCode\x18\x04 \x01(\t\x12\x13\n\x0binitialTags\x18\x05 \x03(\t"2\n\x13DataModuleWriteResp\x12\x1b\n\x06module\x18\x01 \x01(\x0b2\x0b.DataModule"\x85\x01\n\x17DataModuleAddVersionReq\x12\x10\n\x08moduleId\x18\x01 \x01(\t\x12$\n\rversionUpdate\x18\x02 \x01(\x0e2\r.VersionField\x12\x12\n\nsourceCode\x18\x03 \x01(\t\x12\x10\n\x08comments\x18\x04 \x01(\t\x12\x0c\n\x04tags\x18\x05 \x03(\t"7\n\x18DataModuleAddVersionResp\x12\x1b\n\x06module\x18\x01 \x01(\x0b2\x0b.DataModuleB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'module_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_DATAMODULELISTRESP_MODULESENTRY']._options = None
    _globals['_DATAMODULELISTRESP_MODULESENTRY']._serialized_options = b'8\x01'
    _globals['_DATAMODULELISTREQ']._serialized_start = 51
    _globals['_DATAMODULELISTREQ']._serialized_end = 70
    _globals['_DATAMODULELISTRESP']._serialized_start = 73
    _globals['_DATAMODULELISTRESP']._serialized_end = 205
    _globals['_DATAMODULELISTRESP_MODULESENTRY']._serialized_start = 146
    _globals['_DATAMODULELISTRESP_MODULESENTRY']._serialized_end = 205
    _globals['_DATAMODULEGETREQ']._serialized_start = 207
    _globals['_DATAMODULEGETREQ']._serialized_end = 272
    _globals['_DATAMODULEGETRESP']._serialized_start = 274
    _globals['_DATAMODULEGETRESP']._serialized_end = 322
    _globals['_DATAMODULEWRITEREQ']._serialized_start = 324
    _globals['_DATAMODULEWRITEREQ']._serialized_end = 436
    _globals['_DATAMODULEWRITERESP']._serialized_start = 438
    _globals['_DATAMODULEWRITERESP']._serialized_end = 488
    _globals['_DATAMODULEADDVERSIONREQ']._serialized_start = 491
    _globals['_DATAMODULEADDVERSIONREQ']._serialized_end = 624
    _globals['_DATAMODULEADDVERSIONRESP']._serialized_start = 626
    _globals['_DATAMODULEADDVERSIONRESP']._serialized_end = 681