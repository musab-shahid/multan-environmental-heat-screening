"""Spatial separation and all-year weight scenarios for the supplied heat exports.

No satellite re-extraction, calibration or health-risk validation is performed.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
YEARS=[2003,2008,2013,2018,2023]
BUFFERS_KM=[0,2,5]
SEED=42

def weight_grid():
    return [(a/10,b/10,(10-a-b)/10) for a in range(11) for b in range(11-a)]

def evaluate_weights(frame):
    summaries=[];details=[];membership=[]
    for year,group in frame.groupby('YEAR',sort=True):
        g=group.sort_values('SOURCE_ID').reset_index(drop=True)
        x=g[['LST_PCT','NDBI_PCT']].assign(vegetation_deficit=1-g.SAVI_PCT).to_numpy()
        baseline=x@np.array([.5,.3,.2])
        base_top=set(np.argsort(-baseline,kind='stable')[:14])
        ranks=[];classes=[];selected=[]
        for idx,w in enumerate(weight_grid()):
            score=x@np.array(w)
            rank=pd.Series(score).rank(ascending=False,method='average').to_numpy()
            top=set(np.argsort(-score,kind='stable')[:14])
            category=np.where(score<=1/3,0,np.where(score<=2/3,1,2))
            ranks.append(rank);classes.append(category);selected.append(np.array([i in top for i in range(len(g))]))
            summaries.append(dict(YEAR=int(year),scenario=idx,w_lst=w[0],w_ndbi=w[1],w_vegetation=w[2],top14_overlap=len(base_top&top),jaccard=len(base_top&top)/len(base_top|top),rank_spearman=pd.Series(baseline).corr(pd.Series(score),method='spearman')))
        ranks=np.array(ranks);classes=np.array(classes);selected=np.array(selected)
        for i,row in g.iterrows():
            details.append(dict(YEAR=int(year),SOURCE_ID=row.SOURCE_ID,UC_C=row.UC_C,baseline_score=baseline[i],baseline_top14=i in base_top,best_rank=ranks[:,i].min(),worst_rank=ranks[:,i].max(),median_rank=np.median(ranks[:,i]),top14_scenarios=int(selected[:,i].sum()),total_scenarios=len(ranks),top14_fraction=selected[:,i].mean(),lower_scenarios=int((classes[:,i]==0).sum()),middle_scenarios=int((classes[:,i]==1).sum()),higher_scenarios=int((classes[:,i]==2).sum())))
    return pd.DataFrame(summaries),pd.DataFrame(details)

def spatial_splits(polygons,buffers_km=BUFFERS_KM):
    """Whole councils, all years, geometry-only blocks; polygon-edge buffers."""
    councils=polygons[['UC_C','geometry']].dissolve(by='UC_C').sort_index()
    centers=councils.geometry.centroid
    coordinates=np.column_stack([centers.x,centers.y])
    raw=KMeans(n_clusters=5,random_state=SEED,n_init=20).fit_predict(coordinates)
    # Relabel west-to-east for stable, readable block numbers.
    order=sorted(set(raw),key=lambda k:coordinates[raw==k,0].mean())
    councils['BLOCK']=[order.index(k)+1 for k in raw]
    assignments=councils[['BLOCK']].reset_index()
    for block in sorted(councils.BLOCK.unique()):
        test=councils[councils.BLOCK==block]
        pool=councils[councils.BLOCK!=block]
        distance=pool.geometry.distance(test.geometry.union_all())
        for km in buffers_km:
            # Zero means unbuffered geographic blocks; touching boundaries allowed.
            keep=np.ones(len(pool),dtype=bool) if km==0 else distance.to_numpy()>=km*1000
            train=pool.loc[keep]
            if len(train)<5:raise ValueError(f'Too few training councils: block {block}, buffer {km}')
            assert set(train.index).isdisjoint(test.index)
            yield assignments,dict(block=int(block),buffer_km=km,train_councils=set(train.index),test_councils=set(test.index),excluded_councils=set(pool.index)-set(train.index),min_distance_m=float(distance.loc[train.index].min()))

def main():
    raw=pd.read_csv(ROOT/'data/earth_engine_polygon_statistics.csv')
    raw['SOURCE_ID']=raw['system:index'].str.rsplit('_',n=1).str[-1]
    assert not raw.duplicated(['YEAR','SOURCE_ID']).any()
    assert raw.groupby('SOURCE_ID')['.geo'].nunique().eq(1).all()
    frame=pd.read_csv(ROOT/'results/polygon_screening.csv',dtype={'SOURCE_ID':str})
    assert len(frame)==440 and sorted(frame.YEAR.unique())==YEARS
    geometries=raw.drop_duplicates('SOURCE_ID')[['SOURCE_ID','UC_C','.geo']].copy()
    geo=gpd.GeoDataFrame(geometries.drop(columns='.geo'),geometry=geometries['.geo'].map(lambda s:shape(json.loads(s))),crs=4326).to_crs(32642)
    assert geo.is_valid.all()
    metrics=[];predictions=[];members=[];audit=[]
    for assignments,split in spatial_splits(geo):
        train=frame[frame.UC_C.isin(split['train_councils'])]
        test=frame[frame.UC_C.isin(split['test_councils'])]
        assert set(train.SOURCE_ID).isdisjoint(test.SOURCE_ID)
        assert set(train.YEAR)==set(test.YEAR)==set(YEARS)
        for council in assignments.UC_C:
            role='train' if council in split['train_councils'] else 'test' if council in split['test_councils'] else 'buffer_excluded'
            members.append(dict(block=split['block'],buffer_km=split['buffer_km'],UC_C=council,role=role))
        audit.append(dict(block=split['block'],buffer_km=split['buffer_km'],train_councils=len(split['train_councils']),test_councils=len(split['test_councils']),excluded_councils=len(split['excluded_councils']),train_records=len(train),test_records=len(test),minimum_polygon_distance_m=split['min_distance_m']))
        for name,model in [('RF',RandomForestRegressor(n_estimators=200,min_samples_leaf=3,random_state=SEED,n_jobs=-1)),('Mean baseline',DummyRegressor())]:
            model.fit(train[['SAVI','NDBI']],train.LST)
            prediction=model.predict(test[['SAVI','NDBI']])
            metrics.append(dict(block=split['block'],buffer_km=split['buffer_km'],model=name,MAE=mean_absolute_error(test.LST,prediction),R2=r2_score(test.LST,prediction),test_records=len(test)))
            for (_,row),value in zip(test.iterrows(),prediction):predictions.append(dict(block=split['block'],buffer_km=split['buffer_km'],model=name,SOURCE_ID=row.SOURCE_ID,YEAR=int(row.YEAR),observed_lst=row.LST,predicted_lst=value))
    metrics=pd.DataFrame(metrics);predictions=pd.DataFrame(predictions)
    metrics.to_csv(ROOT/'results/spatial_validation.csv',index=False)
    predictions.to_csv(ROOT/'results/spatial_predictions.csv',index=False)
    pd.DataFrame(members).to_csv(ROOT/'results/spatial_split_membership.csv',index=False)
    pd.DataFrame(audit).to_csv(ROOT/'results/spatial_split_checks.csv',index=False)
    assignments.to_csv(ROOT/'results/spatial_blocks.csv',index=False)
    summary=metrics.groupby(['buffer_km','model']).agg(mean_fold_MAE=('MAE','mean'),min_fold_MAE=('MAE','min'),max_fold_MAE=('MAE','max'),mean_fold_R2=('R2','mean')).reset_index()
    summary.to_csv(ROOT/'results/spatial_validation_summary.csv',index=False)
    scenarios,stability=evaluate_weights(frame)
    scenarios.to_csv(ROOT/'results/weight_grid_scenarios.csv',index=False)
    stability.to_csv(ROOT/'results/polygon_weight_stability.csv',index=False)
    scenarios.groupby('YEAR').agg(scenarios=('scenario','size'),min_top14_overlap=('top14_overlap','min'),median_top14_overlap=('top14_overlap','median'),max_top14_overlap=('top14_overlap','max'),min_rank_correlation=('rank_spearman','min')).to_csv(ROOT/'results/weight_grid_summary.csv')
    fig,axs=plt.subplots(1,2,figsize=(11,4.5))
    mapped=geo.merge(assignments,on='UC_C',validate='many_to_one')
    mapped.plot(column='BLOCK',categorical=True,cmap='Set2',edgecolor='white',linewidth=.3,legend=True,ax=axs[0]);axs[0].set_axis_off();axs[0].set_title('Five geographic blocks\nAll parts of each council stay together')
    for name,color in [('RF','#176b62'),('Mean baseline','#9d7251')]:
        v=summary[summary.model==name];axs[1].plot(v.buffer_km,v.mean_fold_MAE,'o-',label=name,color=color)
    axs[1].set(xlabel='Excluded neighborhood around test polygons (km)',ylabel='Mean fold MAE (°C)',title='LST prediction in held-out geographic blocks');axs[1].set_xticks(BUFFERS_KM);axs[1].legend()
    fig.tight_layout();fig.savefig(ROOT/'figures/spatial_validation.png',dpi=180);plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(11,4))
    vals=[scenarios.loc[scenarios.YEAR==year,'top14_overlap'] for year in YEARS]
    axs[0].boxplot(vals,labels=YEARS);axs[0].set(ylabel='Overlap with baseline top 14 polygons',xlabel='Year',ylim=(-.5,14.8),title='66 weight scenarios per year')
    for year in YEARS:
        v=stability[(stability.YEAR==year)&stability.baseline_top14].sort_values('top14_fraction')
        axs[1].plot(range(1,15),v.top14_fraction,'o-',markersize=3,label=str(year))
    axs[1].set(xlabel='Baseline top-14 polygons, ordered by stability',ylabel='Fraction of scenarios retaining top-14 status',ylim=(-.03,1.03),title='Sensitivity to weighting, not probability');axs[1].legend(ncol=2,fontsize=8)
    fig.tight_layout();fig.savefig(ROOT/'figures/weight_stability.png',dpi=180);plt.close(fig)
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'data').glob('*.csv'))}
    (ROOT/'results/robustness_settings.json').write_text(json.dumps(dict(seed=SEED,spatial_blocks=5,buffers_km=BUFFERS_KM,coordinate_crs='EPSG:32642',block_assignment='KMeans on dissolved council centroids; no response values used',distance='Minimum distance between complete training council and test council geometries',weight_grid_step=.1,weight_scenarios_per_year=66,top_k=14,scenario_interpretation='Deliberate stress-test grid, not a probability distribution',input_sha256=manifest),indent=2))
    print(summary.to_string(index=False));print('Completed 15 spatial splits and 330 year-weight scenarios.')

if __name__=='__main__':main()
