"""
***************************************************************************
    offsetcurve.py
    ---------------------
    Date                 : Janaury 2015
    Copyright            : (C) 2015 by Giovanni Manghi
    Email                : giovanni dot manghi at naturalgis dot pt
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Giovanni Manghi'
__date__ = 'January 2015'
__copyright__ = '(C) 2015, Giovanni Manghi'

from qgis.core import (QgsProcessing,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterString,
                       QgsProcessingException,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterVectorDestination)
from processing.algs.gdal.GdalAlgorithm import GdalAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils


class OffsetCurve(GdalAlgorithm):
    INPUT = 'INPUT'
    GEOMETRY = 'GEOMETRY'
    DISTANCE = 'DISTANCE'
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,
                                                              self.tr('Input layer'),
                                                              [QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterString(self.GEOMETRY,
                                                       self.tr('Geometry column name'),
                                                       defaultValue='geometry'))
        self.addParameter(QgsProcessingParameterDistance(self.DISTANCE,
                                                         self.tr('Offset distance (left-sided: positive, right-sided: negative)'),
                                                         parentParameterName=self.INPUT,
                                                         defaultValue=10))

        options_param = QgsProcessingParameterString(self.OPTIONS,
                                                     self.tr('Additional creation options'),
                                                     defaultValue='',
                                                     optional=True)
        options_param.setFlags(options_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(options_param)

        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT,
                                                                  self.tr('Offset curve'),
                                                                  QgsProcessing.TypeVectorLine))

    def name(self):
        return 'offsetcurve'

    def displayName(self):
        return self.tr('Offset curve')

    def group(self):
        return self.tr('Vector geoprocessing')

    def groupId(self):
        return 'vectorgeoprocessing'

    def commandName(self):
        return 'ogr2ogr'

    def getConsoleCommands(self, parameters, context, feedback, executing=True):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        fields = source.fields()
        ogrLayer, layerName = self.getOgrCompatibleSource(self.INPUT, parameters, context, feedback, executing)
        geometry = self.parameterAsString(parameters, self.GEOMETRY, context)
        distance = self.parameterAsDouble(parameters, self.DISTANCE, context)
        options = self.parameterAsString(parameters, self.OPTIONS, context)
        outFile = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        self.setOutputValue(self.OUTPUT, outFile)

        output, outputFormat = GdalUtils.ogrConnectionStringAndFormat(outFile, context)

        other_fields_exist = any(
            True for f in fields
            if f.name() != geometry
        )

        other_fields = ',*' if other_fields_exist else ''

        arguments = [
            output,
            ogrLayer,
            '-dialect',
            'sqlite',
            '-sql'
        ]
        sql = f'SELECT ST_OffsetCurve({geometry}, {distance}) AS {geometry}{other_fields} FROM "{layerName}"'
        arguments.append(sql)

        if options:
            arguments.append(options)

        if outputFormat:
            arguments.append(f'-f {outputFormat}')

        return ['ogr2ogr', GdalUtils.escapeAndJoin(arguments)]
