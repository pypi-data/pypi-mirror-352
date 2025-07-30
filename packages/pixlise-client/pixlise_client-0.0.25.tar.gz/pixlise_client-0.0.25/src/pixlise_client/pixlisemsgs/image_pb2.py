"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bimage.proto"\x87\x02\n\tScanImage\x12\x11\n\timagePath\x18\x01 \x01(\t\x12 \n\x06source\x18\x02 \x01(\x0e2\x10.ScanImageSource\x12\r\n\x05width\x18\x03 \x01(\r\x12\x0e\n\x06height\x18\x04 \x01(\r\x12\x10\n\x08fileSize\x18\x05 \x01(\r\x12"\n\x07purpose\x18\x06 \x01(\x0e2\x11.ScanImagePurpose\x12\x19\n\x11associatedScanIds\x18\x07 \x03(\t\x12\x14\n\x0coriginScanId\x18\x08 \x01(\t\x12\x16\n\x0eoriginImageURL\x18\t \x01(\t\x12\'\n\tmatchInfo\x18\n \x01(\x0b2\x14.ImageMatchTransform"r\n\x13ImageMatchTransform\x12\x19\n\x11beamImageFileName\x18\x01 \x01(\t\x12\x0f\n\x07xOffset\x18\x02 \x01(\x01\x12\x0f\n\x07yOffset\x18\x03 \x01(\x01\x12\x0e\n\x06xScale\x18\x04 \x01(\x01\x12\x0e\n\x06yScale\x18\x05 \x01(\x01"B\n\x12ScanImageDefaultDB\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12\x1c\n\x14defaultImageFileName\x18\x02 \x01(\t*C\n\x0fScanImageSource\x12\x0e\n\nSI_UNKNOWN\x10\x00\x12\x11\n\rSI_INSTRUMENT\x10\x01\x12\r\n\tSI_UPLOAD\x10\x02*J\n\x10ScanImagePurpose\x12\x0f\n\x0bSIP_UNKNOWN\x10\x00\x12\x0f\n\x0bSIP_VIEWING\x10\x01\x12\x14\n\x10SIP_MULTICHANNEL\x10\x02B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'image_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SCANIMAGESOURCE']._serialized_start = 465
    _globals['_SCANIMAGESOURCE']._serialized_end = 532
    _globals['_SCANIMAGEPURPOSE']._serialized_start = 534
    _globals['_SCANIMAGEPURPOSE']._serialized_end = 608
    _globals['_SCANIMAGE']._serialized_start = 16
    _globals['_SCANIMAGE']._serialized_end = 279
    _globals['_IMAGEMATCHTRANSFORM']._serialized_start = 281
    _globals['_IMAGEMATCHTRANSFORM']._serialized_end = 395
    _globals['_SCANIMAGEDEFAULTDB']._serialized_start = 397
    _globals['_SCANIMAGEDEFAULTDB']._serialized_end = 463