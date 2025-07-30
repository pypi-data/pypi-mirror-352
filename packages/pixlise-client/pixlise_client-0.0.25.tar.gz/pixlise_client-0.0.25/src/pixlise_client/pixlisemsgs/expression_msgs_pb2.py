"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import expressions_pb2 as expressions__pb2
from . import search_params_pb2 as search__params__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15expression-msgs.proto\x1a\x11expressions.proto\x1a\x13search-params.proto"8\n\x11ExpressionListReq\x12#\n\x0csearchParams\x18\x01 \x01(\x0b2\r.SearchParams"\x94\x01\n\x12ExpressionListResp\x129\n\x0bexpressions\x18\x01 \x03(\x0b2$.ExpressionListResp.ExpressionsEntry\x1aC\n\x10ExpressionsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1e\n\x05value\x18\x02 \x01(\x0b2\x0f.DataExpression:\x028\x01"\x1e\n\x10ExpressionGetReq\x12\n\n\x02id\x18\x01 \x01(\t"8\n\x11ExpressionGetResp\x12#\n\nexpression\x18\x01 \x01(\x0b2\x0f.DataExpression"9\n\x12ExpressionWriteReq\x12#\n\nexpression\x18\x01 \x01(\x0b2\x0f.DataExpression":\n\x13ExpressionWriteResp\x12#\n\nexpression\x18\x01 \x01(\x0b2\x0f.DataExpression"!\n\x13ExpressionDeleteReq\x12\n\n\x02id\x18\x01 \x01(\t"\x16\n\x14ExpressionDeleteResp"Q\n\x1aExpressionWriteExecStatReq\x12\n\n\x02id\x18\x01 \x01(\t\x12\'\n\x05stats\x18\x02 \x01(\x0b2\x18.DataExpressionExecStats"\x1d\n\x1bExpressionWriteExecStatResp"d\n!ExpressionDisplaySettingsWriteReq\x12\n\n\x02id\x18\x01 \x01(\t\x123\n\x0fdisplaySettings\x18\x02 \x01(\x0b2\x1a.ExpressionDisplaySettings"Y\n"ExpressionDisplaySettingsWriteResp\x123\n\x0fdisplaySettings\x18\x01 \x01(\x0b2\x1a.ExpressionDisplaySettings"-\n\x1fExpressionDisplaySettingsGetReq\x12\n\n\x02id\x18\x01 \x01(\t"W\n ExpressionDisplaySettingsGetResp\x123\n\x0fdisplaySettings\x18\x01 \x01(\x0b2\x1a.ExpressionDisplaySettingsB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'expression_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_EXPRESSIONLISTRESP_EXPRESSIONSENTRY']._options = None
    _globals['_EXPRESSIONLISTRESP_EXPRESSIONSENTRY']._serialized_options = b'8\x01'
    _globals['_EXPRESSIONLISTREQ']._serialized_start = 65
    _globals['_EXPRESSIONLISTREQ']._serialized_end = 121
    _globals['_EXPRESSIONLISTRESP']._serialized_start = 124
    _globals['_EXPRESSIONLISTRESP']._serialized_end = 272
    _globals['_EXPRESSIONLISTRESP_EXPRESSIONSENTRY']._serialized_start = 205
    _globals['_EXPRESSIONLISTRESP_EXPRESSIONSENTRY']._serialized_end = 272
    _globals['_EXPRESSIONGETREQ']._serialized_start = 274
    _globals['_EXPRESSIONGETREQ']._serialized_end = 304
    _globals['_EXPRESSIONGETRESP']._serialized_start = 306
    _globals['_EXPRESSIONGETRESP']._serialized_end = 362
    _globals['_EXPRESSIONWRITEREQ']._serialized_start = 364
    _globals['_EXPRESSIONWRITEREQ']._serialized_end = 421
    _globals['_EXPRESSIONWRITERESP']._serialized_start = 423
    _globals['_EXPRESSIONWRITERESP']._serialized_end = 481
    _globals['_EXPRESSIONDELETEREQ']._serialized_start = 483
    _globals['_EXPRESSIONDELETEREQ']._serialized_end = 516
    _globals['_EXPRESSIONDELETERESP']._serialized_start = 518
    _globals['_EXPRESSIONDELETERESP']._serialized_end = 540
    _globals['_EXPRESSIONWRITEEXECSTATREQ']._serialized_start = 542
    _globals['_EXPRESSIONWRITEEXECSTATREQ']._serialized_end = 623
    _globals['_EXPRESSIONWRITEEXECSTATRESP']._serialized_start = 625
    _globals['_EXPRESSIONWRITEEXECSTATRESP']._serialized_end = 654
    _globals['_EXPRESSIONDISPLAYSETTINGSWRITEREQ']._serialized_start = 656
    _globals['_EXPRESSIONDISPLAYSETTINGSWRITEREQ']._serialized_end = 756
    _globals['_EXPRESSIONDISPLAYSETTINGSWRITERESP']._serialized_start = 758
    _globals['_EXPRESSIONDISPLAYSETTINGSWRITERESP']._serialized_end = 847
    _globals['_EXPRESSIONDISPLAYSETTINGSGETREQ']._serialized_start = 849
    _globals['_EXPRESSIONDISPLAYSETTINGSGETREQ']._serialized_end = 894
    _globals['_EXPRESSIONDISPLAYSETTINGSGETRESP']._serialized_start = 896
    _globals['_EXPRESSIONDISPLAYSETTINGSGETRESP']._serialized_end = 983