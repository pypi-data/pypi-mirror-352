"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import job_pb2 as job__pb2
from . import ownership_access_pb2 as ownership__access__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19quantification-meta.proto\x1a\tjob.proto\x1a\x16ownership-access.proto"\x8b\x02\n\x17QuantStartingParameters\x12&\n\nuserParams\x18\x01 \x01(\x0b2\x12.QuantCreateParams\x12\x10\n\x08pmcCount\x18\x02 \x01(\r\x12\x14\n\x0cscanFilePath\x18\x03 \x01(\t\x12\x12\n\ndataBucket\x18\x04 \x01(\t\x12\x19\n\x11piquantJobsBucket\x18\x05 \x01(\t\x12\x14\n\x0ccoresPerNode\x18\x06 \x01(\r\x12\x18\n\x10startUnixTimeSec\x18\x07 \x01(\r\x12\x17\n\x0frequestorUserId\x18\x08 \x01(\t\x12\x16\n\x0ePIQUANTVersion\x18\t \x01(\t\x12\x10\n\x08comments\x18\n \x01(\t"\xdc\x01\n\x11QuantCreateParams\x12\x0f\n\x07command\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0e\n\x06scanId\x18\x03 \x01(\t\x12\x0c\n\x04pmcs\x18\x04 \x03(\x05\x12\x10\n\x08elements\x18\x05 \x03(\t\x12\x16\n\x0edetectorConfig\x18\x06 \x01(\t\x12\x12\n\nparameters\x18\x07 \x01(\t\x12\x12\n\nrunTimeSec\x18\x08 \x01(\r\x12\x11\n\tquantMode\x18\t \x01(\t\x12\x0e\n\x06roiIDs\x18\n \x03(\t\x12\x15\n\rincludeDwells\x18\x0b \x01(\x08"\xad\x01\n\x15QuantificationSummary\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06scanId\x18\x05 \x01(\t\x12(\n\x06params\x18\x02 \x01(\x0b2\x18.QuantStartingParameters\x12\x10\n\x08elements\x18\x03 \x03(\t\x12\x1a\n\x06status\x18\x04 \x01(\x0b2\n.JobStatus\x12 \n\x05owner\x18\n \x01(\x0b2\x11.OwnershipSummaryB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'quantification_meta_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_QUANTSTARTINGPARAMETERS']._serialized_start = 65
    _globals['_QUANTSTARTINGPARAMETERS']._serialized_end = 332
    _globals['_QUANTCREATEPARAMS']._serialized_start = 335
    _globals['_QUANTCREATEPARAMS']._serialized_end = 555
    _globals['_QUANTIFICATIONSUMMARY']._serialized_start = 558
    _globals['_QUANTIFICATIONSUMMARY']._serialized_end = 731