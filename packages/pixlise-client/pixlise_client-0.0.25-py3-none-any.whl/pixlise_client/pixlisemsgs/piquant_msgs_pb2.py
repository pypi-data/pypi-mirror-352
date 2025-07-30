"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import piquant_config_pb2 as piquant__config__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12piquant-msgs.proto\x1a\x14piquant-config.proto"\x16\n\x14PiquantConfigListReq",\n\x15PiquantConfigListResp\x12\x13\n\x0bconfigNames\x18\x01 \x03(\t"0\n\x1cPiquantConfigVersionsListReq\x12\x10\n\x08configId\x18\x01 \x01(\t"1\n\x1dPiquantConfigVersionsListResp\x12\x10\n\x08versions\x18\x01 \x03(\t"<\n\x17PiquantConfigVersionReq\x12\x10\n\x08configId\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t"A\n\x18PiquantConfigVersionResp\x12%\n\rpiquantConfig\x18\x01 \x01(\x0b2\x0e.PiquantConfig"\x17\n\x15PiquantVersionListReq"1\n\x16PiquantVersionListResp\x12\x17\n\x0fpiquantVersions\x18\x01 \x03(\t"7\n\x1dPiquantWriteCurrentVersionReq\x12\x16\n\x0epiquantVersion\x18\x01 \x01(\t"8\n\x1ePiquantWriteCurrentVersionResp\x12\x16\n\x0epiquantVersion\x18\x01 \x01(\t"\x1a\n\x18PiquantCurrentVersionReq"D\n\x19PiquantCurrentVersionResp\x12\'\n\x0epiquantVersion\x18\x01 \x01(\x0b2\x0f.PiquantVersionB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'piquant_msgs_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_PIQUANTCONFIGLISTREQ']._serialized_start = 44
    _globals['_PIQUANTCONFIGLISTREQ']._serialized_end = 66
    _globals['_PIQUANTCONFIGLISTRESP']._serialized_start = 68
    _globals['_PIQUANTCONFIGLISTRESP']._serialized_end = 112
    _globals['_PIQUANTCONFIGVERSIONSLISTREQ']._serialized_start = 114
    _globals['_PIQUANTCONFIGVERSIONSLISTREQ']._serialized_end = 162
    _globals['_PIQUANTCONFIGVERSIONSLISTRESP']._serialized_start = 164
    _globals['_PIQUANTCONFIGVERSIONSLISTRESP']._serialized_end = 213
    _globals['_PIQUANTCONFIGVERSIONREQ']._serialized_start = 215
    _globals['_PIQUANTCONFIGVERSIONREQ']._serialized_end = 275
    _globals['_PIQUANTCONFIGVERSIONRESP']._serialized_start = 277
    _globals['_PIQUANTCONFIGVERSIONRESP']._serialized_end = 342
    _globals['_PIQUANTVERSIONLISTREQ']._serialized_start = 344
    _globals['_PIQUANTVERSIONLISTREQ']._serialized_end = 367
    _globals['_PIQUANTVERSIONLISTRESP']._serialized_start = 369
    _globals['_PIQUANTVERSIONLISTRESP']._serialized_end = 418
    _globals['_PIQUANTWRITECURRENTVERSIONREQ']._serialized_start = 420
    _globals['_PIQUANTWRITECURRENTVERSIONREQ']._serialized_end = 475
    _globals['_PIQUANTWRITECURRENTVERSIONRESP']._serialized_start = 477
    _globals['_PIQUANTWRITECURRENTVERSIONRESP']._serialized_end = 533
    _globals['_PIQUANTCURRENTVERSIONREQ']._serialized_start = 535
    _globals['_PIQUANTCURRENTVERSIONREQ']._serialized_end = 561
    _globals['_PIQUANTCURRENTVERSIONRESP']._serialized_start = 563
    _globals['_PIQUANTCURRENTVERSIONRESP']._serialized_end = 631