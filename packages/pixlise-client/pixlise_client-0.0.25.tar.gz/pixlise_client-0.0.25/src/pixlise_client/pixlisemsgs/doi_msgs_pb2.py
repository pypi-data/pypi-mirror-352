"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import doi_pb2 as doi__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0edoi-msgs.proto\x1a\tdoi.proto"Z\n\x1cPublishExpressionToZenodoReq\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06output\x18\x02 \x01(\t\x12\x1e\n\x08metadata\x18\x03 \x01(\x0b2\x0c.DOIMetadata":\n\x1dPublishExpressionToZenodoResp\x12\x19\n\x03doi\x18\x01 \x01(\x0b2\x0c.DOIMetadata"\x1d\n\x0fZenodoDOIGetReq\x12\n\n\x02id\x18\x01 \x01(\t"-\n\x10ZenodoDOIGetResp\x12\x19\n\x03doi\x18\x01 \x01(\x0b2\x0c.DOIMetadataB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'doi_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_PUBLISHEXPRESSIONTOZENODOREQ']._serialized_start = 29
    _globals['_PUBLISHEXPRESSIONTOZENODOREQ']._serialized_end = 119
    _globals['_PUBLISHEXPRESSIONTOZENODORESP']._serialized_start = 121
    _globals['_PUBLISHEXPRESSIONTOZENODORESP']._serialized_end = 179
    _globals['_ZENODODOIGETREQ']._serialized_start = 181
    _globals['_ZENODODOIGETREQ']._serialized_end = 210
    _globals['_ZENODODOIGETRESP']._serialized_start = 212
    _globals['_ZENODODOIGETRESP']._serialized_end = 257