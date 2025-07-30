"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11image-coreg.proto"?\n\x07MVPoint\x12\x0c\n\x04Line\x18\x01 \x01(\x02\x12\x0e\n\x06Sample\x18\x02 \x01(\x02\x12\x16\n\x0eSpectrumNumber\x18\x03 \x01(\x05"\xc1\x01\n\rMVObservation\x12\x14\n\x0cInterpolated\x18\x01 \x01(\x08\x12\x1e\n\x16ObservationCSVFilename\x18\x02 \x01(\t\x12\x17\n\x0fContextImageUrl\x18\x03 \x01(\t\x12\x0c\n\x04Site\x18\x04 \x01(\x05\x12\r\n\x05Drive\x18\x05 \x01(\x05\x12 \n\x0eOriginalPoints\x18\x06 \x03(\x0b2\x08.MVPoint\x12"\n\x10TranslatedPoints\x18\x07 \x03(\x0b2\x08.MVPoint"\\\n\x14MVWarpedOverlayImage\x12\x14\n\x0cInterpolated\x18\x01 \x01(\x08\x12\x16\n\x0eMappedImageUrl\x18\x02 \x01(\t\x12\x16\n\x0eWarpedImageUrl\x18\x03 \x01(\t"\x9a\x01\n\x10MarsViewerExport\x12$\n\x0cObservations\x18\x01 \x03(\x0b2\x0e.MVObservation\x12\x14\n\x0cBaseImageUrl\x18\x02 \x01(\t\x122\n\x13WarpedOverlayImages\x18\x03 \x03(\x0b2\x15.MVWarpedOverlayImage\x12\x16\n\x0eMarsviewerLink\x18\x04 \x01(\tB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'image_coreg_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_MVPOINT']._serialized_start = 21
    _globals['_MVPOINT']._serialized_end = 84
    _globals['_MVOBSERVATION']._serialized_start = 87
    _globals['_MVOBSERVATION']._serialized_end = 280
    _globals['_MVWARPEDOVERLAYIMAGE']._serialized_start = 282
    _globals['_MVWARPEDOVERLAYIMAGE']._serialized_end = 374
    _globals['_MARSVIEWEREXPORT']._serialized_start = 377
    _globals['_MARSVIEWEREXPORT']._serialized_end = 531