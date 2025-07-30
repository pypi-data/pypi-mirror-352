"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tjob.proto"\xc1\x04\n\tJobStatus\x12\r\n\x05jobId\x18\x01 \x01(\t\x12!\n\x06status\x18\x02 \x01(\x0e2\x11.JobStatus.Status\x12\x0f\n\x07message\x18\x03 \x01(\t\x12\r\n\x05logId\x18\x04 \x01(\t\x12\x11\n\tjobItemId\x18\n \x01(\t\x12#\n\x07jobType\x18\x0b \x01(\x0e2\x12.JobStatus.JobType\x12\x18\n\x10startUnixTimeSec\x18\x05 \x01(\r\x12\x1d\n\x15lastUpdateUnixTimeSec\x18\x06 \x01(\r\x12\x16\n\x0eendUnixTimeSec\x18\x07 \x01(\r\x12\x16\n\x0eoutputFilePath\x18\x08 \x01(\t\x12\x15\n\rotherLogFiles\x18\t \x03(\t\x12\x17\n\x0frequestorUserId\x18\x0c \x01(\t\x12\x0c\n\x04name\x18\r \x01(\t\x12\x10\n\x08elements\x18\x0e \x03(\t"u\n\x06Status\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0c\n\x08STARTING\x10\x01\x12\x13\n\x0fPREPARING_NODES\x10\x02\x12\x0b\n\x07RUNNING\x10\x03\x12\x15\n\x11GATHERING_RESULTS\x10\x04\x12\x0c\n\x08COMPLETE\x10\x05\x12\t\n\x05ERROR\x10\x06"z\n\x07JobType\x12\x0e\n\nJT_UNKNOWN\x10\x00\x12\x12\n\x0eJT_IMPORT_SCAN\x10\x01\x12\x14\n\x10JT_REIMPORT_SCAN\x10\x02\x12\x13\n\x0fJT_IMPORT_IMAGE\x10\x03\x12\x10\n\x0cJT_RUN_QUANT\x10\x04\x12\x0e\n\nJT_RUN_FIT\x10\x05"b\n\x10JobHandlerDBItem\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05jobId\x18\x02 \x01(\t\x12\x19\n\x11handlerInstanceId\x18\x03 \x01(\t\x12\x18\n\x10timeStampUnixSec\x18\x04 \x01(\rB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'job_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_JOBSTATUS']._serialized_start = 14
    _globals['_JOBSTATUS']._serialized_end = 591
    _globals['_JOBSTATUS_STATUS']._serialized_start = 350
    _globals['_JOBSTATUS_STATUS']._serialized_end = 467
    _globals['_JOBSTATUS_JOBTYPE']._serialized_start = 469
    _globals['_JOBSTATUS_JOBTYPE']._serialized_end = 591
    _globals['_JOBHANDLERDBITEM']._serialized_start = 593
    _globals['_JOBHANDLERDBITEM']._serialized_end = 691