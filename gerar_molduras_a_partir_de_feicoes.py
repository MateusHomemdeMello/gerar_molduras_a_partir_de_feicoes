from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterBoolean,
    QgsFeature,
    QgsGeometry,
    QgsRectangle,
    QgsFields,
    QgsField
)
from PyQt5.QtCore import QVariant
import math


class MolduraPorFeicao(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    SCALE = 'SCALE'
    MAP_WIDTH_CM = 'MAP_WIDTH_CM'
    MAP_HEIGHT_CM = 'MAP_HEIGHT_CM'
    OVERLAP = 'OVERLAP'
    OVERLAP_PERCENT = 'OVERLAP_PERCENT'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Camada de entrada (polígonos)',
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SCALE,
                'Escala (ex: 1000 ou 750.5)',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1000
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.MAP_WIDTH_CM,
                'Largura do mapa no layout (Ex.: 12.5cm)',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=15
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.MAP_HEIGHT_CM,
                'Altura do mapa no layout (Ex.: 12.5cm)',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OVERLAP,
                'Usar sobreposição?',
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.OVERLAP_PERCENT,
                'Percentual de sobreposição (0.1 = 10%)',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.1
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                'Molduras geradas'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        source = self.parameterAsSource(parameters, self.INPUT, context)
        scale = self.parameterAsDouble(parameters, self.SCALE, context)
        map_w_cm = self.parameterAsDouble(parameters, self.MAP_WIDTH_CM, context)
        map_h_cm = self.parameterAsDouble(parameters, self.MAP_HEIGHT_CM, context)
        use_overlap = self.parameterAsBool(parameters, self.OVERLAP, context)
        overlap_percent = self.parameterAsDouble(parameters, self.OVERLAP_PERCENT, context)

        # 🔥 Conversão cm → metros
        ground_w = (map_w_cm / 100.0) * scale
        ground_h = (map_h_cm / 100.0) * scale

        # 🔥 Overlap correto
        if use_overlap:
            overlap_percent = min(overlap_percent, 0.4)

            overlap_x = ground_w * overlap_percent
            overlap_y = ground_h * overlap_percent

            step_x = ground_w - overlap_x
            step_y = ground_h - overlap_y
        else:
            step_x = ground_w
            step_y = ground_h

        # 🔥 Campos de saída (copiando atributos da entrada)
        fields = QgsFields()

        for f in source.fields():
            fields.append(f)

        fields.append(QgsField('id_feat', QVariant.Int))
        fields.append(QgsField('folha', QVariant.Int))
        fields.append(QgsField('total_folhas', QVariant.Int))
        fields.append(QgsField('col', QVariant.Int))
        fields.append(QgsField('row', QVariant.Int))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            source.wkbType(),
            source.sourceCrs()
        )

        total_features = source.featureCount()

        for feat_id, feat in enumerate(source.getFeatures()):

            if feedback.isCanceled():
                break

            geom = feat.geometry()
            bbox = geom.boundingBox()

            xmin_bbox = bbox.xMinimum()
            xmax_bbox = bbox.xMaximum()
            ymin_bbox = bbox.yMinimum()
            ymax_bbox = bbox.yMaximum()

            # 🔥 cálculo correto do grid
            cols = math.ceil((xmax_bbox - xmin_bbox - ground_w) / step_x) + 1
            rows = math.ceil((ymax_bbox - ymin_bbox - ground_h) / step_y) + 1

            cols = max(cols, 1)
            rows = max(rows, 1)

            # 🔥 CENTRALIZAÇÃO REAL
            center = geom.pointOnSurface().asPoint()
            cx = center.x()
            cy = center.y()

            grid_w = (cols - 1) * step_x + ground_w
            grid_h = (rows - 1) * step_y + ground_h

            xmin = cx - (grid_w / 2)
            ymin = cy - (grid_h / 2)

            total_folhas = cols * rows
            folha = 1

            for i in range(cols):
                for j in range(rows):

                    x1 = xmin + i * step_x
                    y1 = ymin + j * step_y
                    x2 = x1 + ground_w
                    y2 = y1 + ground_h

                    rect = QgsRectangle(x1, y1, x2, y2)
                    grid_geom = QgsGeometry.fromRect(rect)

                    if not grid_geom.intersects(geom):
                        continue

                    new_feat = QgsFeature()
                    new_feat.setGeometry(grid_geom)
                    new_feat.setFields(fields)

                    # 🔥 copia atributos originais
                    attrs = feat.attributes()

                    # 🔥 adiciona novos
                    attrs.extend([
                        feat_id,
                        folha,
                        total_folhas,
                        i,
                        j
                    ])

                    new_feat.setAttributes(attrs)

                    sink.addFeature(new_feat)

                    folha += 1

            feedback.setProgress(int((feat_id / total_features) * 100))

        return {self.OUTPUT: dest_id}

    def name(self):
        return 'moldura_por_feicao'

    def displayName(self):
        return 'Moldura por Feição (por escala)'

    def group(self):
        return 'Geoprocessamento'

    def groupId(self):
        return 'geoprocessamento'

    def createInstance(self):
        return MolduraPorFeicao()