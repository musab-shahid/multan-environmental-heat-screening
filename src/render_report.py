"""Render the research report and map book from checked release results."""
from pathlib import Path
import csv,json,re
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from PIL import Image as PILImage
from pypdf import PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
TITLE='Spatiotemporal Urban Heat Vulnerability Assessment — Multan, Pakistan (2003–2023)'
styles=getSampleStyleSheet()
font_pairs=[(Path('C:/Windows/Fonts/arial.ttf'),Path('C:/Windows/Fonts/arialbd.ttf')),(Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))]
regular,bold=next((a,b) for a,b in font_pairs if a.exists() and b.exists())
pdfmetrics.registerFont(TTFont('ResearchSans',str(regular)));pdfmetrics.registerFont(TTFont('ResearchSansBold',str(bold)))
pdfmetrics.registerFontFamily('ResearchSans',normal='ResearchSans',bold='ResearchSansBold',italic='ResearchSans',boldItalic='ResearchSansBold')
for style in styles.byName.values():
    if hasattr(style,'fontName'):style.fontName='ResearchSansBold' if 'Bold' in style.fontName else 'ResearchSans'
styles.add(ParagraphStyle(name='Research',fontName='ResearchSans',fontSize=10.2,leading=14.2,spaceAfter=9))
styles.add(ParagraphStyle(name='Caption',fontName='ResearchSans',fontSize=8.5,leading=11,spaceAfter=10,textColor=colors.HexColor('#52605c')))
styles['Title'].fontSize=25;styles['Title'].leading=29;styles['Title'].textColor=colors.HexColor('#174f47')
styles['Heading1'].fontSize=17;styles['Heading1'].leading=21;styles['Heading1'].spaceAfter=12
story=[];md=[]
def p(text):
    story.append(Paragraph(text.replace('−','-'),styles['Research']))
    markdown=re.sub(r'<link href="([^"]+)"[^>]*>(.*?)</link>',r'[\2](\1)',text).replace('<b>','**').replace('</b>','**')
    md.append(markdown)
def h(text):story.append(Paragraph(text,styles['Heading1']));md.append('## '+text)
def page():story.append(PageBreak())
def table(rows,widths):
    rendered=[[Paragraph(escape(str(c)),styles['Caption']) for c in row] for row in rows]
    t=Table(rendered,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4eee9')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f7f6')]),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#ccd3cf')),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.extend([t,Spacer(1,10)]);md.append('\n'.join(['| '+' | '.join(map(str,rows[0]))+' |','|'+'---|'*len(rows[0])]+['| '+' | '.join(map(str,r))+' |' for r in rows[1:]]))
def fig(path,caption,width=490):
    with PILImage.open(ROOT/path) as im:height=width*im.height/im.width
    story.append(KeepTogether([Image(str(ROOT/path),width=width,height=height),Paragraph(caption,styles['Caption'])]))
    md.append(f'![{caption}](../{path})')
def read(name):return list(csv.DictReader(open(ROOT/'results'/name,encoding='utf-8')))

story.append(Paragraph(TITLE,styles['Title']));md.append('# '+TITLE)
p('Exploratory environmental screening using Google Earth Engine, Colab and machine learning')
p('<b>Musab Shahid | Research report | Revised 9 November 2026</b>')
h('Abstract')
p('This study evaluates satellite surface-temperature, vegetation and built-up indicators for 88 source polygons in Multan at five benchmark years. All 440 polygon-year observations are retained in a transparent within-year environmental screening score. The source polygons represent 82 council codes; repeated codes are kept together during model evaluation.')
p('The current release adds geographic block validation with 2 and 5 km exclusion buffers and 66 additive weight scenarios for each year. At a 5 km buffer, Random Forest mean fold error is 2.99°C compared with 3.44°C for a training-mean baseline. Errors and explanatory performance vary across blocks. Previously evaluated transfer to an unseen year remains poor: RF mean fold error is 4.42°C, worse than the 3.68°C baseline.')
p('Across the full weight grid, 10–14 of the baseline top 14 polygons remain in the selected group, depending on year and weights. These scenario counts describe sensitivity to assumptions, not probabilities of vulnerability. A portable GIS release provides five separate yearly layers, styled layouts and a map book.')
h('Research contribution')
p('The contribution is a reproducible link between polygon identity, environmental screening, model-transfer evaluation and usable GIS outputs. It supports investigation of relative surface conditions within each benchmark year. It does not establish a calibrated warming trend, population exposure, clinical vulnerability or a causal vegetation-cooling effect.')

page();h('1. Data and study design')
p('The inputs are the supplied Earth Engine polygon-statistics export and the preserved legacy model-results table. No new satellite extraction was performed for this release. Geometry is carried from the user’s Multan_UCs asset and preserved using SOURCE_ID.')
table([['Year','Sensor','Historical window','Scenes','Polygons'],['2003','Landsat 7','1 April–30 May','6','88'],['2008','Landsat 7','1 June–1 July','2','88'],['2013','Landsat 8','1 June–1 July','8','88'],['2018','Landsat 8','1 June–1 July','6','88'],['2023','Landsat 9','1 June–1 July','8','88']],[49,82,178,65,116])
p('End dates are exclusive. The source workflow uses Landsat Collection 2 Level 2 products, cloud/shadow masking, scale factors, median composites and a water mask. Valid-pixel fractions were not supplied. Two scenes in 2008 do not demonstrate that Landsat 7 SLC-off gaps were repaired.')
p('The VIIRS product chosen by the historical workflow starts in 2014. Earlier missing or placeholder lights are not observed zero radiance. The current score therefore uses LST, NDBI and SAVI in all five years. The 352-row legacy classifier is retained only for historical comparison; its constructed labels are not independent vulnerability observations.')
h('Polygon identity and joins')
p('Each year has 88 unique SOURCE_ID values with stable geometries. Council names and codes repeat across years and, for some councils, across source polygons. The legacy snapshot was matched with a verified composite key; new spatial layers already contain their own attributes. A five-year table must never be joined by ward name alone.')
p('LST is surface temperature, not air temperature. SAVI and NDBI describe spectral signals rather than independently validated land-cover fractions. Historical extraction windows, sensors and observation coverage differ, so year means are descriptive summaries rather than calibrated long-term trends.')

page();h('2. Screening and descriptive results')
p('Within each year, variables receive average percentile ranks. The baseline score is 0.50 × rank(LST) + 0.30 × rank(NDBI) + 0.20 × [1 − rank(SAVI)]. Lower, Middle and Higher use score cutoffs at 1/3 and 2/3. These are proposed exploratory categories, not equal-size terciles or health thresholds.')
rows=[['Year','Mean LST (°C)','Mean SAVI','Lower / Middle / Higher']]
counts={x['year']:x['classes'] for x in json.loads((ROOT/'gis/gis_checks.json').read_text())['layers']}
for r in read('year_summary.csv'):
    c=counts[int(r['YEAR'])];rows.append([r['YEAR'],f"{float(r['Mean_LST']):.2f}",f"{float(r['Mean_SAVI']):.3f}",f"{c['Lower']} / {c['Middle']} / {c['Higher']}"])
table(rows,[55,115,110,210])
fig('figures/lst_savi_by_year.png','Figure 1. Observed LST–SAVI associations, shown separately by year. Shared axes support inspection of the supplied values; they do not harmonize the extraction windows.')
p('The means summarize polygon means without area weighting. Every year contributes all 88 source polygons. No health, demographic or population-exposure data are present. Rank colors are recalculated each year; color changes cannot be interpreted as physical warming or cooling.')
p('The screening formula is unchanged from the preceding release. New robustness analyses examine its dependence on weights and the separate LST model’s dependence on geographic proximity.')

page();h('3. Geographic model evaluation')
p('The separate regression predicts LST from SAVI and NDBI. It uses 200 trees, minimum leaf size 3 and seed 42, with no test-fold tuning. Five geographic blocks are formed from dissolved council centroids in UTM 42N using KMeans (seed 42, 20 starts), without using LST. All parts and years of a council remain in one block.')
p('Each block is held out in turn. The buffered variants remove entire training councils if any part lies within 2 or 5 km of a test polygon. Distances use complete polygon geometries, not just centroid distances. Zero denotes the same geographic blocks without a buffer. Both models use the same retained training records.')
rows=[['Exclusion buffer','RF MAE (°C)','Baseline MAE (°C)','RF fold MAE range']]
for km in [0,2,5]:
    s=[r for r in read('spatial_validation_summary.csv') if int(r['buffer_km'])==km];a=next(r for r in s if r['model']=='RF');b=next(r for r in s if r['model']=='Mean baseline')
    rows.append([f'{km} km',f"{float(a['mean_fold_MAE']):.2f}",f"{float(b['mean_fold_MAE']):.2f}",f"{float(a['min_fold_MAE']):.2f}–{float(a['max_fold_MAE']):.2f}"])
table(rows,[105,110,130,145])
fig('figures/spatial_validation.png','Figure 2. Geometry-only geographic blocks and unweighted mean fold MAE for the prespecified exclusion distances.')
p('At 5 km, training folds retain 41–63 councils. RF beats the baseline on MAE in four of five blocks, but its mean fold R-squared is negative (−0.18). A modest average error advantage does not imply reliable prediction everywhere. Buffers test geographic separation; they do not prove independent residuals or eliminate shared year effects.')

page();h('4. Temporal transfer and weighting assumptions')
p('The earlier council-group holdout gives RF mean fold MAE 2.42°C versus baseline 3.22°C. Leave-one-year-out gives RF 4.42°C versus baseline 3.68°C, with negative RF R-squared in every held-out year. The new spatial tests retain all years in training and test blocks; they do not solve prediction in a new year or a simultaneous new place and year.')
p('Weight sensitivity now covers all nonnegative triples summing to one in 0.1 increments: 66 scenarios per year, including single-indicator extremes. Each selects the top 14 polygons; ties are resolved by SOURCE_ID. The grid is a deliberate stress test, not a claim that all weights are equally plausible.')
rows=[['Year','Scenarios','Minimum / median / maximum overlap','Always in top 14']]
stability=read('polygon_weight_stability.csv')
for r in read('weight_grid_summary.csv'):
    count=sum(int(s['top14_scenarios'])==66 for s in stability if s['YEAR']==r['YEAR'])
    rows.append([r['YEAR'],'66',f"{r['min_top14_overlap']} / {float(r['median_top14_overlap']):g} / {r['max_top14_overlap']}",str(count)])
table(rows,[45,65,275,105])
fig('figures/weight_stability.png','Figure 3. Top-group overlap across scenarios and selection frequency among the baseline top 14. Frequency describes this grid only; it is not a probability or confidence interval.')
p('The stable core supports a focused review of consistently high-ranked locations, while unstable positions should be reported with their rank range and scenario counts. It does not validate optimal intervention priorities, because the score has no external health or exposure target.')

page();h('5. GIS deliverables and map interpretation')
p('The portable GIS package contains a GeoPackage with five year-specific layers, a QGIS project using relative paths, matching styles and five print layouts. The project opens with only 2023 visible. Each layer has 88 features, one YEAR and unique SOURCE_ID values, with current RELATIVE_SCORE and RELATIVE_CLASS attributes.')
fig('gis/Screening_2023.png','Figure 4. Example current map layout. The downloadable map book includes one page for each benchmark year.',width=490)
p('Open Multan_Heat_Screening.qgz in QGIS, switch on one year at a time, and use its matching layout. ArcGIS Pro can read the GeoPackage layers; the .qgz project and .qml styles are QGIS-specific. The data CRS is WGS84 and the layouts use WGS84 / UTM zone 42N for scale and distance.')
p('These maps replace the old RF-class presentation for current interpretation. In particular, 2013 now displays all 88 screening polygons because the current score does not require missing nighttime lights. The historical RF maps remain archived and should not be mixed with the new categories.')

page();h('6. Reproducibility, limitations and conclusion')
p('Run src/analyze.py from the repository root to rebuild the existing screening, regression checks and GeoJSON layers; then run src/robustness.py for the spatial and weighting analyses. The updated notebook executes both stages. The GIS builder uses the separate QGIS Python runtime; report rendering uses reportlab and pypdf.')
p('Six tests check the weight grid, scenario accounting, test-record uniqueness, council membership and buffer distances, recalculated prediction errors, and preservation of the baseline score. Source-file hashes and exact settings are stored with the results. GIS checks verify one year and 88 unique feature identities per layer; relative paths support moving the project with its GeoPackage.')
h('Limits of the evidence')
p('This release does not re-extract harmonized seasonal imagery, quantify missing-pixel coverage, validate boundaries against an authoritative current source, or calibrate sensors. The original boundary vintage and redistribution terms remain unverified. Existing provider rights apply; no blanket geometry license is granted.')
p('The five geographic blocks and three buffer settings are a prespecified sensitivity design, not an exhaustive spatial-validation study. No block layout or buffer was selected for favorable model scores. There are only five folds. Spatial and temporal tests answer different prediction questions, and neither validates the constructed screening score against health outcomes.')
p('The project now provides a more complete assessment of geographic transfer, explicit all-year weight sensitivity and directly usable GIS materials. Its defensible contribution remains exploratory environmental screening with transparent limitations, rather than an operational heat-health model.')
h('Sources and attribution')
sources=[('Landsat Collection 2 Level 2 products','https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2'),('VIIRS VCMSLCFG product','https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMSLCFG'),('scikit-learn grouped cross-validation documentation','https://scikit-learn.org/stable/modules/cross_validation.html'),('QGIS project and vector writer API','https://qgis.org/pyqgis/master/core/QgsProject.html'),('Public research repository','https://github.com/musab-shahid/multan-environmental-heat-screening')]
for label,url in sources:p(f'<link href="{url}" color="#176b62">{label}</link>')
p('Research by Musab Shahid. The November release includes AI-assisted code development, verification and editing. Suggested citation: Shahid, M. (2026). '+TITLE+'. Exploratory research report, revised 9 November 2026.')

def footer(canvas,doc):
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#60736c'));canvas.drawString(48,26,'Musab Shahid | Environmental heat screening | November 2026');canvas.drawRightString(A4[0]-48,26,str(doc.page))
doc=SimpleDocTemplate(str(ROOT/'docs/REPORT.pdf'),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=40,bottomMargin=42,title=TITLE,author='Musab Shahid')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(ROOT/'docs/REPORT.md').write_text('\n\n'.join(md)+'\n',encoding='utf-8')
writer=PdfWriter()
for year in [2003,2008,2013,2018,2023]:writer.append(ROOT/f'gis/Screening_{year}.pdf',outline_item=str(year))
writer.add_metadata({'/Title':TITLE+' — Map book','/Author':'Musab Shahid'})
writer.write(ROOT/'gis/Multan_Heat_Screening_Map_Book.pdf')
print('Rendered report and five-page map book.')
