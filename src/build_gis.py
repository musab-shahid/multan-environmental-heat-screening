"""Build a portable QGIS project and one-year-at-a-time screening maps.

Run with the QGIS Python interpreter, not the scientific-analysis environment.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
if os.environ.get('HEAT_PROJ_DATA'):
    os.environ['PROJ_DATA']=os.environ['HEAT_PROJ_DATA']
    os.environ['PROJ_LIB']=os.environ['HEAT_PROJ_DATA']
from pathlib import Path
import json
from qgis.core import (QgsApplication,QgsProject,QgsCoordinateReferenceSystem,QgsVectorLayer,QgsFillSymbol,QgsRendererCategory,QgsCategorizedSymbolRenderer,QgsPrintLayout,QgsLayoutItemPage,QgsLayoutItemLabel,QgsLayoutPoint,QgsLayoutSize,QgsLayoutItemMap,QgsCoordinateTransform,QgsLayoutItemLegend,QgsLayoutItemScaleBar,QgsUnitTypes,QgsLayoutExporter,QgsReferencedRectangle,QgsVectorFileWriter,Qgis)
from qgis.PyQt.QtGui import QFont,QFontDatabase

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'gis';OUT.mkdir(exist_ok=True)
app=QgsApplication([],False);app.initQgis()
if os.name=='nt':
    for font in ['arial.ttf','arialbd.ttf']:
        font_path=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/font
        if font_path.exists():QFontDatabase.addApplicationFont(str(font_path))
app.setFont(QFont('Arial',10))
project=QgsProject.instance();project.setCrs(QgsCoordinateReferenceSystem('EPSG:32642'))
project.setFilePathStorage(Qgis.FilePathType.Relative)
layers=[];checks=[]
gpkg=OUT/'Multan_Heat_Screening.gpkg'
for year in [2003,2008,2013,2018,2023]:
    source=QgsVectorLayer(str(ROOT/f'maps/screening_{year}.geojson'),str(year),'ogr')
    assert source.isValid() and source.featureCount()==88
    options=QgsVectorFileWriter.SaveVectorOptions();options.driverName='GPKG';options.layerName=f'screening_{year}'
    options.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteFile if year==2003 else QgsVectorFileWriter.CreateOrOverwriteLayer
    result=QgsVectorFileWriter.writeAsVectorFormatV3(source,str(gpkg),project.transformContext(),options)
    assert result[0]==QgsVectorFileWriter.NoError,str(result)
    layer=QgsVectorLayer(str(gpkg)+f'|layername=screening_{year}',f'{year} — relative screening','ogr')
    assert layer.isValid() and layer.featureCount()==88
    values=list(layer.getFeatures());ids=[str(f['SOURCE_ID']) for f in values]
    assert len(set(ids))==88 and {int(f['YEAR']) for f in values}=={year}
    counts={name:sum(str(f['RELATIVE_CLASS'])==name for f in values) for name in ['Lower','Middle','Higher']}
    assert sum(counts.values())==88
    checks.append(dict(year=year,features=88,unique_source_ids=88,classes=counts))
    categories=[]
    for value,color in [('Lower','#287c70'),('Middle','#e3c568'),('Higher','#ae4147')]:
        symbol=QgsFillSymbol.createSimple({'color':color,'outline_color':'#ffffff','outline_width':'0.12'})
        categories.append(QgsRendererCategory(value,symbol,value))
    layer.setRenderer(QgsCategorizedSymbolRenderer('RELATIVE_CLASS',categories))
    project.addMapLayer(layer);layers.append(layer);layer.saveNamedStyle(str(OUT/f'screening_{year}.qml'))
    layout=QgsPrintLayout(project);layout.initializeDefaults();layout.setName(f'Screening {year}')
    layout.pageCollection().pages()[0].setPageSize('A4',QgsLayoutItemPage.Landscape)
    def label(text,x,y,w,h,size=10):
        item=QgsLayoutItemLabel(layout);item.setText(text);item.setFont(QFont('Arial',size));layout.addLayoutItem(item);item.attemptMove(QgsLayoutPoint(x,y));item.attemptResize(QgsLayoutSize(w,h));return item
    label('Spatiotemporal Urban Heat Vulnerability Assessment —',10,7,280,9,16)
    label('Multan, Pakistan (2003–2023)',10,17,280,8,14)
    label(f'{year} | Relative environmental screening',10,28,280,8,12)
    mapitem=QgsLayoutItemMap(layout);layout.addLayoutItem(mapitem);mapitem.attemptMove(QgsLayoutPoint(10,39));mapitem.attemptResize(QgsLayoutSize(195,147));mapitem.setCrs(project.crs());mapitem.setLayers([layer]);mapitem.setKeepLayerSet(True)
    extent=QgsCoordinateTransform(layer.crs(),project.crs(),project).transformBoundingBox(layer.extent());extent.scale(1.06);mapitem.zoomToExtent(extent)
    legend=QgsLayoutItemLegend(layout);legend.setTitle('Within-year category');legend.setLinkedMap(mapitem);legend.setAutoUpdateModel(False);legend.model().rootGroup().clear();legend.model().rootGroup().addLayer(layer);layout.addLayoutItem(legend);legend.attemptMove(QgsLayoutPoint(211,42));legend.attemptResize(QgsLayoutSize(75,50))
    label('Grid N\n↑',184,41,22,20,12)
    scalebar=QgsLayoutItemScaleBar(layout);scalebar.setStyle('Single Box');scalebar.setLinkedMap(mapitem);scalebar.setUnits(QgsUnitTypes.DistanceKilometers);scalebar.setUnitsPerSegment(10);scalebar.setNumberOfSegments(2);scalebar.setNumberOfSegmentsLeft(0);scalebar.setUnitLabel('km');layout.addLayoutItem(scalebar);scalebar.attemptMove(QgsLayoutPoint(16,178))
    label('88 source polygons\n82 council codes\n\nScore components\nLST percentile: 50%\nNDBI percentile: 30%\nVegetation deficit: 20%\n\nLower: score ≤ 1/3\nMiddle: 1/3 < score ≤ 2/3\nHigher: score > 2/3',211,94,77,76,10)
    label('Compare locations within this year. Colors are not health-risk thresholds or calibrated changes through time.\nSources: supplied Landsat / Earth Engine exports and Multan_UCs boundaries. Display CRS: WGS 84 / UTM 42N.',10,191,280,12,8)
    project.layoutManager().addLayout(layout)
    exporter=QgsLayoutExporter(layout);settings=QgsLayoutExporter.ImageExportSettings();settings.dpi=160
    for suffix in ['png','pdf']:
        target=OUT/f'Screening_{year}.{suffix}'
        if target.exists():target.unlink()
    assert exporter.exportToImage(str(OUT/f'Screening_{year}.png'),settings)==QgsLayoutExporter.Success
    assert exporter.exportToPdf(str(OUT/f'Screening_{year}.pdf'),QgsLayoutExporter.PdfExportSettings())==QgsLayoutExporter.Success
for layer in layers:project.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(layer==layers[-1])
project.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(extent,project.crs()))
assert project.write(str(OUT/'Multan_Heat_Screening.qgz'))
(OUT/'gis_checks.json').write_text(json.dumps({'qgis_version':Qgis.QGIS_VERSION,'layers':checks,'data_crs':'EPSG:4326','display_crs':'EPSG:32642','paths':'relative','classification_field':'RELATIVE_CLASS'},indent=2))
print('Created GeoPackage, QGIS project, five styles and five year-specific map layouts.')
