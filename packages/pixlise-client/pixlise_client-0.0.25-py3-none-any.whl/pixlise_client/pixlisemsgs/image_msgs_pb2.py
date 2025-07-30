"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import image_pb2 as image__pb2
from . import image_beam_location_pb2 as image__beam__location__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10image-msgs.proto\x1a\x0bimage.proto\x1a\x19image-beam-location.proto"7\n\x0cImageListReq\x12\x0f\n\x07scanIds\x18\x01 \x03(\t\x12\x16\n\x0emustIncludeAll\x18\x02 \x01(\x08"+\n\rImageListResp\x12\x1a\n\x06images\x18\x01 \x03(\x0b2\n.ScanImage";\n\x0cImageListUpd\x12\x18\n\x10associatedScanId\x18\x01 \x01(\t\x12\x11\n\timageName\x18\x02 \x01(\t" \n\x0bImageGetReq\x12\x11\n\timageName\x18\x01 \x01(\t")\n\x0cImageGetResp\x12\x19\n\x05image\x18\x01 \x01(\x0b2\n.ScanImage"%\n\x12ImageGetDefaultReq\x12\x0f\n\x07scanIds\x18\x01 \x03(\t"\xa6\x01\n\x13ImageGetDefaultResp\x12P\n\x16defaultImagesPerScanId\x18\x01 \x03(\x0b20.ImageGetDefaultResp.DefaultImagesPerScanIdEntry\x1a=\n\x1bDefaultImagesPerScanIdEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x028\x01"B\n\x12ImageSetDefaultReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12\x1c\n\x14defaultImageFileName\x18\x02 \x01(\t"\x15\n\x13ImageSetDefaultResp"\xd3\x01\n\x16ImageUploadHttpRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\timageData\x18\x02 \x01(\x0c\x12\x19\n\x11associatedScanIds\x18\x05 \x03(\t\x12\x14\n\x0coriginScanId\x18\x06 \x01(\t\x12*\n\x0flocationPerScan\x18\x03 \x01(\x0b2\x0f.ImageLocationsH\x00\x12,\n\x0cbeamImageRef\x18\x04 \x01(\x0b2\x14.ImageMatchTransformH\x00B\r\n\x0bAssociation"\x1e\n\x0eImageDeleteReq\x12\x0c\n\x04name\x18\x01 \x01(\t"\x11\n\x0fImageDeleteResp"W\n\x19ImageSetMatchTransformReq\x12\x11\n\timageName\x18\x01 \x01(\t\x12\'\n\ttransform\x18\x02 \x01(\x0b2\x14.ImageMatchTransform"\x1c\n\x1aImageSetMatchTransformRespB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'image_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_IMAGEGETDEFAULTRESP_DEFAULTIMAGESPERSCANIDENTRY']._options = None
    _globals['_IMAGEGETDEFAULTRESP_DEFAULTIMAGESPERSCANIDENTRY']._serialized_options = b'8\x01'
    _globals['_IMAGELISTREQ']._serialized_start = 60
    _globals['_IMAGELISTREQ']._serialized_end = 115
    _globals['_IMAGELISTRESP']._serialized_start = 117
    _globals['_IMAGELISTRESP']._serialized_end = 160
    _globals['_IMAGELISTUPD']._serialized_start = 162
    _globals['_IMAGELISTUPD']._serialized_end = 221
    _globals['_IMAGEGETREQ']._serialized_start = 223
    _globals['_IMAGEGETREQ']._serialized_end = 255
    _globals['_IMAGEGETRESP']._serialized_start = 257
    _globals['_IMAGEGETRESP']._serialized_end = 298
    _globals['_IMAGEGETDEFAULTREQ']._serialized_start = 300
    _globals['_IMAGEGETDEFAULTREQ']._serialized_end = 337
    _globals['_IMAGEGETDEFAULTRESP']._serialized_start = 340
    _globals['_IMAGEGETDEFAULTRESP']._serialized_end = 506
    _globals['_IMAGEGETDEFAULTRESP_DEFAULTIMAGESPERSCANIDENTRY']._serialized_start = 445
    _globals['_IMAGEGETDEFAULTRESP_DEFAULTIMAGESPERSCANIDENTRY']._serialized_end = 506
    _globals['_IMAGESETDEFAULTREQ']._serialized_start = 508
    _globals['_IMAGESETDEFAULTREQ']._serialized_end = 574
    _globals['_IMAGESETDEFAULTRESP']._serialized_start = 576
    _globals['_IMAGESETDEFAULTRESP']._serialized_end = 597
    _globals['_IMAGEUPLOADHTTPREQUEST']._serialized_start = 600
    _globals['_IMAGEUPLOADHTTPREQUEST']._serialized_end = 811
    _globals['_IMAGEDELETEREQ']._serialized_start = 813
    _globals['_IMAGEDELETEREQ']._serialized_end = 843
    _globals['_IMAGEDELETERESP']._serialized_start = 845
    _globals['_IMAGEDELETERESP']._serialized_end = 862
    _globals['_IMAGESETMATCHTRANSFORMREQ']._serialized_start = 864
    _globals['_IMAGESETMATCHTRANSFORMREQ']._serialized_end = 951
    _globals['_IMAGESETMATCHTRANSFORMRESP']._serialized_start = 953
    _globals['_IMAGESETMATCHTRANSFORMRESP']._serialized_end = 981