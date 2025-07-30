"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import ownership_access_pb2 as ownership__access__pb2
from . import version_pb2 as version__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11expressions.proto\x1a\x16ownership-access.proto\x1a\rversion.proto"\x90\x02\n\x0eDataExpression\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x12\n\nsourceCode\x18\x03 \x01(\t\x12\x16\n\x0esourceLanguage\x18\x04 \x01(\t\x12\x10\n\x08comments\x18\x05 \x01(\t\x12\x0c\n\x04tags\x18\x06 \x03(\t\x12*\n\x10moduleReferences\x18\x07 \x03(\x0b2\x10.ModuleReference\x121\n\x0frecentExecStats\x18\x08 \x01(\x0b2\x18.DataExpressionExecStats\x12\x17\n\x0fmodifiedUnixSec\x18\t \x01(\r\x12 \n\x05owner\x18\n \x01(\x0b2\x11.OwnershipSummary"F\n\x0fModuleReference\x12\x10\n\x08moduleId\x18\x01 \x01(\t\x12!\n\x07version\x18\x02 \x01(\x0b2\x10.SemanticVersion"f\n\x17DataExpressionExecStats\x12\x14\n\x0cdataRequired\x18\x01 \x03(\t\x12\x1b\n\x13runtimeMsPer1000Pts\x18\x02 \x01(\x02\x12\x18\n\x10timeStampUnixSec\x18\x03 \x01(\r"8\n\x14ExpressionResultItem\x12\x10\n\x08location\x18\x01 \x01(\x05\x12\x0e\n\x06values\x18\x02 \x03(\x02";\n\x19ExpressionDisplaySettings\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\ncolourRamp\x18\x02 \x01(\tB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'expressions_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_DATAEXPRESSION']._serialized_start = 61
    _globals['_DATAEXPRESSION']._serialized_end = 333
    _globals['_MODULEREFERENCE']._serialized_start = 335
    _globals['_MODULEREFERENCE']._serialized_end = 405
    _globals['_DATAEXPRESSIONEXECSTATS']._serialized_start = 407
    _globals['_DATAEXPRESSIONEXECSTATS']._serialized_end = 509
    _globals['_EXPRESSIONRESULTITEM']._serialized_start = 511
    _globals['_EXPRESSIONRESULTITEM']._serialized_end = 567
    _globals['_EXPRESSIONDISPLAYSETTINGS']._serialized_start = 569
    _globals['_EXPRESSIONDISPLAYSETTINGS']._serialized_end = 628