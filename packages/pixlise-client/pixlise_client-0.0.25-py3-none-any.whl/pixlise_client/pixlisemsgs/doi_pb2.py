"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tdoi.proto"<\n\x14DOIRelatedIdentifier\x12\x12\n\nidentifier\x18\x01 \x01(\t\x12\x10\n\x08relation\x18\x02 \x01(\t">\n\nDOICreator\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0baffiliation\x18\x02 \x01(\t\x12\r\n\x05orcid\x18\x03 \x01(\t"P\n\x0eDOIContributor\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0baffiliation\x18\x02 \x01(\t\x12\r\n\x05orcid\x18\x03 \x01(\t\x12\x0c\n\x04type\x18\x04 \x01(\t"\xac\x02\n\x0bDOIMetadata\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x1d\n\x08creators\x18\x03 \x03(\x0b2\x0b.DOICreator\x12\x13\n\x0bdescription\x18\x04 \x01(\t\x12\x10\n\x08keywords\x18\x05 \x01(\t\x12\r\n\x05notes\x18\x06 \x01(\t\x121\n\x12relatedIdentifiers\x18\x07 \x03(\x0b2\x15.DOIRelatedIdentifier\x12%\n\x0ccontributors\x18\x08 \x03(\x0b2\x0f.DOIContributor\x12\x12\n\nreferences\x18\t \x01(\t\x12\x0f\n\x07version\x18\n \x01(\t\x12\x0b\n\x03doi\x18\x0b \x01(\t\x12\x10\n\x08doiBadge\x18\x0c \x01(\t\x12\x0f\n\x07doiLink\x18\r \x01(\t"0\n\x0eZenodoFileLink\x12\x10\n\x08download\x18\x01 \x01(\t\x12\x0c\n\x04self\x18\x02 \x01(\t"n\n\nZenodoFile\x12\x10\n\x08checksum\x18\x01 \x01(\t\x12\x10\n\x08filename\x18\x02 \x01(\t\x12\x10\n\x08filesize\x18\x03 \x01(\r\x12\n\n\x02id\x18\x04 \x01(\t\x12\x1e\n\x05links\x18\x05 \x01(\x0b2\x0f.ZenodoFileLink"\xab\x01\n\x0bZenodoLinks\x12\r\n\x05badge\x18\x01 \x01(\t\x12\x0e\n\x06bucket\x18\x02 \x01(\t\x12\x14\n\x0cconceptBadge\x18\x03 \x01(\t\x12\x12\n\nconceptDOI\x18\x04 \x01(\t\x12\x0b\n\x03doi\x18\x05 \x01(\t\x12\x0e\n\x06latest\x18\x06 \x01(\t\x12\x12\n\nlatestHTML\x18\x07 \x01(\t\x12\x0e\n\x06record\x18\x08 \x01(\t\x12\x12\n\nrecordHTML\x18\t \x01(\t"\xab\x01\n\x10ZenodoDraftLinks\x12\x0e\n\x06bucket\x18\x01 \x01(\t\x12\x0f\n\x07discard\x18\x02 \x01(\t\x12\x0c\n\x04edit\x18\x03 \x01(\t\x12\r\n\x05files\x18\x04 \x01(\t\x12\x0c\n\x04html\x18\x05 \x01(\t\x12\x13\n\x0blatestDraft\x18\x06 \x01(\t\x12\x17\n\x0flatestDraftHTML\x18\x07 \x01(\t\x12\x0f\n\x07publish\x18\x08 \x01(\t\x12\x0c\n\x04self\x18\t \x01(\t"%\n\x0fZenodoCommunity\x12\x12\n\nidentifier\x18\x01 \x01(\t"!\n\x11ZenodoNameCreator\x12\x0c\n\x04name\x18\x01 \x01(\t"A\n\x1cZenodoNameAffiliationCreator\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0baffiliation\x18\x02 \x01(\t"1\n\x13ZenodoPrereserveDOI\x12\x0b\n\x03doi\x18\x01 \x01(\t\x12\r\n\x05recid\x18\x02 \x01(\r"\x9d\x02\n\x1dZenodoPublishResponseMetadata\x12\x13\n\x0baccessRight\x18\x01 \x01(\t\x12%\n\x0bcommunities\x18\x02 \x03(\x0b2\x10.ZenodoCommunity\x12$\n\x08creators\x18\x03 \x03(\x0b2\x12.ZenodoNameCreator\x12\x13\n\x0bdescription\x18\x04 \x01(\t\x12\x0b\n\x03doi\x18\x05 \x01(\t\x12\x0f\n\x07license\x18\x06 \x01(\t\x12+\n\rprereserveDOI\x18\x07 \x01(\x0b2\x14.ZenodoPrereserveDOI\x12\x17\n\x0fpublicationDate\x18\x08 \x01(\t\x12\r\n\x05title\x18\t \x01(\t\x12\x12\n\nuploadType\x18\n \x01(\t"\xca\x02\n\x15ZenodoPublishResponse\x12\x12\n\nconceptDOI\x18\x01 \x01(\t\x12\x14\n\x0cconceptRecID\x18\x02 \x01(\t\x12\x0f\n\x07created\x18\x03 \x01(\t\x12\x0b\n\x03doi\x18\x04 \x01(\t\x12\x0e\n\x06doiURL\x18\x05 \x01(\t\x12\x1a\n\x05files\x18\x06 \x03(\x0b2\x0b.ZenodoFile\x12\n\n\x02id\x18\x07 \x01(\r\x12\x1b\n\x05links\x18\x08 \x01(\x0b2\x0c.ZenodoLinks\x120\n\x08metadata\x18\t \x01(\x0b2\x1e.ZenodoPublishResponseMetadata\x12\x10\n\x08modified\x18\n \x01(\t\x12\r\n\x05owner\x18\x0b \x01(\r\x12\x10\n\x08recordID\x18\x0c \x01(\r\x12\r\n\x05state\x18\r \x01(\t\x12\x11\n\tsubmitted\x18\x0e \x01(\x08\x12\r\n\x05title\x18\x0f \x01(\t"\xa3\x02\n\x18ZenodoDepositionMetadata\x12\x13\n\x0baccessRight\x18\x01 \x01(\t\x12%\n\x0bcommunities\x18\x02 \x03(\x0b2\x10.ZenodoCommunity\x12/\n\x08creators\x18\x03 \x03(\x0b2\x1d.ZenodoNameAffiliationCreator\x12\x13\n\x0bdescription\x18\x04 \x01(\t\x12\x0b\n\x03doi\x18\x05 \x01(\t\x12\x0f\n\x07license\x18\x06 \x01(\t\x12+\n\rprereserveDOI\x18\x07 \x01(\x0b2\x14.ZenodoPrereserveDOI\x12\x17\n\x0fpublicationDate\x18\x08 \x01(\t\x12\r\n\x05title\x18\t \x01(\t\x12\x12\n\nuploadType\x18\n \x01(\t"\xae\x02\n\x12ZenodoMetaResponse\x12\x14\n\x0cconceptRecID\x18\x01 \x01(\t\x12\x0f\n\x07created\x18\x02 \x01(\t\x12\x0b\n\x03doi\x18\x03 \x01(\t\x12\x0e\n\x06doiURL\x18\x04 \x01(\t\x12\x1a\n\x05files\x18\x05 \x03(\x0b2\x0b.ZenodoFile\x12\n\n\x02id\x18\x06 \x01(\r\x12\x1b\n\x05links\x18\x07 \x01(\x0b2\x0c.ZenodoLinks\x12+\n\x08metadata\x18\x08 \x01(\x0b2\x19.ZenodoDepositionMetadata\x12\x10\n\x08modified\x18\t \x01(\t\x12\r\n\x05owner\x18\n \x01(\r\x12\x10\n\x08recordID\x18\x0b \x01(\r\x12\r\n\x05state\x18\x0c \x01(\t\x12\x11\n\tsubmitted\x18\r \x01(\x08\x12\r\n\x05title\x18\x0e \x01(\t"\x85\x02\n\x18ZenodoDepositionResponse\x12\x14\n\x0cconceptRecID\x18\x01 \x01(\t\x12\x0f\n\x07created\x18\x02 \x01(\t\x12\x1a\n\x05files\x18\x03 \x03(\x0b2\x0b.ZenodoFile\x12\n\n\x02id\x18\x04 \x01(\r\x12 \n\x05links\x18\x05 \x01(\x0b2\x11.ZenodoDraftLinks\x12&\n\x08metadata\x18\x06 \x01(\x0b2\x14.ZenodoPrereserveDOI\x12\r\n\x05owner\x18\x07 \x01(\r\x12\x10\n\x08recordID\x18\x08 \x01(\r\x12\r\n\x05state\x18\t \x01(\t\x12\x11\n\tsubmitted\x18\n \x01(\x08\x12\r\n\x05title\x18\x0b \x01(\t"G\n\x15ZenodoFileUploadsLink\x12\x0c\n\x04self\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\x12\x0f\n\x07uploads\x18\x03 \x01(\t"\xdb\x01\n\x18ZenodoFileUploadResponse\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x10\n\x08mimetype\x18\x02 \x01(\t\x12\x10\n\x08checksum\x18\x03 \x01(\t\x12\x11\n\tversionID\x18\x04 \x01(\t\x12\x0c\n\x04size\x18\x05 \x01(\r\x12\x0f\n\x07created\x18\x06 \x01(\t\x12\x0f\n\x07updated\x18\x07 \x01(\t\x12%\n\x05links\x18\x08 \x01(\x0b2\x16.ZenodoFileUploadsLink\x12\x0e\n\x06isHead\x18\t \x01(\x08\x12\x14\n\x0cdeleteMarker\x18\n \x01(\x08B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'doi_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_DOIRELATEDIDENTIFIER']._serialized_start = 13
    _globals['_DOIRELATEDIDENTIFIER']._serialized_end = 73
    _globals['_DOICREATOR']._serialized_start = 75
    _globals['_DOICREATOR']._serialized_end = 137
    _globals['_DOICONTRIBUTOR']._serialized_start = 139
    _globals['_DOICONTRIBUTOR']._serialized_end = 219
    _globals['_DOIMETADATA']._serialized_start = 222
    _globals['_DOIMETADATA']._serialized_end = 522
    _globals['_ZENODOFILELINK']._serialized_start = 524
    _globals['_ZENODOFILELINK']._serialized_end = 572
    _globals['_ZENODOFILE']._serialized_start = 574
    _globals['_ZENODOFILE']._serialized_end = 684
    _globals['_ZENODOLINKS']._serialized_start = 687
    _globals['_ZENODOLINKS']._serialized_end = 858
    _globals['_ZENODODRAFTLINKS']._serialized_start = 861
    _globals['_ZENODODRAFTLINKS']._serialized_end = 1032
    _globals['_ZENODOCOMMUNITY']._serialized_start = 1034
    _globals['_ZENODOCOMMUNITY']._serialized_end = 1071
    _globals['_ZENODONAMECREATOR']._serialized_start = 1073
    _globals['_ZENODONAMECREATOR']._serialized_end = 1106
    _globals['_ZENODONAMEAFFILIATIONCREATOR']._serialized_start = 1108
    _globals['_ZENODONAMEAFFILIATIONCREATOR']._serialized_end = 1173
    _globals['_ZENODOPRERESERVEDOI']._serialized_start = 1175
    _globals['_ZENODOPRERESERVEDOI']._serialized_end = 1224
    _globals['_ZENODOPUBLISHRESPONSEMETADATA']._serialized_start = 1227
    _globals['_ZENODOPUBLISHRESPONSEMETADATA']._serialized_end = 1512
    _globals['_ZENODOPUBLISHRESPONSE']._serialized_start = 1515
    _globals['_ZENODOPUBLISHRESPONSE']._serialized_end = 1845
    _globals['_ZENODODEPOSITIONMETADATA']._serialized_start = 1848
    _globals['_ZENODODEPOSITIONMETADATA']._serialized_end = 2139
    _globals['_ZENODOMETARESPONSE']._serialized_start = 2142
    _globals['_ZENODOMETARESPONSE']._serialized_end = 2444
    _globals['_ZENODODEPOSITIONRESPONSE']._serialized_start = 2447
    _globals['_ZENODODEPOSITIONRESPONSE']._serialized_end = 2708
    _globals['_ZENODOFILEUPLOADSLINK']._serialized_start = 2710
    _globals['_ZENODOFILEUPLOADSLINK']._serialized_end = 2781
    _globals['_ZENODOFILEUPLOADRESPONSE']._serialized_start = 2784
    _globals['_ZENODOFILEUPLOADRESPONSE']._serialized_end = 3003