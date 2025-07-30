"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import element_set_pb2 as element__set__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16element-set-msgs.proto\x1a\x11element-set.proto"\x13\n\x11ElementSetListReq"\x97\x01\n\x12ElementSetListResp\x129\n\x0belementSets\x18\x01 \x03(\x0b2$.ElementSetListResp.ElementSetsEntry\x1aF\n\x10ElementSetsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12!\n\x05value\x18\x02 \x01(\x0b2\x12.ElementSetSummary:\x028\x01"\x1e\n\x10ElementSetGetReq\x12\n\n\x02id\x18\x01 \x01(\t"4\n\x11ElementSetGetResp\x12\x1f\n\nelementSet\x18\x01 \x01(\x0b2\x0b.ElementSet"5\n\x12ElementSetWriteReq\x12\x1f\n\nelementSet\x18\x01 \x01(\x0b2\x0b.ElementSet"6\n\x13ElementSetWriteResp\x12\x1f\n\nelementSet\x18\x01 \x01(\x0b2\x0b.ElementSet"!\n\x13ElementSetDeleteReq\x12\n\n\x02id\x18\x01 \x01(\t"\x16\n\x14ElementSetDeleteRespB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'element_set_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_ELEMENTSETLISTRESP_ELEMENTSETSENTRY']._options = None
    _globals['_ELEMENTSETLISTRESP_ELEMENTSETSENTRY']._serialized_options = b'8\x01'
    _globals['_ELEMENTSETLISTREQ']._serialized_start = 45
    _globals['_ELEMENTSETLISTREQ']._serialized_end = 64
    _globals['_ELEMENTSETLISTRESP']._serialized_start = 67
    _globals['_ELEMENTSETLISTRESP']._serialized_end = 218
    _globals['_ELEMENTSETLISTRESP_ELEMENTSETSENTRY']._serialized_start = 148
    _globals['_ELEMENTSETLISTRESP_ELEMENTSETSENTRY']._serialized_end = 218
    _globals['_ELEMENTSETGETREQ']._serialized_start = 220
    _globals['_ELEMENTSETGETREQ']._serialized_end = 250
    _globals['_ELEMENTSETGETRESP']._serialized_start = 252
    _globals['_ELEMENTSETGETRESP']._serialized_end = 304
    _globals['_ELEMENTSETWRITEREQ']._serialized_start = 306
    _globals['_ELEMENTSETWRITEREQ']._serialized_end = 359
    _globals['_ELEMENTSETWRITERESP']._serialized_start = 361
    _globals['_ELEMENTSETWRITERESP']._serialized_end = 415
    _globals['_ELEMENTSETDELETEREQ']._serialized_start = 417
    _globals['_ELEMENTSETDELETEREQ']._serialized_end = 450
    _globals['_ELEMENTSETDELETERESP']._serialized_start = 452
    _globals['_ELEMENTSETDELETERESP']._serialized_end = 474