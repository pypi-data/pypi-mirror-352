"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import scan_pb2 as scan__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19image-beam-location.proto\x1a\nscan.proto"$\n\x0cCoordinate2D\x12\t\n\x01i\x18\x01 \x01(\x02\x12\t\n\x01j\x18\x02 \x01(\x02"\x83\x01\n\x15ImageLocationsForScan\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12\x13\n\x0bbeamVersion\x18\x03 \x01(\r\x12#\n\ninstrument\x18\x04 \x01(\x0e2\x0f.ScanInstrument\x12 \n\tlocations\x18\x02 \x03(\x0b2\r.Coordinate2D"T\n\x0eImageLocations\x12\x11\n\timageName\x18\x01 \x01(\t\x12/\n\x0flocationPerScan\x18\x02 \x03(\x0b2\x16.ImageLocationsForScanB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'image_beam_location_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_COORDINATE2D']._serialized_start = 41
    _globals['_COORDINATE2D']._serialized_end = 77
    _globals['_IMAGELOCATIONSFORSCAN']._serialized_start = 80
    _globals['_IMAGELOCATIONSFORSCAN']._serialized_end = 211
    _globals['_IMAGELOCATIONS']._serialized_start = 213
    _globals['_IMAGELOCATIONS']._serialized_end = 297