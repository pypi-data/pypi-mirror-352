"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1aquantification-multi.proto";\n\x10QuantCombineItem\x12\r\n\x05roiId\x18\x01 \x01(\t\x12\x18\n\x10quantificationId\x18\x02 \x01(\t"<\n\x14QuantCombineItemList\x12$\n\troiZStack\x18\x01 \x03(\x0b2\x11.QuantCombineItem"i\n\x16QuantCombineItemListDB\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06userId\x18\x02 \x01(\t\x12\x0e\n\x06scanId\x18\x03 \x01(\t\x12#\n\x04list\x18\x04 \x01(\x0b2\x15.QuantCombineItemList"J\n\x16QuantCombineSummaryRow\x12\x0e\n\x06values\x18\x01 \x03(\x02\x12\x0e\n\x06roiIds\x18\x02 \x03(\t\x12\x10\n\x08roiNames\x18\x03 \x03(\t"\xba\x01\n\x13QuantCombineSummary\x12\x11\n\tdetectors\x18\x01 \x03(\t\x12@\n\x0eweightPercents\x18\x02 \x03(\x0b2(.QuantCombineSummary.WeightPercentsEntry\x1aN\n\x13WeightPercentsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12&\n\x05value\x18\x02 \x01(\x0b2\x17.QuantCombineSummaryRow:\x028\x01"\xb4\x01\n\x14QuantComparisonTable\x12\x0f\n\x07quantId\x18\x01 \x01(\t\x12\x11\n\tquantName\x18\x02 \x01(\t\x12A\n\x0eelementWeights\x18\x03 \x03(\x0b2).QuantComparisonTable.ElementWeightsEntry\x1a5\n\x13ElementWeightsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x02:\x028\x01B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'quantification_multi_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_QUANTCOMBINESUMMARY_WEIGHTPERCENTSENTRY']._options = None
    _globals['_QUANTCOMBINESUMMARY_WEIGHTPERCENTSENTRY']._serialized_options = b'8\x01'
    _globals['_QUANTCOMPARISONTABLE_ELEMENTWEIGHTSENTRY']._options = None
    _globals['_QUANTCOMPARISONTABLE_ELEMENTWEIGHTSENTRY']._serialized_options = b'8\x01'
    _globals['_QUANTCOMBINEITEM']._serialized_start = 30
    _globals['_QUANTCOMBINEITEM']._serialized_end = 89
    _globals['_QUANTCOMBINEITEMLIST']._serialized_start = 91
    _globals['_QUANTCOMBINEITEMLIST']._serialized_end = 151
    _globals['_QUANTCOMBINEITEMLISTDB']._serialized_start = 153
    _globals['_QUANTCOMBINEITEMLISTDB']._serialized_end = 258
    _globals['_QUANTCOMBINESUMMARYROW']._serialized_start = 260
    _globals['_QUANTCOMBINESUMMARYROW']._serialized_end = 334
    _globals['_QUANTCOMBINESUMMARY']._serialized_start = 337
    _globals['_QUANTCOMBINESUMMARY']._serialized_end = 523
    _globals['_QUANTCOMBINESUMMARY_WEIGHTPERCENTSENTRY']._serialized_start = 445
    _globals['_QUANTCOMBINESUMMARY_WEIGHTPERCENTSENTRY']._serialized_end = 523
    _globals['_QUANTCOMPARISONTABLE']._serialized_start = 526
    _globals['_QUANTCOMPARISONTABLE']._serialized_end = 706
    _globals['_QUANTCOMPARISONTABLE_ELEMENTWEIGHTSENTRY']._serialized_start = 653
    _globals['_QUANTCOMPARISONTABLE_ELEMENTWEIGHTSENTRY']._serialized_end = 706