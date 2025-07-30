"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import scan_pb2 as scan__pb2
from . import job_pb2 as job__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fscan-msgs.proto\x1a\nscan.proto\x1a\tjob.proto"\xa2\x01\n\x0bScanListReq\x126\n\rsearchFilters\x18\x01 \x03(\x0b2\x1f.ScanListReq.SearchFiltersEntry\x1a4\n\x12SearchFiltersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x028\x01\x1a%\n\tMinMaxInt\x12\x0b\n\x03min\x18\x01 \x01(\x03\x12\x0b\n\x03max\x18\x02 \x01(\x03"(\n\x0cScanListResp\x12\x18\n\x05scans\x18\x01 \x03(\x0b2\t.ScanItem"\r\n\x0bScanListUpd"\x18\n\nScanGetReq\x12\n\n\x02id\x18\x01 \x01(\t"&\n\x0bScanGetResp\x12\x17\n\x04scan\x18\x01 \x01(\x0b2\t.ScanItem"@\n\rScanUploadReq\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06format\x18\x02 \x01(\t\x12\x13\n\x0bzipFileName\x18\x04 \x01(\t"\x1f\n\x0eScanUploadResp\x12\r\n\x05jobId\x18\x01 \x01(\t"+\n\rScanUploadUpd\x12\x1a\n\x06status\x18\x01 \x01(\x0b2\n.JobStatus"\x1e\n\x10ScanAutoShareReq\x12\n\n\x02id\x18\x01 \x01(\t"7\n\x11ScanAutoShareResp\x12"\n\x05entry\x18\x01 \x01(\x0b2\x13.ScanAutoShareEntry";\n\x15ScanAutoShareWriteReq\x12"\n\x05entry\x18\x01 \x01(\x0b2\x13.ScanAutoShareEntry"\x18\n\x16ScanAutoShareWriteResp"T\n\x10ScanMetaWriteReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x13\n\x0bdescription\x18\x03 \x01(\t\x12\x0c\n\x04tags\x18\x05 \x03(\t"\x13\n\x11ScanMetaWriteResp"(\n\x16ScanTriggerReImportReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t"(\n\x17ScanTriggerReImportResp\x12\r\n\x05jobId\x18\x01 \x01(\t"4\n\x16ScanTriggerReImportUpd\x12\x1a\n\x06status\x18\x01 \x01(\x0b2\n.JobStatus"+\n\x19ScanMetaLabelsAndTypesReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t"V\n\x1aScanMetaLabelsAndTypesResp\x12\x12\n\nmetaLabels\x18\x01 \x03(\t\x12$\n\tmetaTypes\x18\x02 \x03(\x0e2\x11.ScanMetaDataType"@\n\rScanDeleteReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12\x1f\n\x17scanNameForVerification\x18\x02 \x01(\t"\x10\n\x0eScanDeleteResp"2\n\x11ScanTriggerJobReq\x12\x0e\n\x06scanId\x18\x01 \x01(\t\x12\r\n\x05jobId\x18\x02 \x01(\t"\x14\n\x12ScanTriggerJobResp"\x11\n\x0fScanListJobsReq"1\n\x10ScanListJobsResp\x12\x1d\n\x04jobs\x18\x01 \x03(\x0b2\x0f.JobGroupConfig"/\n\x0fScanWriteJobReq\x12\x1c\n\x03job\x18\x03 \x01(\x0b2\x0f.JobGroupConfig"\x12\n\x10ScanWriteJobRespB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'scan_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SCANLISTREQ_SEARCHFILTERSENTRY']._options = None
    _globals['_SCANLISTREQ_SEARCHFILTERSENTRY']._serialized_options = b'8\x01'
    _globals['_SCANLISTREQ']._serialized_start = 43
    _globals['_SCANLISTREQ']._serialized_end = 205
    _globals['_SCANLISTREQ_SEARCHFILTERSENTRY']._serialized_start = 114
    _globals['_SCANLISTREQ_SEARCHFILTERSENTRY']._serialized_end = 166
    _globals['_SCANLISTREQ_MINMAXINT']._serialized_start = 168
    _globals['_SCANLISTREQ_MINMAXINT']._serialized_end = 205
    _globals['_SCANLISTRESP']._serialized_start = 207
    _globals['_SCANLISTRESP']._serialized_end = 247
    _globals['_SCANLISTUPD']._serialized_start = 249
    _globals['_SCANLISTUPD']._serialized_end = 262
    _globals['_SCANGETREQ']._serialized_start = 264
    _globals['_SCANGETREQ']._serialized_end = 288
    _globals['_SCANGETRESP']._serialized_start = 290
    _globals['_SCANGETRESP']._serialized_end = 328
    _globals['_SCANUPLOADREQ']._serialized_start = 330
    _globals['_SCANUPLOADREQ']._serialized_end = 394
    _globals['_SCANUPLOADRESP']._serialized_start = 396
    _globals['_SCANUPLOADRESP']._serialized_end = 427
    _globals['_SCANUPLOADUPD']._serialized_start = 429
    _globals['_SCANUPLOADUPD']._serialized_end = 472
    _globals['_SCANAUTOSHAREREQ']._serialized_start = 474
    _globals['_SCANAUTOSHAREREQ']._serialized_end = 504
    _globals['_SCANAUTOSHARERESP']._serialized_start = 506
    _globals['_SCANAUTOSHARERESP']._serialized_end = 561
    _globals['_SCANAUTOSHAREWRITEREQ']._serialized_start = 563
    _globals['_SCANAUTOSHAREWRITEREQ']._serialized_end = 622
    _globals['_SCANAUTOSHAREWRITERESP']._serialized_start = 624
    _globals['_SCANAUTOSHAREWRITERESP']._serialized_end = 648
    _globals['_SCANMETAWRITEREQ']._serialized_start = 650
    _globals['_SCANMETAWRITEREQ']._serialized_end = 734
    _globals['_SCANMETAWRITERESP']._serialized_start = 736
    _globals['_SCANMETAWRITERESP']._serialized_end = 755
    _globals['_SCANTRIGGERREIMPORTREQ']._serialized_start = 757
    _globals['_SCANTRIGGERREIMPORTREQ']._serialized_end = 797
    _globals['_SCANTRIGGERREIMPORTRESP']._serialized_start = 799
    _globals['_SCANTRIGGERREIMPORTRESP']._serialized_end = 839
    _globals['_SCANTRIGGERREIMPORTUPD']._serialized_start = 841
    _globals['_SCANTRIGGERREIMPORTUPD']._serialized_end = 893
    _globals['_SCANMETALABELSANDTYPESREQ']._serialized_start = 895
    _globals['_SCANMETALABELSANDTYPESREQ']._serialized_end = 938
    _globals['_SCANMETALABELSANDTYPESRESP']._serialized_start = 940
    _globals['_SCANMETALABELSANDTYPESRESP']._serialized_end = 1026
    _globals['_SCANDELETEREQ']._serialized_start = 1028
    _globals['_SCANDELETEREQ']._serialized_end = 1092
    _globals['_SCANDELETERESP']._serialized_start = 1094
    _globals['_SCANDELETERESP']._serialized_end = 1110
    _globals['_SCANTRIGGERJOBREQ']._serialized_start = 1112
    _globals['_SCANTRIGGERJOBREQ']._serialized_end = 1162
    _globals['_SCANTRIGGERJOBRESP']._serialized_start = 1164
    _globals['_SCANTRIGGERJOBRESP']._serialized_end = 1184
    _globals['_SCANLISTJOBSREQ']._serialized_start = 1186
    _globals['_SCANLISTJOBSREQ']._serialized_end = 1203
    _globals['_SCANLISTJOBSRESP']._serialized_start = 1205
    _globals['_SCANLISTJOBSRESP']._serialized_end = 1254
    _globals['_SCANWRITEJOBREQ']._serialized_start = 1256
    _globals['_SCANWRITEJOBREQ']._serialized_end = 1303
    _globals['_SCANWRITEJOBRESP']._serialized_start = 1305
    _globals['_SCANWRITEJOBRESP']._serialized_end = 1323