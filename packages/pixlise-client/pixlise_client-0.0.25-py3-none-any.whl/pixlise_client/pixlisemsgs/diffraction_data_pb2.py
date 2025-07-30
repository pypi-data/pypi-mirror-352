"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16diffraction-data.proto"\xad\x02\n\x1eDetectedDiffractionPerLocation\x12\n\n\x02id\x18\x01 \x01(\t\x12F\n\x05peaks\x18\x02 \x03(\x0b27.DetectedDiffractionPerLocation.DetectedDiffractionPeak\x1a\xb6\x01\n\x17DetectedDiffractionPeak\x12\x13\n\x0bpeakChannel\x18\x01 \x01(\x05\x12\x12\n\neffectSize\x18\x02 \x01(\x02\x12\x19\n\x11baselineVariation\x18\x03 \x01(\x02\x12\x18\n\x10globalDifference\x18\x04 \x01(\x02\x12\x17\n\x0fdifferenceSigma\x18\x05 \x01(\x02\x12\x12\n\npeakHeight\x18\x06 \x01(\x02\x12\x10\n\x08detector\x18\x07 \x01(\t"\x82\x01\n\x15ManualDiffractionPeak\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06scanId\x18\x02 \x01(\t\x12\x0b\n\x03pmc\x18\x03 \x01(\x05\x12\x11\n\tenergykeV\x18\x04 \x01(\x02\x12\x16\n\x0ecreatedUnixSec\x18\x05 \x01(\r\x12\x15\n\rcreatorUserId\x18\x06 \x01(\t"\xaa\x02\n\x1fDetectedDiffractionPeakStatuses\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06scanId\x18\x02 \x01(\t\x12@\n\x08statuses\x18\x03 \x03(\x0b2..DetectedDiffractionPeakStatuses.StatusesEntry\x1aK\n\nPeakStatus\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x16\n\x0ecreatedUnixSec\x18\x02 \x01(\r\x12\x15\n\rcreatorUserId\x18\x03 \x01(\t\x1a\\\n\rStatusesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12:\n\x05value\x18\x02 \x01(\x0b2+.DetectedDiffractionPeakStatuses.PeakStatus:\x028\x01"\xbb\x01\n\x15ClientDiffractionPeak\x12\n\n\x02id\x18\x01 \x01(\x05\x12E\n\x04peak\x18\x02 \x01(\x0b27.DetectedDiffractionPerLocation.DetectedDiffractionPeak\x12\x11\n\tenergykeV\x18\x03 \x01(\x02\x12\x16\n\x0estartEnergykeV\x18\x04 \x01(\x02\x12\x14\n\x0cendEnergykeV\x18\x05 \x01(\x02\x12\x0e\n\x06status\x18\x06 \x01(\t"\x18\n\x16ClientDiffractionPeaks"L\n\x13ClientRoughnessItem\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x18\n\x10GlobalDifference\x18\x02 \x01(\x02\x12\x0f\n\x07Deleted\x18\x03 \x01(\x08"i\n\x15ClientDiffractionData\x12%\n\x05peaks\x18\x01 \x03(\x0b2\x16.ClientDiffractionPeak\x12)\n\x0broughnesses\x18\x02 \x03(\x0b2\x14.ClientRoughnessItemB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'diffraction_data_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_DETECTEDDIFFRACTIONPEAKSTATUSES_STATUSESENTRY']._options = None
    _globals['_DETECTEDDIFFRACTIONPEAKSTATUSES_STATUSESENTRY']._serialized_options = b'8\x01'
    _globals['_DETECTEDDIFFRACTIONPERLOCATION']._serialized_start = 27
    _globals['_DETECTEDDIFFRACTIONPERLOCATION']._serialized_end = 328
    _globals['_DETECTEDDIFFRACTIONPERLOCATION_DETECTEDDIFFRACTIONPEAK']._serialized_start = 146
    _globals['_DETECTEDDIFFRACTIONPERLOCATION_DETECTEDDIFFRACTIONPEAK']._serialized_end = 328
    _globals['_MANUALDIFFRACTIONPEAK']._serialized_start = 331
    _globals['_MANUALDIFFRACTIONPEAK']._serialized_end = 461
    _globals['_DETECTEDDIFFRACTIONPEAKSTATUSES']._serialized_start = 464
    _globals['_DETECTEDDIFFRACTIONPEAKSTATUSES']._serialized_end = 762
    _globals['_DETECTEDDIFFRACTIONPEAKSTATUSES_PEAKSTATUS']._serialized_start = 593
    _globals['_DETECTEDDIFFRACTIONPEAKSTATUSES_PEAKSTATUS']._serialized_end = 668
    _globals['_DETECTEDDIFFRACTIONPEAKSTATUSES_STATUSESENTRY']._serialized_start = 670
    _globals['_DETECTEDDIFFRACTIONPEAKSTATUSES_STATUSESENTRY']._serialized_end = 762
    _globals['_CLIENTDIFFRACTIONPEAK']._serialized_start = 765
    _globals['_CLIENTDIFFRACTIONPEAK']._serialized_end = 952
    _globals['_CLIENTDIFFRACTIONPEAKS']._serialized_start = 954
    _globals['_CLIENTDIFFRACTIONPEAKS']._serialized_end = 978
    _globals['_CLIENTROUGHNESSITEM']._serialized_start = 980
    _globals['_CLIENTROUGHNESSITEM']._serialized_end = 1056
    _globals['_CLIENTDIFFRACTIONDATA']._serialized_start = 1058
    _globals['_CLIENTDIFFRACTIONDATA']._serialized_end = 1163