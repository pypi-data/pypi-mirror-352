"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import quantification_multi_pb2 as quantification__multi__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fquantification-multi-msgs.proto\x1a\x1aquantification-multi.proto"\x7f\n\x0fQuantCombineReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12$\n\troiZStack\x18\x02 \x03(\x0b2\x11.QuantCombineItem\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x13\n\x0bdescription\x18\x04 \x01(\t\x12\x13\n\x0bsummaryOnly\x18\x05 \x01(\x08"]\n\x10QuantCombineResp\x12\x0f\n\x05jobId\x18\x01 \x01(\tH\x00\x12\'\n\x07summary\x18\x02 \x01(\x0b2\x14.QuantCombineSummaryH\x00B\x0f\n\rCombineResult"(\n\x16QuantCombineListGetReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t">\n\x17QuantCombineListGetResp\x12#\n\x04list\x18\x01 \x01(\x0b2\x15.QuantCombineItemList"O\n\x18QuantCombineListWriteReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12#\n\x04list\x18\x02 \x01(\x0b2\x15.QuantCombineItemList"\x1b\n\x19QuantCombineListWriteResp"g\n\x14MultiQuantCompareReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12\x10\n\x08reqRoiId\x18\x02 \x01(\t\x12\x10\n\x08quantIds\x18\x03 \x03(\t\x12\x1b\n\x13remainingPointsPMCs\x18\x04 \x03(\x05"R\n\x15MultiQuantCompareResp\x12\r\n\x05roiId\x18\x01 \x01(\t\x12*\n\x0bquantTables\x18\x02 \x03(\x0b2\x15.QuantComparisonTableB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'quantification_multi_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_QUANTCOMBINEREQ']._serialized_start = 63
    _globals['_QUANTCOMBINEREQ']._serialized_end = 190
    _globals['_QUANTCOMBINERESP']._serialized_start = 192
    _globals['_QUANTCOMBINERESP']._serialized_end = 285
    _globals['_QUANTCOMBINELISTGETREQ']._serialized_start = 287
    _globals['_QUANTCOMBINELISTGETREQ']._serialized_end = 327
    _globals['_QUANTCOMBINELISTGETRESP']._serialized_start = 329
    _globals['_QUANTCOMBINELISTGETRESP']._serialized_end = 391
    _globals['_QUANTCOMBINELISTWRITEREQ']._serialized_start = 393
    _globals['_QUANTCOMBINELISTWRITEREQ']._serialized_end = 472
    _globals['_QUANTCOMBINELISTWRITERESP']._serialized_start = 474
    _globals['_QUANTCOMBINELISTWRITERESP']._serialized_end = 501
    _globals['_MULTIQUANTCOMPAREREQ']._serialized_start = 503
    _globals['_MULTIQUANTCOMPAREREQ']._serialized_end = 606
    _globals['_MULTIQUANTCOMPARERESP']._serialized_start = 608
    _globals['_MULTIQUANTCOMPARERESP']._serialized_end = 690