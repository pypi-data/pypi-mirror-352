"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import scan_beam_location_pb2 as scan__beam__location__pb2
from . import scan_pb2 as scan__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dscan-beam-location-msgs.proto\x1a\x18scan-beam-location.proto\x1a\nscan.proto"H\n\x14ScanBeamLocationsReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12 \n\x07entries\x18\x02 \x01(\x0b2\x0f.ScanEntryRange"=\n\x15ScanBeamLocationsResp\x12$\n\rbeamLocations\x18\x01 \x03(\x0b2\r.Coordinate3D"D\n\x12ClientBeamLocation\x12\x0b\n\x03PMC\x18\x01 \x01(\x05\x12!\n\ncoordinate\x18\x02 \x01(\x0b2\r.Coordinate3D"=\n\x13ClientBeamLocations\x12&\n\tlocations\x18\x01 \x03(\x0b2\x13.ClientBeamLocationB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'scan_beam_location_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SCANBEAMLOCATIONSREQ']._serialized_start = 71
    _globals['_SCANBEAMLOCATIONSREQ']._serialized_end = 143
    _globals['_SCANBEAMLOCATIONSRESP']._serialized_start = 145
    _globals['_SCANBEAMLOCATIONSRESP']._serialized_end = 206
    _globals['_CLIENTBEAMLOCATION']._serialized_start = 208
    _globals['_CLIENTBEAMLOCATION']._serialized_end = 276
    _globals['_CLIENTBEAMLOCATIONS']._serialized_start = 278
    _globals['_CLIENTBEAMLOCATIONS']._serialized_end = 339