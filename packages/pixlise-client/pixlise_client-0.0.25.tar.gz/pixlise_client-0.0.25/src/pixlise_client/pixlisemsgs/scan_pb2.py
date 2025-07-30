"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import ownership_access_pb2 as ownership__access__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nscan.proto\x1a\x16ownership-access.proto"\xc8\x04\n\x08ScanItem\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x13\n\x0bdescription\x18\x03 \x01(\t\x12*\n\tdataTypes\x18\x04 \x03(\x0b2\x17.ScanItem.ScanTypeCount\x12#\n\ninstrument\x18\x05 \x01(\x0e2\x0f.ScanInstrument\x12\x18\n\x10instrumentConfig\x18\x06 \x01(\t\x12\x18\n\x10timestampUnixSec\x18\x07 \x01(\r\x12!\n\x04meta\x18\x08 \x03(\x0b2\x13.ScanItem.MetaEntry\x123\n\rcontentCounts\x18\t \x03(\x0b2\x1c.ScanItem.ContentCountsEntry\x12\x15\n\rcreatorUserId\x18\n \x01(\t\x12 \n\x05owner\x18\x0b \x01(\x0b2\x11.OwnershipSummary\x12\x0c\n\x04tags\x18\x0c \x03(\t\x12"\n\x1apreviousImportTimesUnixSec\x18\r \x03(\r\x12 \n\x18completeTimeStampUnixSec\x18\x0e \x01(\r\x1a?\n\rScanTypeCount\x12\x1f\n\x08dataType\x18\x01 \x01(\x0e2\r.ScanDataType\x12\r\n\x05count\x18\x02 \x01(\r\x1a+\n\tMetaEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x028\x01\x1a4\n\x12ContentCountsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x05:\x028\x01"Q\n\x10ScanMetaDataItem\x12\x10\n\x06fvalue\x18\x01 \x01(\x02H\x00\x12\x10\n\x06ivalue\x18\x02 \x01(\x05H\x00\x12\x10\n\x06svalue\x18\x03 \x01(\tH\x00B\x07\n\x05Value"!\n\x0eScanEntryRange\x12\x0f\n\x07indexes\x18\x01 \x03(\x05"b\n\x12ScanAutoShareEntry\x12\n\n\x02id\x18\x01 \x01(\t\x12\x1f\n\x07viewers\x18\x02 \x01(\x0b2\x0e.UserGroupList\x12\x1f\n\x07editors\x18\x03 \x01(\x0b2\x0e.UserGroupList"\x7f\n\x0eJobGroupConfig\x12\x12\n\njobGroupId\x18\x01 \x01(\t\x12\x13\n\x0bdockerImage\x18\x02 \x01(\t\x12\x11\n\tfastStart\x18\x03 \x01(\x08\x12\x11\n\tnodeCount\x18\x04 \x01(\x05\x12\x1e\n\nnodeConfig\x18\x05 \x01(\x0b2\n.JobConfig"J\n\x0bJobFilePath\x12\x14\n\x0cremoteBucket\x18\x01 \x01(\t\x12\x12\n\nremotePath\x18\x02 \x01(\t\x12\x11\n\tlocalPath\x18\x03 \x01(\t"\x81\x01\n\tJobConfig\x12\r\n\x05jobId\x18\x01 \x01(\t\x12#\n\rrequiredFiles\x18\x02 \x03(\x0b2\x0c.JobFilePath\x12\x0f\n\x07command\x18\x03 \x01(\t\x12\x0c\n\x04args\x18\x04 \x03(\t\x12!\n\x0boutputFiles\x18\x05 \x03(\x0b2\x0c.JobFilePath"\\\n\tClientMap\x12\x11\n\tEntryPMCs\x18\x01 \x03(\x05\x12\x13\n\x0bFloatValues\x18\x02 \x03(\x01\x12\x11\n\tIntValues\x18\x03 \x03(\x03\x12\x14\n\x0cStringValues\x18\x04 \x03(\t"#\n\x10ClientStringList\x12\x0f\n\x07Strings\x18\x01 \x03(\t*E\n\x0cScanDataType\x12\x0e\n\nSD_UNKNOWN\x10\x00\x12\x0c\n\x08SD_IMAGE\x10\x01\x12\n\n\x06SD_XRF\x10\x02\x12\x0b\n\x07SD_RGBU\x10\x03*v\n\x0eScanInstrument\x12\x16\n\x12UNKNOWN_INSTRUMENT\x10\x00\x12\x0b\n\x07PIXL_FM\x10\x01\x12\x0b\n\x07PIXL_EM\x10\x02\x12\x12\n\x0eJPL_BREADBOARD\x10\x03\x12\x12\n\x0eSBU_BREADBOARD\x10\x04\x12\n\n\x06BRUKER\x10\x05*;\n\x10ScanMetaDataType\x12\x0c\n\x08MT_FLOAT\x10\x00\x12\n\n\x06MT_INT\x10\x01\x12\r\n\tMT_STRING\x10\x02B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'scan_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SCANITEM_METAENTRY']._options = None
    _globals['_SCANITEM_METAENTRY']._serialized_options = b'8\x01'
    _globals['_SCANITEM_CONTENTCOUNTSENTRY']._options = None
    _globals['_SCANITEM_CONTENTCOUNTSENTRY']._serialized_options = b'8\x01'
    _globals['_SCANDATATYPE']._serialized_start = 1311
    _globals['_SCANDATATYPE']._serialized_end = 1380
    _globals['_SCANINSTRUMENT']._serialized_start = 1382
    _globals['_SCANINSTRUMENT']._serialized_end = 1500
    _globals['_SCANMETADATATYPE']._serialized_start = 1502
    _globals['_SCANMETADATATYPE']._serialized_end = 1561
    _globals['_SCANITEM']._serialized_start = 39
    _globals['_SCANITEM']._serialized_end = 623
    _globals['_SCANITEM_SCANTYPECOUNT']._serialized_start = 461
    _globals['_SCANITEM_SCANTYPECOUNT']._serialized_end = 524
    _globals['_SCANITEM_METAENTRY']._serialized_start = 526
    _globals['_SCANITEM_METAENTRY']._serialized_end = 569
    _globals['_SCANITEM_CONTENTCOUNTSENTRY']._serialized_start = 571
    _globals['_SCANITEM_CONTENTCOUNTSENTRY']._serialized_end = 623
    _globals['_SCANMETADATAITEM']._serialized_start = 625
    _globals['_SCANMETADATAITEM']._serialized_end = 706
    _globals['_SCANENTRYRANGE']._serialized_start = 708
    _globals['_SCANENTRYRANGE']._serialized_end = 741
    _globals['_SCANAUTOSHAREENTRY']._serialized_start = 743
    _globals['_SCANAUTOSHAREENTRY']._serialized_end = 841
    _globals['_JOBGROUPCONFIG']._serialized_start = 843
    _globals['_JOBGROUPCONFIG']._serialized_end = 970
    _globals['_JOBFILEPATH']._serialized_start = 972
    _globals['_JOBFILEPATH']._serialized_end = 1046
    _globals['_JOBCONFIG']._serialized_start = 1049
    _globals['_JOBCONFIG']._serialized_end = 1178
    _globals['_CLIENTMAP']._serialized_start = 1180
    _globals['_CLIENTMAP']._serialized_end = 1272
    _globals['_CLIENTSTRINGLIST']._serialized_start = 1274
    _globals['_CLIENTSTRINGLIST']._serialized_end = 1309