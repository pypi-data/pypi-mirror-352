"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import diffraction_data_pb2 as diffraction__data__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1ddiffraction-status-msgs.proto\x1a\x16diffraction-data.proto".\n\x1cDiffractionPeakStatusListReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t"W\n\x1dDiffractionPeakStatusListResp\x126\n\x0cpeakStatuses\x18\x01 \x01(\x0b2 .DetectedDiffractionPeakStatuses"Z\n\x1dDiffractionPeakStatusWriteReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12\x19\n\x11diffractionPeakId\x18\x02 \x01(\t\x12\x0e\n\x06status\x18\x03 \x01(\t" \n\x1eDiffractionPeakStatusWriteResp"K\n\x1eDiffractionPeakStatusDeleteReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12\x19\n\x11diffractionPeakId\x18\x02 \x01(\t"!\n\x1fDiffractionPeakStatusDeleteRespB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'diffraction_status_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_DIFFRACTIONPEAKSTATUSLISTREQ']._serialized_start = 57
    _globals['_DIFFRACTIONPEAKSTATUSLISTREQ']._serialized_end = 103
    _globals['_DIFFRACTIONPEAKSTATUSLISTRESP']._serialized_start = 105
    _globals['_DIFFRACTIONPEAKSTATUSLISTRESP']._serialized_end = 192
    _globals['_DIFFRACTIONPEAKSTATUSWRITEREQ']._serialized_start = 194
    _globals['_DIFFRACTIONPEAKSTATUSWRITEREQ']._serialized_end = 284
    _globals['_DIFFRACTIONPEAKSTATUSWRITERESP']._serialized_start = 286
    _globals['_DIFFRACTIONPEAKSTATUSWRITERESP']._serialized_end = 318
    _globals['_DIFFRACTIONPEAKSTATUSDELETEREQ']._serialized_start = 320
    _globals['_DIFFRACTIONPEAKSTATUSDELETEREQ']._serialized_end = 395
    _globals['_DIFFRACTIONPEAKSTATUSDELETERESP']._serialized_start = 397
    _globals['_DIFFRACTIONPEAKSTATUSDELETERESP']._serialized_end = 430