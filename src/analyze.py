"""Reproducible descriptive screening and validation audit; no health-risk inference."""
from pathlib import Path
import json,sys,platform
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import GroupKFold,LeaveOneGroupOut
from sklearn.metrics import accuracy_score,balanced_accuracy_score,mean_absolute_error,r2_score
import sklearn
ROOT=Path(__file__).resolve().parents[1]
raw=pd.read_csv(ROOT/'data/earth_engine_polygon_statistics.csv')
old=pd.read_csv(ROOT/'data/legacy_model_results.csv')
keys=['YEAR','UC_C','WARD_NAME','Shape_Area','Shape_Leng']
assert not raw.duplicated(keys).any() and not old.duplicated(keys).any()
raw['SOURCE_ID']=raw['system:index'].str.rsplit('_',n=1).str[-1]
assert not raw.duplicated(['YEAR','SOURCE_ID']).any()
assert raw.groupby('SOURCE_ID')['.geo'].nunique().max()==1
joined=raw.merge(old[keys+['CLASS','RF_CLASS']],on=keys,how='left',validate='one_to_one')
assert joined.RF_CLASS.notna().sum()==352
required=['LST','SAVI','NDBI']
assert joined[required].notna().all().all()
# Actual lights are unavailable before 2014 in the selected VCMSLCFG product.
joined['LIGHTS_OBSERVED']=joined.LIGHTS.where(joined.YEAR>=2014)
for col in required:
    joined[col+'_PCT']=joined.groupby('YEAR')[col].rank(pct=True,method='average')
# Relative within-year environmental screening only. Proposed weights, no clinical threshold.
joined['RELATIVE_SCORE']=.5*joined.LST_PCT+.3*joined.NDBI_PCT+.2*(1-joined.SAVI_PCT)
joined['RELATIVE_CLASS']=pd.cut(joined.RELATIVE_SCORE,[-np.inf,1/3,2/3,np.inf],labels=['Lower','Middle','Higher'])
joined.drop(columns=['.geo']).to_csv(ROOT/'results/polygon_screening.csv',index=False)
summary=joined.groupby('YEAR').agg(Polygons=('SOURCE_ID','size'),Mean_LST=('LST','mean'),Min_LST=('LST','min'),Max_LST=('LST','max'),Mean_SAVI=('SAVI','mean'),Legacy_modeled=('RF_CLASS','count'),Observed_lights=('LIGHTS_OBSERVED','count'))
summary.to_csv(ROOT/'results/year_summary.csv')
# Legacy target agreement: groups held out, but original target globally constructed.
scores=[]
for fold,(train,test) in enumerate(GroupKFold(5).split(old,old.CLASS,old.WARD_NAME),1):
    assert set(old.iloc[train].WARD_NAME).isdisjoint(old.iloc[test].WARD_NAME)
    rf=RandomForestClassifier(n_estimators=200,random_state=42,n_jobs=-1)
    rf.fit(old.iloc[train][['SAVI','NDBI','LIGHTS']],old.iloc[train].CLASS)
    pred=rf.predict(old.iloc[test][['SAVI','NDBI','LIGHTS']])
    scores.append(dict(fold=fold,accuracy=accuracy_score(old.iloc[test].CLASS,pred),balanced_accuracy=balanced_accuracy_score(old.iloc[test].CLASS,pred),test_records=len(test)))
pd.DataFrame(scores).to_csv(ROOT/'results/legacy_group_validation.csv',index=False)
# A separate regression experiment predicts observed LST, rather than a self-built class.
reg=[]
for scheme,splitter,groups in [('held_out_council',GroupKFold(5),joined.UC_C),('held_out_year',LeaveOneGroupOut(),joined.YEAR)]:
    for fold,(train,test) in enumerate(splitter.split(joined,groups=groups),1):
        for name,model in [('RF',RandomForestRegressor(n_estimators=200,min_samples_leaf=3,random_state=42,n_jobs=-1)),('Mean baseline',DummyRegressor())]:
            model.fit(joined.iloc[train][['SAVI','NDBI']],joined.iloc[train].LST)
            pred=model.predict(joined.iloc[test][['SAVI','NDBI']])
            reg.append(dict(scheme=scheme,fold=fold,model=name,test_year=','.join(map(str,sorted(joined.iloc[test].YEAR.unique()))),MAE=mean_absolute_error(joined.iloc[test].LST,pred),R2=r2_score(joined.iloc[test].LST,pred),test_records=len(test)))
pd.DataFrame(reg).to_csv(ROOT/'results/lst_regression_validation.csv',index=False)
# Sensitivity holds the additive rank formula fixed and varies only weights.
top={}
for name,w in [('baseline',[.5,.3,.2]),('thermal',[.7,.2,.1]),('vegetation',[.4,.2,.4])]:
    v=joined[joined.YEAR==2023].copy()
    v['score']=w[0]*v.LST_PCT+w[1]*v.NDBI_PCT+w[2]*(1-v.SAVI_PCT)
    top[name]=set(v.sort_values(['score','SOURCE_ID'],ascending=[False,True]).head(14).SOURCE_ID)
pd.DataFrame([dict(scenario=k,top14_overlap=len(v&top['baseline']),jaccard=len(v&top['baseline'])/len(v|top['baseline'])) for k,v in top.items()]).to_csv(ROOT/'results/weight_sensitivity.csv',index=False)
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#faf9f5','axes.facecolor':'#faf9f5'})
fig,axs=plt.subplots(1,5,figsize=(16,4),sharex=True,sharey=True)
for ax,(year,sub) in zip(axs,joined.groupby('YEAR')):
    ax.scatter(sub.SAVI,sub.LST,s=18,color='#176b62',alpha=.7)
    ax.set(title=str(year),xlabel='SAVI')
axs[0].set_ylabel('Land surface temperature (°C)')
fig.suptitle('Observed vegetation–surface temperature patterns | 88 source polygons per year')
fig.text(.5,.01,'Different seasonal windows and sensors; descriptive observations, not a calibrated temperature trend.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.05,1,.95));fig.savefig(ROOT/'figures/lst_savi_by_year.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,4))
for name,color in [('RF','#176b62'),('Mean baseline','#ab8461')]:
    v=pd.DataFrame(reg);v=v[(v.scheme=='held_out_year')&(v.model==name)]
    ax.plot(v.test_year,v.MAE,'o-',label=name,color=color)
ax.set(xlabel='Held-out year',ylabel='MAE (°C)',title='Can vegetation and built-up indices predict LST in an unseen year?');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/temporal_generalization.png',dpi=180);plt.close(fig)
import geopandas as gpd
from shapely.geometry import shape
from matplotlib.patches import Patch
g=gpd.GeoDataFrame(joined,geometry=joined['.geo'].map(lambda s:shape(json.loads(s))),crs='EPSG:4326').to_crs(32642)
assert g.is_valid.all()
colors={'Lower':'#287c70','Middle':'#e3c568','Higher':'#ae4147'}
fig,axs=plt.subplots(1,5,figsize=(16,7))
for ax,(year,sub) in zip(axs,g.groupby('YEAR')):
    sub.plot(ax=ax,color=sub.RELATIVE_CLASS.map(colors).astype(str),edgecolor='white',linewidth=.35)
    ax.set_title(str(year));ax.set_axis_off()
fig.suptitle('Relative environmental heat screening within each year',fontsize=19)
fig.legend(handles=[Patch(color=c,label=k) for k,c in colors.items()],loc='lower center',ncol=3,bbox_to_anchor=(.5,.06))
fig.text(.5,.025,'Proposed rank-based score: LST 50%, NDBI 30%, vegetation deficit 20%. Relative categories are not health-risk thresholds.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.12,1,.94));fig.savefig(ROOT/'figures/relative_screening_maps.png',dpi=180);plt.close(fig)
for year,sub in g.groupby('YEAR'):
    sub[['SOURCE_ID','UC_C','WARD_NAME','YEAR','LST','SAVI','NDBI','RELATIVE_SCORE','RELATIVE_CLASS','geometry']].to_crs(4326).to_file(ROOT/f'maps/screening_{year}.geojson',driver='GeoJSON')
env=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__,matplotlib=matplotlib.__version__)
(ROOT/'results/environment.json').write_text(json.dumps(env,indent=2))
print(summary.to_string())
print('Legacy grouped RF mean:',np.mean([s['accuracy'] for s in scores]))
print('Completed: 440 descriptive records, 352 legacy validation records; all polygon joins unique.')
