"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import pseudo_intensities_pb2 as pseudo__intensities__pb2
from . import scan_pb2 as scan__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dpseudo-intensities-msgs.proto\x1a\x18pseudo-intensities.proto\x1a\nscan.proto"F\n\x12PseudoIntensityReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12 \n\x07entries\x18\x02 \x01(\x0b2\x0f.ScanEntryRange"R\n\x13PseudoIntensityResp\x12\x17\n\x0fintensityLabels\x18\x01 \x03(\t\x12"\n\x04data\x18\x02 \x03(\x0b2\x14.PseudoIntensityDataB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'pseudo_intensities_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_PSEUDOINTENSITYREQ']._serialized_start = 71
    _globals['_PSEUDOINTENSITYREQ']._serialized_end = 141
    _globals['_PSEUDOINTENSITYRESP']._serialized_start = 143
    _globals['_PSEUDOINTENSITYRESP']._serialized_end = 225