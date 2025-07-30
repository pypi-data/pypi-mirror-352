"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14quantification.proto"\xaf\x03\n\x0eQuantification\x12\x0e\n\x06labels\x18\x01 \x03(\t\x12,\n\x05types\x18\x02 \x03(\x0e2\x1d.Quantification.QuantDataType\x125\n\x0blocationSet\x18\x03 \x03(\x0b2 .Quantification.QuantLocationSet\x1a\xa5\x01\n\rQuantLocation\x12\x0b\n\x03pmc\x18\x01 \x01(\x05\x12\x0b\n\x03rtt\x18\x02 \x01(\x05\x12\x0c\n\x04sclk\x18\x03 \x01(\x05\x12;\n\x06values\x18\x05 \x03(\x0b2+.Quantification.QuantLocation.QuantDataItem\x1a/\n\rQuantDataItem\x12\x0e\n\x06fvalue\x18\x02 \x01(\x02\x12\x0e\n\x06ivalue\x18\x03 \x01(\x05\x1aU\n\x10QuantLocationSet\x12\x10\n\x08detector\x18\x01 \x01(\t\x12/\n\x08location\x18\x02 \x03(\x0b2\x1d.Quantification.QuantLocation")\n\rQuantDataType\x12\x0c\n\x08QT_FLOAT\x10\x00\x12\n\n\x06QT_INT\x10\x01B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'quantification_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_QUANTIFICATION']._serialized_start = 25
    _globals['_QUANTIFICATION']._serialized_end = 456
    _globals['_QUANTIFICATION_QUANTLOCATION']._serialized_start = 161
    _globals['_QUANTIFICATION_QUANTLOCATION']._serialized_end = 326
    _globals['_QUANTIFICATION_QUANTLOCATION_QUANTDATAITEM']._serialized_start = 279
    _globals['_QUANTIFICATION_QUANTLOCATION_QUANTDATAITEM']._serialized_end = 326
    _globals['_QUANTIFICATION_QUANTLOCATIONSET']._serialized_start = 328
    _globals['_QUANTIFICATION_QUANTLOCATIONSET']._serialized_end = 413
    _globals['_QUANTIFICATION_QUANTDATATYPE']._serialized_start = 415
    _globals['_QUANTIFICATION_QUANTDATATYPE']._serialized_end = 456