"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import job_pb2 as job__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ejob-msgs.proto\x1a\tjob.proto"\x0c\n\nJobListReq"\'\n\x0bJobListResp\x12\x18\n\x04jobs\x18\x01 \x03(\x0b2\n.JobStatus"%\n\nJobListUpd\x12\x17\n\x03job\x18\x01 \x01(\x0b2\n.JobStatusB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'job_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_JOBLISTREQ']._serialized_start = 29
    _globals['_JOBLISTREQ']._serialized_end = 41
    _globals['_JOBLISTRESP']._serialized_start = 43
    _globals['_JOBLISTRESP']._serialized_end = 82
    _globals['_JOBLISTUPD']._serialized_start = 84
    _globals['_JOBLISTUPD']._serialized_end = 121