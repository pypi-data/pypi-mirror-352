"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import image_beam_location_pb2 as image__beam__location__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1eimage-beam-location-msgs.proto\x1a\x19image-beam-location.proto"\xc6\x01\n\x15ImageBeamLocationsReq\x12\x11\n\timageName\x18\x01 \x01(\t\x12F\n\x10scanBeamVersions\x18\x04 \x03(\x0b2,.ImageBeamLocationsReq.ScanBeamVersionsEntry\x12\x19\n\x11generateForScanId\x18\x03 \x01(\t\x1a7\n\x15ScanBeamVersionsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\r:\x028\x01"<\n\x16ImageBeamLocationsResp\x12"\n\tlocations\x18\x01 \x01(\x0b2\x0f.ImageLocations"1\n\x1cImageBeamLocationVersionsReq\x12\x11\n\timageName\x18\x01 \x01(\t"\x87\x02\n\x1dImageBeamLocationVersionsResp\x12R\n\x12beamVersionPerScan\x18\x01 \x03(\x0b26.ImageBeamLocationVersionsResp.BeamVersionPerScanEntry\x1a%\n\x11AvailableVersions\x12\x10\n\x08versions\x18\x01 \x03(\r\x1ak\n\x17BeamVersionPerScanEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12?\n\x05value\x18\x02 \x01(\x0b20.ImageBeamLocationVersionsResp.AvailableVersions:\x028\x01"Y\n\x1aImageBeamLocationUploadReq\x12\x11\n\timageName\x18\x01 \x01(\t\x12(\n\x08location\x18\x02 \x01(\x0b2\x16.ImageLocationsForScan"\x1d\n\x1bImageBeamLocationUploadRespB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'image_beam_location_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_IMAGEBEAMLOCATIONSREQ_SCANBEAMVERSIONSENTRY']._options = None
    _globals['_IMAGEBEAMLOCATIONSREQ_SCANBEAMVERSIONSENTRY']._serialized_options = b'8\x01'
    _globals['_IMAGEBEAMLOCATIONVERSIONSRESP_BEAMVERSIONPERSCANENTRY']._options = None
    _globals['_IMAGEBEAMLOCATIONVERSIONSRESP_BEAMVERSIONPERSCANENTRY']._serialized_options = b'8\x01'
    _globals['_IMAGEBEAMLOCATIONSREQ']._serialized_start = 62
    _globals['_IMAGEBEAMLOCATIONSREQ']._serialized_end = 260
    _globals['_IMAGEBEAMLOCATIONSREQ_SCANBEAMVERSIONSENTRY']._serialized_start = 205
    _globals['_IMAGEBEAMLOCATIONSREQ_SCANBEAMVERSIONSENTRY']._serialized_end = 260
    _globals['_IMAGEBEAMLOCATIONSRESP']._serialized_start = 262
    _globals['_IMAGEBEAMLOCATIONSRESP']._serialized_end = 322
    _globals['_IMAGEBEAMLOCATIONVERSIONSREQ']._serialized_start = 324
    _globals['_IMAGEBEAMLOCATIONVERSIONSREQ']._serialized_end = 373
    _globals['_IMAGEBEAMLOCATIONVERSIONSRESP']._serialized_start = 376
    _globals['_IMAGEBEAMLOCATIONVERSIONSRESP']._serialized_end = 639
    _globals['_IMAGEBEAMLOCATIONVERSIONSRESP_AVAILABLEVERSIONS']._serialized_start = 493
    _globals['_IMAGEBEAMLOCATIONVERSIONSRESP_AVAILABLEVERSIONS']._serialized_end = 530
    _globals['_IMAGEBEAMLOCATIONVERSIONSRESP_BEAMVERSIONPERSCANENTRY']._serialized_start = 532
    _globals['_IMAGEBEAMLOCATIONVERSIONSRESP_BEAMVERSIONPERSCANENTRY']._serialized_end = 639
    _globals['_IMAGEBEAMLOCATIONUPLOADREQ']._serialized_start = 641
    _globals['_IMAGEBEAMLOCATIONUPLOADREQ']._serialized_end = 730
    _globals['_IMAGEBEAMLOCATIONUPLOADRESP']._serialized_start = 732
    _globals['_IMAGEBEAMLOCATIONUPLOADRESP']._serialized_end = 761