"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from . import element_set_pb2 as element__set__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11widget-data.proto\x1a\x11element-set.proto"(\n\nVisibleROI\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06scanId\x18\x02 \x01(\t"G\n\x14SpectrumXRFLineState\x12\x1e\n\x08lineInfo\x18\x01 \x01(\x0b2\x0c.ElementLine\x12\x0f\n\x07visible\x18\x02 \x01(\x08"L\n\x11EnergyCalibration\x12\x10\n\x08detector\x18\x01 \x01(\t\x12\x0f\n\x07eVStart\x18\x02 \x01(\x02\x12\x14\n\x0ceVPerChannel\x18\x03 \x01(\x02"7\n\rSpectrumLines\x12\r\n\x05roiID\x18\x01 \x01(\t\x12\x17\n\x0flineExpressions\x18\x02 \x03(\t"\xcd\x01\n\x13SpectrumWidgetState\x12\x0c\n\x04panX\x18\x01 \x01(\x02\x12\x0c\n\x04panY\x18\x02 \x01(\x02\x12\r\n\x05zoomX\x18\x03 \x01(\x02\x12\r\n\x05zoomY\x18\x04 \x01(\x02\x12%\n\rspectrumLines\x18\x05 \x03(\x0b2\x0e.SpectrumLines\x12\x10\n\x08logScale\x18\x06 \x01(\x08\x12\x15\n\rshowXAsEnergy\x18\x08 \x01(\x08\x12\x15\n\ryCountsPerMin\x18\n \x01(\x08\x12\x15\n\ryCountsPerPMC\x18\x0b \x01(\x08"\xb9\x01\n\x0eHistogramState\x12\x18\n\x10showStdDeviation\x18\x01 \x01(\x08\x12\x10\n\x08logScale\x18\x02 \x01(\x08\x12\x15\n\rexpressionIDs\x18\x03 \x03(\t\x12 \n\x0bvisibleROIs\x18\x04 \x03(\x0b2\x0b.VisibleROI\x12\x14\n\x0cshowWhiskers\x18\x05 \x01(\x08\x12\x1a\n\x12whiskerDisplayMode\x18\x06 \x01(\t\x12\x10\n\x08zoomMode\x18\x07 \x01(\t"v\n\nChordState\x12\x18\n\x10showForSelection\x18\x01 \x01(\x08\x12\x15\n\rexpressionIDs\x18\x02 \x03(\t\x12\x12\n\ndisplayROI\x18\x03 \x01(\t\x12\x11\n\tthreshold\x18\x04 \x01(\x02\x12\x10\n\x08drawMode\x18\x05 \x01(\t"X\n\x0bBinaryState\x12\x10\n\x08showMmol\x18\x01 \x01(\x08\x12\x15\n\rexpressionIDs\x18\x02 \x03(\t\x12 \n\x0bvisibleROIs\x18\x03 \x03(\x0b2\x0b.VisibleROI"Y\n\x0cTernaryState\x12\x10\n\x08showMmol\x18\x01 \x01(\x08\x12\x15\n\rexpressionIDs\x18\x02 \x03(\t\x12 \n\x0bvisibleROIs\x18\x03 \x03(\x0b2\x0b.VisibleROI"A\n\x12VisibleROIAndQuant\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06scanId\x18\x02 \x01(\t\x12\x0f\n\x07quantId\x18\x03 \x01(\t"_\n\nTableState\x12\x18\n\x10showPureElements\x18\x01 \x01(\x08\x12\r\n\x05order\x18\x02 \x01(\t\x12(\n\x0bvisibleROIs\x18\x03 \x03(\x0b2\x13.VisibleROIAndQuant"3\n\x12ROIQuantTableState\x12\x0b\n\x03roi\x18\x01 \x01(\t\x12\x10\n\x08quantIDs\x18\x02 \x03(\t"\xc5\x02\n\x0eVariogramState\x12\x15\n\rexpressionIDs\x18\x01 \x03(\t\x12 \n\x0bvisibleROIs\x18\x02 \x03(\x0b2\x0b.VisibleROI\x12\x12\n\nvarioModel\x18\x03 \x01(\t\x12\x13\n\x0bmaxDistance\x18\x04 \x01(\x02\x12\x10\n\x08binCount\x18\x05 \x01(\x05\x12\x16\n\x0edrawModeVector\x18\x06 \x01(\x08\x12\x1c\n\x14comparisonAlgorithms\x18\x07 \x03(\t\x12\x12\n\nliveUpdate\x18\x08 \x01(\x08\x12\x19\n\x11distanceSliderMin\x18\t \x01(\x02\x12\x19\n\x11distanceSliderMax\x18\n \x01(\x02\x12\x14\n\x0cbinSliderMin\x18\x0b \x01(\x02\x12\x14\n\x0cbinSliderMax\x18\x0c \x01(\x02\x12\x13\n\x0bdrawBestFit\x18\r \x01(\x08"\xa5\x01\n\x12MapLayerVisibility\x12\x14\n\x0cexpressionID\x18\x01 \x01(\t\x12\x0f\n\x07opacity\x18\x02 \x01(\x02\x12\x0f\n\x07visible\x18\x03 \x01(\x08\x12\x1c\n\x14displayValueRangeMin\x18\x04 \x01(\x02\x12\x1c\n\x14displayValueRangeMax\x18\x05 \x01(\x02\x12\x1b\n\x13displayValueShading\x18\x06 \x01(\t"R\n\x12ROILayerVisibility\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07opacity\x18\x02 \x01(\x02\x12\x0f\n\x07visible\x18\x03 \x01(\x08\x12\x0e\n\x06scanId\x18\x04 \x01(\t"\xc8\x05\n\x11ContextImageState\x12\x0c\n\x04panX\x18\x01 \x01(\x02\x12\x0c\n\x04panY\x18\x02 \x01(\x02\x12\r\n\x05zoomX\x18\x03 \x01(\x02\x12\r\n\x05zoomY\x18\x04 \x01(\x02\x12\x12\n\nshowPoints\x18\x05 \x01(\x08\x12\x15\n\rshowPointBBox\x18\x06 \x01(\x08\x12\x19\n\x11pointColourScheme\x18\x07 \x01(\t\x12\x1d\n\x15pointBBoxColourScheme\x18\x08 \x01(\t\x12\x14\n\x0ccontextImage\x18\t \x01(\t\x12\x1d\n\x15contextImageSmoothing\x18\n \x01(\t\x12&\n\tmapLayers\x18\x0b \x03(\x0b2\x13.MapLayerVisibility\x12&\n\troiLayers\x18\x0c \x03(\x0b2\x13.ROILayerVisibility\x12\x1e\n\x16elementRelativeShading\x18\r \x01(\x08\x12\x12\n\nbrightness\x18\x0e \x01(\x02\x12\x14\n\x0crgbuChannels\x18\x0f \x01(\t\x12\x19\n\x11unselectedOpacity\x18\x10 \x01(\x02\x12\x1b\n\x13unselectedGrayscale\x18\x11 \x01(\x08\x12\x16\n\x0ecolourRatioMin\x18\x12 \x01(\x02\x12\x16\n\x0ecolourRatioMax\x18\x13 \x01(\x02\x12"\n\x1aremoveTopSpecularArtifacts\x18\x14 \x01(\x08\x12%\n\x1dremoveBottomSpecularArtifacts\x18\x15 \x01(\x08\x12\x1e\n\x16hideFootprintsForScans\x18\x16 \x03(\t\x12\x1a\n\x12hidePointsForScans\x18\x17 \x03(\t\x12\x19\n\x11unlinkFromDataset\x18\x19 \x01(\x08\x12\x11\n\thideImage\x18\x1a \x01(\x08\x12"\n\x1ashowMISTROIReproducibility\x18\x1b \x01(\x08J\x04\x08\x18\x10\x19"R\n\x0fAnnotationPoint\x12\t\n\x01x\x18\x01 \x01(\x02\x12\t\n\x01y\x18\x02 \x01(\x02\x12\x13\n\x0bscreenWidth\x18\x03 \x01(\x02\x12\x14\n\x0cscreenHeight\x18\x04 \x01(\x02"\x98\x01\n\x18FullScreenAnnotationItem\x12\x0c\n\x04type\x18\x01 \x01(\t\x12 \n\x06points\x18\x02 \x03(\x0b2\x10.AnnotationPoint\x12\x0e\n\x06colour\x18\x03 \x01(\t\x12\x10\n\x08complete\x18\x04 \x01(\x08\x12\x0c\n\x04text\x18\x05 \x01(\t\x12\x10\n\x08fontSize\x18\x06 \x01(\x05\x12\n\n\x02id\x18\x07 \x01(\x05"M\n\x16AnnotationDisplayState\x123\n\x10savedAnnotations\x18\x01 \x03(\x0b2\x19.FullScreenAnnotationItem"\xe0\x01\n\x0fROIDisplayState\x124\n\nroiColours\x18\x01 \x03(\x0b2 .ROIDisplayState.RoiColoursEntry\x122\n\troiShapes\x18\x02 \x03(\x0b2\x1f.ROIDisplayState.RoiShapesEntry\x1a1\n\x0fRoiColoursEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x028\x01\x1a0\n\x0eRoiShapesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x028\x01"\x9a\x02\n\x13RGBUPlotWidgetState\x12\x10\n\x08minerals\x18\x01 \x03(\t\x12\x11\n\tyChannelA\x18\x02 \x01(\t\x12\x11\n\tyChannelB\x18\x03 \x01(\t\x12\x11\n\txChannelA\x18\x04 \x01(\t\x12\x11\n\txChannelB\x18\x05 \x01(\t\x12\x16\n\x0edrawMonochrome\x18\x06 \x01(\x08\x12\x19\n\x11selectedMinXValue\x18\x07 \x01(\x02\x12\x19\n\x11selectedMaxXValue\x18\x08 \x01(\x02\x12\x19\n\x11selectedMinYValue\x18\t \x01(\x02\x12\x19\n\x11selectedMaxYValue\x18\n \x01(\x02\x12\x11\n\timageName\x18\x0b \x01(\t\x12\x0e\n\x06roiIds\x18\x0c \x03(\t"\xe1\x01\n\x19SingleAxisRGBUWidgetState\x12\x10\n\x08minerals\x18\x01 \x03(\t\x12\x10\n\x08channelA\x18\x02 \x01(\t\x12\x10\n\x08channelB\x18\x03 \x01(\t\x12\x19\n\x11roiStackedOverlap\x18\x04 \x01(\x08\x12\x11\n\timageName\x18\x05 \x01(\t\x12\x18\n\x10selectedMinValue\x18\x06 \x01(\x02\x12\x18\n\x10selectedMaxValue\x18\x07 \x01(\x02\x12\x0e\n\x06roiIds\x18\x08 \x03(\t\x12\x1c\n\x14showAllMineralLabels\x18\t \x01(\x08">\n\x15RGBUImagesWidgetState\x12\x12\n\nbrightness\x18\x02 \x01(\x02\x12\x11\n\timageName\x18\x03 \x01(\t"\x81\x01\n\x18ParallelogramWidgetState\x12\x0f\n\x07regions\x18\x01 \x03(\t\x12\x10\n\x08channels\x18\x02 \x03(\t\x12\x13\n\x0bexcludeZero\x18\x04 \x01(\x08\x12\x13\n\x0baverageMode\x18\x05 \x01(\t\x12\x12\n\nsigmaLevel\x18\x06 \x01(\tJ\x04\x08\x03\x10\x04"$\n\x11MarkdownViewState\x12\x0f\n\x07content\x18\x01 \x01(\t"\xb7\x04\n\nWidgetData\x12\n\n\x02id\x18\x01 \x01(\t\x12&\n\x08spectrum\x18\x02 \x01(\x0b2\x14.SpectrumWidgetState\x12\x1c\n\x06binary\x18\x03 \x01(\x0b2\x0c.BinaryState\x12\x1e\n\x07ternary\x18\x04 \x01(\x0b2\r.TernaryState\x12"\n\thistogram\x18\x05 \x01(\x0b2\x0f.HistogramState\x12(\n\x0ccontextImage\x18\x06 \x01(\x0b2\x12.ContextImageState\x12\x1a\n\x05chord\x18\x07 \x01(\x0b2\x0b.ChordState\x12\x1a\n\x05table\x18\x08 \x01(\x0b2\x0b.TableState\x12*\n\rroiQuantTable\x18\t \x01(\x0b2\x13.ROIQuantTableState\x12"\n\tvariogram\x18\n \x01(\x0b2\x0f.VariogramState\x12&\n\x08rgbuPlot\x18\x0b \x01(\x0b2\x14.RGBUPlotWidgetState\x122\n\x0esingleAxisRGBU\x18\x0c \x01(\x0b2\x1a.SingleAxisRGBUWidgetState\x12)\n\trgbuImage\x18\r \x01(\x0b2\x16.RGBUImagesWidgetState\x120\n\rparallelogram\x18\x0e \x01(\x0b2\x19.ParallelogramWidgetState\x12(\n\x0cmarkdownView\x18\x0f \x01(\x0b2\x12.MarkdownViewStateB\nZ\x08.;protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'widget_data_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x08.;protos'
    _globals['_ROIDISPLAYSTATE_ROICOLOURSENTRY']._options = None
    _globals['_ROIDISPLAYSTATE_ROICOLOURSENTRY']._serialized_options = b'8\x01'
    _globals['_ROIDISPLAYSTATE_ROISHAPESENTRY']._options = None
    _globals['_ROIDISPLAYSTATE_ROISHAPESENTRY']._serialized_options = b'8\x01'
    _globals['_VISIBLEROI']._serialized_start = 40
    _globals['_VISIBLEROI']._serialized_end = 80
    _globals['_SPECTRUMXRFLINESTATE']._serialized_start = 82
    _globals['_SPECTRUMXRFLINESTATE']._serialized_end = 153
    _globals['_ENERGYCALIBRATION']._serialized_start = 155
    _globals['_ENERGYCALIBRATION']._serialized_end = 231
    _globals['_SPECTRUMLINES']._serialized_start = 233
    _globals['_SPECTRUMLINES']._serialized_end = 288
    _globals['_SPECTRUMWIDGETSTATE']._serialized_start = 291
    _globals['_SPECTRUMWIDGETSTATE']._serialized_end = 496
    _globals['_HISTOGRAMSTATE']._serialized_start = 499
    _globals['_HISTOGRAMSTATE']._serialized_end = 684
    _globals['_CHORDSTATE']._serialized_start = 686
    _globals['_CHORDSTATE']._serialized_end = 804
    _globals['_BINARYSTATE']._serialized_start = 806
    _globals['_BINARYSTATE']._serialized_end = 894
    _globals['_TERNARYSTATE']._serialized_start = 896
    _globals['_TERNARYSTATE']._serialized_end = 985
    _globals['_VISIBLEROIANDQUANT']._serialized_start = 987
    _globals['_VISIBLEROIANDQUANT']._serialized_end = 1052
    _globals['_TABLESTATE']._serialized_start = 1054
    _globals['_TABLESTATE']._serialized_end = 1149
    _globals['_ROIQUANTTABLESTATE']._serialized_start = 1151
    _globals['_ROIQUANTTABLESTATE']._serialized_end = 1202
    _globals['_VARIOGRAMSTATE']._serialized_start = 1205
    _globals['_VARIOGRAMSTATE']._serialized_end = 1530
    _globals['_MAPLAYERVISIBILITY']._serialized_start = 1533
    _globals['_MAPLAYERVISIBILITY']._serialized_end = 1698
    _globals['_ROILAYERVISIBILITY']._serialized_start = 1700
    _globals['_ROILAYERVISIBILITY']._serialized_end = 1782
    _globals['_CONTEXTIMAGESTATE']._serialized_start = 1785
    _globals['_CONTEXTIMAGESTATE']._serialized_end = 2497
    _globals['_ANNOTATIONPOINT']._serialized_start = 2499
    _globals['_ANNOTATIONPOINT']._serialized_end = 2581
    _globals['_FULLSCREENANNOTATIONITEM']._serialized_start = 2584
    _globals['_FULLSCREENANNOTATIONITEM']._serialized_end = 2736
    _globals['_ANNOTATIONDISPLAYSTATE']._serialized_start = 2738
    _globals['_ANNOTATIONDISPLAYSTATE']._serialized_end = 2815
    _globals['_ROIDISPLAYSTATE']._serialized_start = 2818
    _globals['_ROIDISPLAYSTATE']._serialized_end = 3042
    _globals['_ROIDISPLAYSTATE_ROICOLOURSENTRY']._serialized_start = 2943
    _globals['_ROIDISPLAYSTATE_ROICOLOURSENTRY']._serialized_end = 2992
    _globals['_ROIDISPLAYSTATE_ROISHAPESENTRY']._serialized_start = 2994
    _globals['_ROIDISPLAYSTATE_ROISHAPESENTRY']._serialized_end = 3042
    _globals['_RGBUPLOTWIDGETSTATE']._serialized_start = 3045
    _globals['_RGBUPLOTWIDGETSTATE']._serialized_end = 3327
    _globals['_SINGLEAXISRGBUWIDGETSTATE']._serialized_start = 3330
    _globals['_SINGLEAXISRGBUWIDGETSTATE']._serialized_end = 3555
    _globals['_RGBUIMAGESWIDGETSTATE']._serialized_start = 3557
    _globals['_RGBUIMAGESWIDGETSTATE']._serialized_end = 3619
    _globals['_PARALLELOGRAMWIDGETSTATE']._serialized_start = 3622
    _globals['_PARALLELOGRAMWIDGETSTATE']._serialized_end = 3751
    _globals['_MARKDOWNVIEWSTATE']._serialized_start = 3753
    _globals['_MARKDOWNVIEWSTATE']._serialized_end = 3789
    _globals['_WIDGETDATA']._serialized_start = 3792
    _globals['_WIDGETDATA']._serialized_end = 4359