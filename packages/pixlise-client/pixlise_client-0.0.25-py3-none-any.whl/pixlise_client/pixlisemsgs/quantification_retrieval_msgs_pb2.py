"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import quantification_meta_pb2 as quantification__meta__pb2
from . import quantification_pb2 as quantification__pb2
from . import search_params_pb2 as search__params__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#quantification-retrieval-msgs.proto\x1a\x19quantification-meta.proto\x1a\x14quantification.proto\x1a\x13search-params.proto"3\n\x0cQuantListReq\x12#\n\x0csearchParams\x18\x01 \x01(\x0b2\r.SearchParams"7\n\rQuantListResp\x12&\n\x06quants\x18\x01 \x03(\x0b2\x16.QuantificationSummary"3\n\x0bQuantGetReq\x12\x0f\n\x07quantId\x18\x01 \x01(\t\x12\x13\n\x0bsummaryOnly\x18\x02 \x01(\x08"V\n\x0cQuantGetResp\x12\'\n\x07summary\x18\x01 \x01(\x0b2\x16.QuantificationSummary\x12\x1d\n\x04data\x18\x02 \x01(\x0b2\x0f.Quantification""\n\x0fQuantLogListReq\x12\x0f\n\x07quantId\x18\x01 \x01(\t"%\n\x10QuantLogListResp\x12\x11\n\tfileNames\x18\x01 \x03(\t"2\n\x0eQuantLogGetReq\x12\x0f\n\x07quantId\x18\x01 \x01(\t\x12\x0f\n\x07logName\x18\x02 \x01(\t""\n\x0fQuantLogGetResp\x12\x0f\n\x07logData\x18\x01 \x01(\t"%\n\x12QuantRawDataGetReq\x12\x0f\n\x07quantId\x18\x01 \x01(\t"#\n\x13QuantRawDataGetResp\x12\x0c\n\x04data\x18\x01 \x01(\t"e\n\x15QuantLastOutputGetReq\x12$\n\noutputType\x18\x01 \x01(\x0e2\x10.QuantOutputType\x12\x0e\n\x06scanId\x18\x02 \x01(\t\x12\x16\n\x0epiquantCommand\x18\x03 \x01(\t"(\n\x16QuantLastOutputGetResp\x12\x0e\n\x06output\x18\x01 \x01(\t*:\n\x0fQuantOutputType\x12\x0e\n\nQO_UNKNOWN\x10\x00\x12\x0b\n\x07QO_DATA\x10\x01\x12\n\n\x06QO_LOG\x10\x02B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'quantification_retrieval_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_QUANTOUTPUTTYPE']._serialized_start = 744
    _globals['_QUANTOUTPUTTYPE']._serialized_end = 802
    _globals['_QUANTLISTREQ']._serialized_start = 109
    _globals['_QUANTLISTREQ']._serialized_end = 160
    _globals['_QUANTLISTRESP']._serialized_start = 162
    _globals['_QUANTLISTRESP']._serialized_end = 217
    _globals['_QUANTGETREQ']._serialized_start = 219
    _globals['_QUANTGETREQ']._serialized_end = 270
    _globals['_QUANTGETRESP']._serialized_start = 272
    _globals['_QUANTGETRESP']._serialized_end = 358
    _globals['_QUANTLOGLISTREQ']._serialized_start = 360
    _globals['_QUANTLOGLISTREQ']._serialized_end = 394
    _globals['_QUANTLOGLISTRESP']._serialized_start = 396
    _globals['_QUANTLOGLISTRESP']._serialized_end = 433
    _globals['_QUANTLOGGETREQ']._serialized_start = 435
    _globals['_QUANTLOGGETREQ']._serialized_end = 485
    _globals['_QUANTLOGGETRESP']._serialized_start = 487
    _globals['_QUANTLOGGETRESP']._serialized_end = 521
    _globals['_QUANTRAWDATAGETREQ']._serialized_start = 523
    _globals['_QUANTRAWDATAGETREQ']._serialized_end = 560
    _globals['_QUANTRAWDATAGETRESP']._serialized_start = 562
    _globals['_QUANTRAWDATAGETRESP']._serialized_end = 597
    _globals['_QUANTLASTOUTPUTGETREQ']._serialized_start = 599
    _globals['_QUANTLASTOUTPUTGETREQ']._serialized_end = 700
    _globals['_QUANTLASTOUTPUTGETRESP']._serialized_start = 702
    _globals['_QUANTLASTOUTPUTGETRESP']._serialized_end = 742