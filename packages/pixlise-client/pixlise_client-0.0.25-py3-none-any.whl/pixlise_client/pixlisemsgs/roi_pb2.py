"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import ownership_access_pb2 as ownership__access__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\troi.proto\x1a\x16ownership-access.proto"\x88\x02\n\x0bMistROIItem\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06scanId\x18\x02 \x01(\t\x12\x0f\n\x07species\x18\x03 \x01(\t\x12\x16\n\x0emineralGroupID\x18\x04 \x01(\t\x12\x0f\n\x07idDepth\x18\x05 \x01(\x05\x12\x1b\n\x13classificationTrail\x18\x06 \x01(\t\x12\x0f\n\x07formula\x18\x07 \x01(\t\x12<\n\x10pmcConfidenceMap\x18\x08 \x03(\x0b2".MistROIItem.PmcConfidenceMapEntry\x1a7\n\x15PmcConfidenceMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\x01:\x028\x01"C\n\x16ROIItemDisplaySettings\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05shape\x18\x02 \x01(\t\x12\x0e\n\x06colour\x18\x03 \x01(\t"\xc7\x02\n\x07ROIItem\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06scanId\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x13\n\x0bdescription\x18\x04 \x01(\t\x12\x1f\n\x17scanEntryIndexesEncoded\x18\x05 \x03(\x05\x12\x11\n\timageName\x18\x06 \x01(\t\x12\x1b\n\x13pixelIndexesEncoded\x18\x07 \x03(\x05\x12!\n\x0bmistROIItem\x18\x08 \x01(\x0b2\x0c.MistROIItem\x12\x0e\n\x06isMIST\x18\t \x01(\x08\x12\x0c\n\x04tags\x18\n \x03(\t\x12\x17\n\x0fmodifiedUnixSec\x18\x0b \x01(\r\x120\n\x0fdisplaySettings\x18\x0c \x01(\x0b2\x17.ROIItemDisplaySettings\x12 \n\x05owner\x18\r \x01(\x0b2\x11.OwnershipSummary"\x90\x02\n\x0eROIItemSummary\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06scanId\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x13\n\x0bdescription\x18\x04 \x01(\t\x12\x11\n\timageName\x18\x05 \x01(\t\x12\x0c\n\x04tags\x18\x06 \x03(\t\x12\x17\n\x0fmodifiedUnixSec\x18\x07 \x01(\r\x12!\n\x0bmistROIItem\x18\x08 \x01(\x0b2\x0c.MistROIItem\x12\x0e\n\x06isMIST\x18\t \x01(\x08\x120\n\x0fdisplaySettings\x18\n \x01(\x0b2\x17.ROIItemDisplaySettings\x12 \n\x05owner\x18\x0b \x01(\x0b2\x11.OwnershipSummaryB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'roi_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_MISTROIITEM_PMCCONFIDENCEMAPENTRY']._options = None
    _globals['_MISTROIITEM_PMCCONFIDENCEMAPENTRY']._serialized_options = b'8\x01'
    _globals['_MISTROIITEM']._serialized_start = 38
    _globals['_MISTROIITEM']._serialized_end = 302
    _globals['_MISTROIITEM_PMCCONFIDENCEMAPENTRY']._serialized_start = 247
    _globals['_MISTROIITEM_PMCCONFIDENCEMAPENTRY']._serialized_end = 302
    _globals['_ROIITEMDISPLAYSETTINGS']._serialized_start = 304
    _globals['_ROIITEMDISPLAYSETTINGS']._serialized_end = 371
    _globals['_ROIITEM']._serialized_start = 374
    _globals['_ROIITEM']._serialized_end = 701
    _globals['_ROIITEMSUMMARY']._serialized_start = 704
    _globals['_ROIITEMSUMMARY']._serialized_end = 976