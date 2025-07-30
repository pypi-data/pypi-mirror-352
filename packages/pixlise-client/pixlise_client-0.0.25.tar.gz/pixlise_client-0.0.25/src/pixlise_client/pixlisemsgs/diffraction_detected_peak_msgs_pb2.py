"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import diffraction_data_pb2 as diffraction__data__pb2
from . import scan_pb2 as scan__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n$diffraction-detected-peak-msgs.proto\x1a\x16diffraction-data.proto\x1a\nscan.proto"O\n\x1bDetectedDiffractionPeaksReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12 \n\x07entries\x18\x02 \x01(\x0b2\x0f.ScanEntryRange"Y\n\x1cDetectedDiffractionPeaksResp\x129\n\x10peaksPerLocation\x18\x01 \x03(\x0b2\x1f.DetectedDiffractionPerLocationB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'diffraction_detected_peak_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_DETECTEDDIFFRACTIONPEAKSREQ']._serialized_start = 76
    _globals['_DETECTEDDIFFRACTIONPEAKSREQ']._serialized_end = 155
    _globals['_DETECTEDDIFFRACTIONPEAKSRESP']._serialized_start = 157
    _globals['_DETECTEDDIFFRACTIONPEAKSRESP']._serialized_end = 246