"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import job_pb2 as job__pb2
from . import quantification_meta_pb2 as quantification__meta__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bquantification-create.proto\x1a\tjob.proto\x1a\x19quantification-meta.proto"4\n\x0eQuantCreateReq\x12"\n\x06params\x18\x01 \x01(\x0b2\x12.QuantCreateParams"-\n\x0fQuantCreateResp\x12\x1a\n\x06status\x18\x01 \x01(\x0b2\n.JobStatus"@\n\x0eQuantCreateUpd\x12\x1a\n\x06status\x18\x01 \x01(\x0b2\n.JobStatus\x12\x12\n\nresultData\x18\x02 \x01(\x0cB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'quantification_create_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_QUANTCREATEREQ']._serialized_start = 69
    _globals['_QUANTCREATEREQ']._serialized_end = 121
    _globals['_QUANTCREATERESP']._serialized_start = 123
    _globals['_QUANTCREATERESP']._serialized_end = 168
    _globals['_QUANTCREATEUPD']._serialized_start = 170
    _globals['_QUANTCREATEUPD']._serialized_end = 234