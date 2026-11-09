import unittest
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('robustness',ROOT/'src/robustness.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class RobustnessTests(unittest.TestCase):
    def test_weight_grid_and_baseline(self):
        weights=module.weight_grid()
        self.assertEqual(len(weights),66)
        self.assertEqual(len(set(weights)),66)
        self.assertIn((.5,.3,.2),weights)
        self.assertTrue(all(abs(sum(w)-1)<1e-12 and min(w)>=0 for w in weights))
    def test_scenario_accounting(self):
        s=pd.read_csv(ROOT/'results/polygon_weight_stability.csv')
        self.assertEqual(len(s),440)
        self.assertTrue((s[['lower_scenarios','middle_scenarios','higher_scenarios']].sum(axis=1)==66).all())
        self.assertTrue((s.groupby('YEAR').top14_scenarios.sum()==66*14).all())
    def test_each_record_tested_once_per_buffer(self):
        p=pd.read_csv(ROOT/'results/spatial_predictions.csv',dtype={'SOURCE_ID':str})
        for _,g in p.groupby(['buffer_km','model']):
            self.assertEqual(len(g),440)
            self.assertFalse(g.duplicated(['SOURCE_ID','YEAR']).any())
    def test_separation_and_council_roles(self):
        checks=pd.read_csv(ROOT/'results/spatial_split_checks.csv')
        self.assertEqual(len(checks),15)
        self.assertTrue((checks.minimum_polygon_distance_m+1e-6>=checks.buffer_km*1000).all())
        m=pd.read_csv(ROOT/'results/spatial_split_membership.csv')
        self.assertFalse(m.duplicated(['block','buffer_km','UC_C']).any())
        self.assertTrue((m.groupby(['block','buffer_km']).size()==82).all())
    def test_metrics_recalculate_from_predictions(self):
        m=pd.read_csv(ROOT/'results/spatial_validation.csv')
        p=pd.read_csv(ROOT/'results/spatial_predictions.csv')
        for _,row in m.iterrows():
            g=p[(p.block==row.block)&(p.buffer_km==row.buffer_km)&(p.model==row.model)]
            self.assertAlmostEqual(np.abs(g.observed_lst-g.predicted_lst).mean(),row.MAE,places=10)
    def test_original_screening_preserved(self):
        p=pd.read_csv(ROOT/'results/polygon_screening.csv')
        score=.5*p.LST_PCT+.3*p.NDBI_PCT+.2*(1-p.SAVI_PCT)
        np.testing.assert_allclose(score,p.RELATIVE_SCORE,rtol=1e-12,atol=1e-12)
if __name__=='__main__':unittest.main()
