"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import diffraction_data_pb2 as diffraction__data__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1ddiffraction-manual-msgs.proto\x1a\x16diffraction-data.proto".\n\x1cDiffractionPeakManualListReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t"\x9f\x01\n\x1dDiffractionPeakManualListResp\x128\n\x05peaks\x18\x01 \x03(\x0b2).DiffractionPeakManualListResp.PeaksEntry\x1aD\n\nPeaksEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12%\n\x05value\x18\x02 \x01(\x0b2\x16.ManualDiffractionPeak:\x028\x01"P\n\x1eDiffractionPeakManualInsertReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12\x0b\n\x03pmc\x18\x02 \x01(\x05\x12\x11\n\tenergykeV\x18\x03 \x01(\x02"4\n\x1fDiffractionPeakManualInsertResp\x12\x11\n\tcreatedId\x18\x01 \x01(\t",\n\x1eDiffractionPeakManualDeleteReq\x12\n\n\x02id\x18\x01 \x01(\t"!\n\x1fDiffractionPeakManualDeleteRespB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'diffraction_manual_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_DIFFRACTIONPEAKMANUALLISTRESP_PEAKSENTRY']._options = None
    _globals['_DIFFRACTIONPEAKMANUALLISTRESP_PEAKSENTRY']._serialized_options = b'8\x01'
    _globals['_DIFFRACTIONPEAKMANUALLISTREQ']._serialized_start = 57
    _globals['_DIFFRACTIONPEAKMANUALLISTREQ']._serialized_end = 103
    _globals['_DIFFRACTIONPEAKMANUALLISTRESP']._serialized_start = 106
    _globals['_DIFFRACTIONPEAKMANUALLISTRESP']._serialized_end = 265
    _globals['_DIFFRACTIONPEAKMANUALLISTRESP_PEAKSENTRY']._serialized_start = 197
    _globals['_DIFFRACTIONPEAKMANUALLISTRESP_PEAKSENTRY']._serialized_end = 265
    _globals['_DIFFRACTIONPEAKMANUALINSERTREQ']._serialized_start = 267
    _globals['_DIFFRACTIONPEAKMANUALINSERTREQ']._serialized_end = 347
    _globals['_DIFFRACTIONPEAKMANUALINSERTRESP']._serialized_start = 349
    _globals['_DIFFRACTIONPEAKMANUALINSERTRESP']._serialized_end = 401
    _globals['_DIFFRACTIONPEAKMANUALDELETEREQ']._serialized_start = 403
    _globals['_DIFFRACTIONPEAKMANUALDELETEREQ']._serialized_end = 447
    _globals['_DIFFRACTIONPEAKMANUALDELETERESP']._serialized_start = 449
    _globals['_DIFFRACTIONPEAKMANUALDELETERESP']._serialized_end = 482