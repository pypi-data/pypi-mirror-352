"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import spectrum_pb2 as spectrum__pb2
from . import scan_pb2 as scan__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13spectrum-msgs.proto\x1a\x0espectrum.proto\x1a\nscan.proto"b\n\x0bSpectrumReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12 \n\x07entries\x18\x02 \x01(\x0b2\x0f.ScanEntryRange\x12\x0f\n\x07bulkSum\x18\x03 \x01(\x08\x12\x10\n\x08maxValue\x18\x04 \x01(\x08"\xf9\x01\n\x0cSpectrumResp\x12$\n\x12spectraPerLocation\x18\x01 \x03(\x0b2\x08.Spectra\x12\x1e\n\x0bbulkSpectra\x18\x02 \x03(\x0b2\t.Spectrum\x12\x1d\n\nmaxSpectra\x18\x03 \x03(\x0b2\t.Spectrum\x12\x14\n\x0cchannelCount\x18\x04 \x01(\r\x12\x1c\n\x14normalSpectraForScan\x18\x05 \x01(\r\x12\x1b\n\x13dwellSpectraForScan\x18\x06 \x01(\r\x12\x19\n\x11liveTimeMetaIndex\x18\x07 \x01(\r\x12\x18\n\x10timeStampUnixSec\x18\x08 \x01(\rB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'spectrum_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SPECTRUMREQ']._serialized_start = 51
    _globals['_SPECTRUMREQ']._serialized_end = 149
    _globals['_SPECTRUMRESP']._serialized_start = 152
    _globals['_SPECTRUMRESP']._serialized_end = 401