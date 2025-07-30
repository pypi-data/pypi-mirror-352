"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n quantification-upload-msgs.proto"Q\n\x0eQuantUploadReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08comments\x18\x03 \x01(\t\x12\x0f\n\x07csvData\x18\x05 \x01(\t")\n\x0fQuantUploadResp\x12\x16\n\x0ecreatedQuantId\x18\x01 \x01(\tB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'quantification_upload_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_QUANTUPLOADREQ']._serialized_start = 36
    _globals['_QUANTUPLOADREQ']._serialized_end = 117
    _globals['_QUANTUPLOADRESP']._serialized_start = 119
    _globals['_QUANTUPLOADRESP']._serialized_end = 160