"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import job_pb2 as job__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16image-coreg-msgs.proto\x1a\tjob.proto".\n\x18ImportMarsViewerImageReq\x12\x12\n\ntriggerUrl\x18\x01 \x01(\t"*\n\x19ImportMarsViewerImageResp\x12\r\n\x05jobId\x18\x01 \x01(\t"6\n\x18ImportMarsViewerImageUpd\x12\x1a\n\x06status\x18\x01 \x01(\x0b2\n.JobStatusB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'image_coreg_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_IMPORTMARSVIEWERIMAGEREQ']._serialized_start = 37
    _globals['_IMPORTMARSVIEWERIMAGEREQ']._serialized_end = 83
    _globals['_IMPORTMARSVIEWERIMAGERESP']._serialized_start = 85
    _globals['_IMPORTMARSVIEWERIMAGERESP']._serialized_end = 127
    _globals['_IMPORTMARSVIEWERIMAGEUPD']._serialized_start = 129
    _globals['_IMPORTMARSVIEWERIMAGEUPD']._serialized_end = 183