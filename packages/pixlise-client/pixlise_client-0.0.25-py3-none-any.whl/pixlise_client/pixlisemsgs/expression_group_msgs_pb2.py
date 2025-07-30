"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import expression_group_pb2 as expression__group__pb2
from . import search_params_pb2 as search__params__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bexpression-group-msgs.proto\x1a\x16expression-group.proto\x1a\x13search-params.proto"=\n\x16ExpressionGroupListReq\x12#\n\x0csearchParams\x18\x01 \x01(\x0b2\r.SearchParams"\x90\x01\n\x17ExpressionGroupListResp\x124\n\x06groups\x18\x01 \x03(\x0b2$.ExpressionGroupListResp.GroupsEntry\x1a?\n\x0bGroupsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1f\n\x05value\x18\x02 \x01(\x0b2\x10.ExpressionGroup:\x028\x01"#\n\x15ExpressionGroupGetReq\x12\n\n\x02id\x18\x01 \x01(\t"9\n\x16ExpressionGroupGetResp\x12\x1f\n\x05group\x18\x01 \x01(\x0b2\x10.ExpressionGroup":\n\x17ExpressionGroupWriteReq\x12\x1f\n\x05group\x18\x01 \x01(\x0b2\x10.ExpressionGroup";\n\x18ExpressionGroupWriteResp\x12\x1f\n\x05group\x18\x01 \x01(\x0b2\x10.ExpressionGroup"&\n\x18ExpressionGroupDeleteReq\x12\n\n\x02id\x18\x01 \x01(\t"\x1b\n\x19ExpressionGroupDeleteRespB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'expression_group_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_EXPRESSIONGROUPLISTRESP_GROUPSENTRY']._options = None
    _globals['_EXPRESSIONGROUPLISTRESP_GROUPSENTRY']._serialized_options = b'8\x01'
    _globals['_EXPRESSIONGROUPLISTREQ']._serialized_start = 76
    _globals['_EXPRESSIONGROUPLISTREQ']._serialized_end = 137
    _globals['_EXPRESSIONGROUPLISTRESP']._serialized_start = 140
    _globals['_EXPRESSIONGROUPLISTRESP']._serialized_end = 284
    _globals['_EXPRESSIONGROUPLISTRESP_GROUPSENTRY']._serialized_start = 221
    _globals['_EXPRESSIONGROUPLISTRESP_GROUPSENTRY']._serialized_end = 284
    _globals['_EXPRESSIONGROUPGETREQ']._serialized_start = 286
    _globals['_EXPRESSIONGROUPGETREQ']._serialized_end = 321
    _globals['_EXPRESSIONGROUPGETRESP']._serialized_start = 323
    _globals['_EXPRESSIONGROUPGETRESP']._serialized_end = 380
    _globals['_EXPRESSIONGROUPWRITEREQ']._serialized_start = 382
    _globals['_EXPRESSIONGROUPWRITEREQ']._serialized_end = 440
    _globals['_EXPRESSIONGROUPWRITERESP']._serialized_start = 442
    _globals['_EXPRESSIONGROUPWRITERESP']._serialized_end = 501
    _globals['_EXPRESSIONGROUPDELETEREQ']._serialized_start = 503
    _globals['_EXPRESSIONGROUPDELETEREQ']._serialized_end = 541
    _globals['_EXPRESSIONGROUPDELETERESP']._serialized_start = 543
    _globals['_EXPRESSIONGROUPDELETERESP']._serialized_end = 570