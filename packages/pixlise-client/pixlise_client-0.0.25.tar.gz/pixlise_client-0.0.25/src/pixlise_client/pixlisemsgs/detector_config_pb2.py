"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15detector-config.proto"\xfb\x01\n\x0eDetectorConfig\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\nminElement\x18\x02 \x01(\x05\x12\x12\n\nmaxElement\x18\x03 \x01(\x05\x12\x17\n\x0fxrfeVLowerBound\x18\x04 \x01(\x05\x12\x17\n\x0fxrfeVUpperBound\x18\x05 \x01(\x05\x12\x17\n\x0fxrfeVResolution\x18\x06 \x01(\x05\x12\x15\n\rwindowElement\x18\x07 \x01(\x05\x12\x13\n\x0btubeElement\x18\x08 \x01(\x05\x12\x15\n\rdefaultParams\x18\t \x01(\t\x12\x14\n\x0cmmBeamRadius\x18\n \x01(\x02\x12\x11\n\televAngle\x18\x0b \x01(\x02B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'detector_config_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_DETECTORCONFIG']._serialized_start = 26
    _globals['_DETECTORCONFIG']._serialized_end = 277