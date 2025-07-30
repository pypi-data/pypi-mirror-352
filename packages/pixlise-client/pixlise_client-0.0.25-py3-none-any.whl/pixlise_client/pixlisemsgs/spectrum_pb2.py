"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import scan_pb2 as scan__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0espectrum.proto\x1a\nscan.proto"\xbe\x01\n\x08Spectrum\x12\x10\n\x08detector\x18\x01 \x01(\t\x12\x1b\n\x04type\x18\x02 \x01(\x0e2\r.SpectrumType\x12\x0e\n\x06counts\x18\x03 \x03(\r\x12\x10\n\x08maxCount\x18\x04 \x01(\r\x12!\n\x04meta\x18\x05 \x03(\x0b2\x13.Spectrum.MetaEntry\x1a>\n\tMetaEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12 \n\x05value\x18\x02 \x01(\x0b2\x11.ScanMetaDataItem:\x028\x01"%\n\x07Spectra\x12\x1a\n\x07spectra\x18\x01 \x03(\x0b2\t.Spectrum"\xca\x01\n\x0eClientSpectrum\x12\x10\n\x08detector\x18\x01 \x01(\t\x12\x1b\n\x04type\x18\x02 \x01(\x0e2\r.SpectrumType\x12\x0e\n\x06counts\x18\x03 \x03(\r\x12\x10\n\x08maxCount\x18\x04 \x01(\r\x12\'\n\x04meta\x18\x05 \x03(\x0b2\x19.ClientSpectrum.MetaEntry\x1a>\n\tMetaEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12 \n\x05value\x18\x02 \x01(\x0b2\x11.ScanMetaDataItem:\x028\x01"H\n\x1fClientSpectrumEnergyCalibration\x12\x0f\n\x07StarteV\x18\x01 \x01(\x02\x12\x14\n\x0cPerChanneleV\x18\x02 \x01(\x02"\xca\x01\n\x17ClientEnergyCalibration\x12P\n\x14DetectorCalibrations\x18\x01 \x03(\x0b22.ClientEnergyCalibration.DetectorCalibrationsEntry\x1a]\n\x19DetectorCalibrationsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12/\n\x05value\x18\x02 \x01(\x0b2 .ClientSpectrumEnergyCalibration:\x028\x01*r\n\x0cSpectrumType\x12\x14\n\x10SPECTRUM_UNKNOWN\x10\x00\x12\x10\n\x0cSPECTRUM_MAX\x10\x01\x12\x11\n\rSPECTRUM_BULK\x10\x02\x12\x13\n\x0fSPECTRUM_NORMAL\x10\x03\x12\x12\n\x0eSPECTRUM_DWELL\x10\x04*J\n\x17EnergyCalibrationSource\x12\x0f\n\x0bCAL_UNKNOWN\x10\x00\x12\x10\n\x0cCAL_BULK_SUM\x10\x01\x12\x0c\n\x08CAL_USER\x10\x02B\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'spectrum_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_SPECTRUM_METAENTRY']._options = None
    _globals['_SPECTRUM_METAENTRY']._serialized_options = b'8\x01'
    _globals['_CLIENTSPECTRUM_METAENTRY']._options = None
    _globals['_CLIENTSPECTRUM_METAENTRY']._serialized_options = b'8\x01'
    _globals['_CLIENTENERGYCALIBRATION_DETECTORCALIBRATIONSENTRY']._options = None
    _globals['_CLIENTENERGYCALIBRATION_DETECTORCALIBRATIONSENTRY']._serialized_options = b'8\x01'
    _globals['_SPECTRUMTYPE']._serialized_start = 746
    _globals['_SPECTRUMTYPE']._serialized_end = 860
    _globals['_ENERGYCALIBRATIONSOURCE']._serialized_start = 862
    _globals['_ENERGYCALIBRATIONSOURCE']._serialized_end = 936
    _globals['_SPECTRUM']._serialized_start = 31
    _globals['_SPECTRUM']._serialized_end = 221
    _globals['_SPECTRUM_METAENTRY']._serialized_start = 159
    _globals['_SPECTRUM_METAENTRY']._serialized_end = 221
    _globals['_SPECTRA']._serialized_start = 223
    _globals['_SPECTRA']._serialized_end = 260
    _globals['_CLIENTSPECTRUM']._serialized_start = 263
    _globals['_CLIENTSPECTRUM']._serialized_end = 465
    _globals['_CLIENTSPECTRUM_METAENTRY']._serialized_start = 403
    _globals['_CLIENTSPECTRUM_METAENTRY']._serialized_end = 465
    _globals['_CLIENTSPECTRUMENERGYCALIBRATION']._serialized_start = 467
    _globals['_CLIENTSPECTRUMENERGYCALIBRATION']._serialized_end = 539
    _globals['_CLIENTENERGYCALIBRATION']._serialized_start = 542
    _globals['_CLIENTENERGYCALIBRATION']._serialized_end = 744
    _globals['_CLIENTENERGYCALIBRATION_DETECTORCALIBRATIONSENTRY']._serialized_start = 651
    _globals['_CLIENTENERGYCALIBRATION_DETECTORCALIBRATIONSENTRY']._serialized_end = 744