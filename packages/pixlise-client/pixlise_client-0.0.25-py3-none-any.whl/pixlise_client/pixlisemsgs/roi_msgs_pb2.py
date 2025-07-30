"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import roi_pb2 as roi__pb2
from . import search_params_pb2 as search__params__pb2
from . import ownership_access_pb2 as ownership__access__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eroi-msgs.proto\x1a\troi.proto\x1a\x13search-params.proto\x1a\x16ownership-access.proto"N\n\x17RegionOfInterestListReq\x12#\n\x0csearchParams\x18\x01 \x01(\x0b2\r.SearchParams\x12\x0e\n\x06isMIST\x18\x02 \x01(\x08"\xc2\x01\n\x18RegionOfInterestListResp\x12K\n\x11regionsOfInterest\x18\x01 \x03(\x0b20.RegionOfInterestListResp.RegionsOfInterestEntry\x12\x0e\n\x06isMIST\x18\x02 \x01(\x08\x1aI\n\x16RegionsOfInterestEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1e\n\x05value\x18\x02 \x01(\x0b2\x0f.ROIItemSummary:\x028\x01"4\n\x16RegionOfInterestGetReq\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06isMIST\x18\x02 \x01(\x08"=\n\x17RegionOfInterestGetResp\x12"\n\x10regionOfInterest\x18\x01 \x01(\x0b2\x08.ROIItem"N\n\x18RegionOfInterestWriteReq\x12"\n\x10regionOfInterest\x18\x01 \x01(\x0b2\x08.ROIItem\x12\x0e\n\x06isMIST\x18\x02 \x01(\x08"?\n\x19RegionOfInterestWriteResp\x12"\n\x10regionOfInterest\x18\x01 \x01(\x0b2\x08.ROIItem"g\n\'RegionOfInterestDisplaySettingsWriteReq\x12\n\n\x02id\x18\x01 \x01(\t\x120\n\x0fdisplaySettings\x18\x02 \x01(\x0b2\x17.ROIItemDisplaySettings"\\\n(RegionOfInterestDisplaySettingsWriteResp\x120\n\x0fdisplaySettings\x18\x01 \x01(\x0b2\x17.ROIItemDisplaySettings"3\n%RegionOfInterestDisplaySettingsGetReq\x12\n\n\x02id\x18\x01 \x01(\t"Z\n&RegionOfInterestDisplaySettingsGetResp\x120\n\x0fdisplaySettings\x18\x01 \x01(\x0b2\x17.ROIItemDisplaySettings"\xe0\x01\n\x1cRegionOfInterestBulkWriteReq\x12#\n\x11regionsOfInterest\x18\x01 \x03(\x0b2\x08.ROIItem\x12\x11\n\toverwrite\x18\x02 \x01(\x08\x12\x16\n\x0eskipDuplicates\x18\x03 \x01(\x08\x12\x0e\n\x06isMIST\x18\x04 \x01(\x08\x12\x1e\n\x16mistROIScanIdsToDelete\x18\x05 \x03(\t\x12\x1f\n\x07editors\x18\x06 \x01(\x0b2\x0e.UserGroupList\x12\x1f\n\x07viewers\x18\x07 \x01(\x0b2\x0e.UserGroupList"D\n\x1dRegionOfInterestBulkWriteResp\x12#\n\x11regionsOfInterest\x18\x01 \x03(\x0b2\x08.ROIItem"7\n\x19RegionOfInterestDeleteReq\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06isMIST\x18\x02 \x01(\x08"\x1c\n\x1aRegionOfInterestDeleteResp"?\n RegionOfInterestBulkDuplicateReq\x12\x0b\n\x03ids\x18\x01 \x03(\t\x12\x0e\n\x06isMIST\x18\x02 \x01(\x08"\xc4\x01\n!RegionOfInterestBulkDuplicateResp\x12T\n\x11regionsOfInterest\x18\x01 \x03(\x0b29.RegionOfInterestBulkDuplicateResp.RegionsOfInterestEntry\x1aI\n\x16RegionsOfInterestEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1e\n\x05value\x18\x02 \x01(\x0b2\x0f.ROIItemSummary:\x028\x01B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'roi_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_REGIONOFINTERESTLISTRESP_REGIONSOFINTERESTENTRY']._options = None
    _globals['_REGIONOFINTERESTLISTRESP_REGIONSOFINTERESTENTRY']._serialized_options = b'8\x01'
    _globals['_REGIONOFINTERESTBULKDUPLICATERESP_REGIONSOFINTERESTENTRY']._options = None
    _globals['_REGIONOFINTERESTBULKDUPLICATERESP_REGIONSOFINTERESTENTRY']._serialized_options = b'8\x01'
    _globals['_REGIONOFINTERESTLISTREQ']._serialized_start = 74
    _globals['_REGIONOFINTERESTLISTREQ']._serialized_end = 152
    _globals['_REGIONOFINTERESTLISTRESP']._serialized_start = 155
    _globals['_REGIONOFINTERESTLISTRESP']._serialized_end = 349
    _globals['_REGIONOFINTERESTLISTRESP_REGIONSOFINTERESTENTRY']._serialized_start = 276
    _globals['_REGIONOFINTERESTLISTRESP_REGIONSOFINTERESTENTRY']._serialized_end = 349
    _globals['_REGIONOFINTERESTGETREQ']._serialized_start = 351
    _globals['_REGIONOFINTERESTGETREQ']._serialized_end = 403
    _globals['_REGIONOFINTERESTGETRESP']._serialized_start = 405
    _globals['_REGIONOFINTERESTGETRESP']._serialized_end = 466
    _globals['_REGIONOFINTERESTWRITEREQ']._serialized_start = 468
    _globals['_REGIONOFINTERESTWRITEREQ']._serialized_end = 546
    _globals['_REGIONOFINTERESTWRITERESP']._serialized_start = 548
    _globals['_REGIONOFINTERESTWRITERESP']._serialized_end = 611
    _globals['_REGIONOFINTERESTDISPLAYSETTINGSWRITEREQ']._serialized_start = 613
    _globals['_REGIONOFINTERESTDISPLAYSETTINGSWRITEREQ']._serialized_end = 716
    _globals['_REGIONOFINTERESTDISPLAYSETTINGSWRITERESP']._serialized_start = 718
    _globals['_REGIONOFINTERESTDISPLAYSETTINGSWRITERESP']._serialized_end = 810
    _globals['_REGIONOFINTERESTDISPLAYSETTINGSGETREQ']._serialized_start = 812
    _globals['_REGIONOFINTERESTDISPLAYSETTINGSGETREQ']._serialized_end = 863
    _globals['_REGIONOFINTERESTDISPLAYSETTINGSGETRESP']._serialized_start = 865
    _globals['_REGIONOFINTERESTDISPLAYSETTINGSGETRESP']._serialized_end = 955
    _globals['_REGIONOFINTERESTBULKWRITEREQ']._serialized_start = 958
    _globals['_REGIONOFINTERESTBULKWRITEREQ']._serialized_end = 1182
    _globals['_REGIONOFINTERESTBULKWRITERESP']._serialized_start = 1184
    _globals['_REGIONOFINTERESTBULKWRITERESP']._serialized_end = 1252
    _globals['_REGIONOFINTERESTDELETEREQ']._serialized_start = 1254
    _globals['_REGIONOFINTERESTDELETEREQ']._serialized_end = 1309
    _globals['_REGIONOFINTERESTDELETERESP']._serialized_start = 1311
    _globals['_REGIONOFINTERESTDELETERESP']._serialized_end = 1339
    _globals['_REGIONOFINTERESTBULKDUPLICATEREQ']._serialized_start = 1341
    _globals['_REGIONOFINTERESTBULKDUPLICATEREQ']._serialized_end = 1404
    _globals['_REGIONOFINTERESTBULKDUPLICATERESP']._serialized_start = 1407
    _globals['_REGIONOFINTERESTBULKDUPLICATERESP']._serialized_end = 1603
    _globals['_REGIONOFINTERESTBULKDUPLICATERESP_REGIONSOFINTERESTENTRY']._serialized_start = 276
    _globals['_REGIONOFINTERESTBULKDUPLICATERESP_REGIONSOFINTERESTENTRY']._serialized_end = 349