import unittest
import json
import yaml
import tempfile
import os
from pydantic import ValidationError
from quickstats.workspace.elements import (
    Workspace,
    Category,
    Sample,
    CountingData, ASCIIData,
    Systematic,
    AsimovAction
)
from quickstats.utils.common_utils import load_json_or_yaml_file
from quickstats.interface.pydantic.helpers import resolve_field_import, resolve_model_import


class TestWorkspace(unittest.TestCase):

    def setUp(self):
        # Create temporary JSON and YAML files for samples and systematics
        self.temp_sample_json_file = self.create_temp_file(
            suffix='.json',
            content={
                'name': 'sample_from_json',
                'model': {
                    'type': 'userdef',
                    'modelitem': "EXPR::bkgPdf_JSON('exp((@0-100)*@1/100)', :observable:,  BKG_p0_JSON[-1,-1000,1000])"
                },
                'xsection': 1,
                'selection_eff': 1,
                'import_syst': ':self:',
                'multiply_lumi': False,
                'norm_factors': [{'name': 'nbkg_JSON[56,0,10000000]'}]
            }
        )

        self.temp_systematic_yaml_file = self.create_temp_file(
            suffix='.yaml',
            content={
                'name': 'systematic_from_yaml',
                'constr': 'logn',
                'central_value': 1,
                'magnitude': 0.009,
                'whereto': 'yield'
            }
        )

        self.temp_category_json_file = self.create_temp_file(
            suffix='.json',
            content={
                'name': 'new_category',
                'type': 'shape',
                'data': {
                    'type': 'ascii',
                    'filename': 'data_new_category.txt',
                    'observable': 'atlas_invMass_new[105,160]',
                    'binning': 220,
                    'inject_ghost': 1,
                    'blind_range': [120., 130.]
                },
                'lumi': 1.0,
                'samples': [],
                'systematics': [],
                'items': ['kl[1]', 'k2v[1]']
            }
        )

        self.temp_import_item_json_file = self.create_temp_file(
            suffix='.json',
            content={
                'systematics': [
                    {
                        'name': 'ggF_XS',
                        'constr': 'logn',
                        'magnitude': 0.087,
                        'whereto': 'yield'
                    },
                    {
                        'name': 'lumi',
                        'constr': 'logn',
                        'magnitude': 0.013,
                        'whereto': 'yield'
                    }
                ]
            }
        )

        # Define the workspace configuration
        self.config = {
            'categories': [
                {
                    'name': 'HM',
                    'type': 'shape',
                    'data': {
                        'type': 'ascii',
                        'filename': 'data_HM.txt',
                        'observable': 'atlas_invMass_HM[105,160]',
                        'binning': 220,
                        'inject_ghost': 1,
                        'blind_range':  [120., 130.]
                    },
                    'lumi': 1.0,
                    'samples': [
                        {
                            'name': 'ggFHH_kl1p0',
                            'model': {
                                'type': 'userdef',
                                'items': [
                                    'mH[125.0]',
                                    "expr::muCBNom_ggFHH_kl1p0('125.13090677127211-125+@0',mH)",
                                    "sigmaCBNom_ggFHH_kl1p0[1.4756097507355888]",
                                    "alphaCBLo_ggFHH_kl1p0[1.6204344639561659]",
                                    "alphaCBHi_ggFHH_kl1p0[1.4274901476939337]",
                                    "nCBLo_ggFHH_kl1p0[5.748568247067687]",
                                    "nCBHi_ggFHH_kl1p0[16.39930410986513]"
                                ],
                                'modelitem': "RooTwoSidedCBShape::signal(:observable:, prod::muCB_ggFHH_kl1p0(muCBNom_ggFHH_kl1p0,response::ggFHH_kl1p0_scale), prod::sigmaCB_ggFHH_kl1p0(sigmaCBNom_ggFHH_kl1p0,response::ggFHH_kl1p0_resolution), alphaCBLo_ggFHH_kl1p0, nCBLo_ggFHH_kl1p0, alphaCBHi_ggFHH_kl1p0, nCBHi_ggFHH_kl1p0)"
                            },
                            'xsection': 1,
                            'selection_eff': 1,
                            'import_syst': ':common:,ggFHH_kl1p0',
                            'multiply_lumi': True,
                            'norm_factors': [
                                {'name': 'yield_ggFHH_kl1p0[0.2538105445167669]'},
                                {'name': 'mu_HH_ggF[1]'},
                                {'name': 'SF_XS_ggFHH_kl1p0[1]', 'correlate': True},
                                {'name': 'mu_HH[1]'}
                            ]
                        },
                        self.temp_sample_json_file
                    ],
                    'systematics': [
                        {
                            'name': 'ATLAS_lumi_run2',
                            'constr': 'logn',
                            'central_value': 1,
                            'magnitude': 0.00830,
                            'whereto': 'yield'
                        },
                        self.temp_systematic_yaml_file
                    ],
                    'items': ['kl[1]', 'k2v[1]'],
                    'import_items': [
                        self.temp_import_item_json_file
                    ]
                },
                self.temp_category_json_file
            ],
            'pois': ['mu_HH_ggF', 'mu_HH_VBF', 'mu_HH'],
            'workspace_name': 'combWS',
            'modelconfig_name': 'ModelConfig',
            'dataset_name': 'obsData',
            'asimov_actions': [
                {
                    'name': 'setup',
                    'setup': 'mu_HH=1,mu_HH_ggF=1,mu_HH_VBF=1',
                    'action': ''
                },
                {
                    'name': 'POISnap',
                    'setup': '',
                    'action': 'savesnapshot',
                    'snapshot_poi': 'nominalPOI'
                },
                {
                    'name': 'NPSnap',
                    'setup': 'mu_HH=0',
                    'action': 'fixsyst:fit:float:savesnapshot:nominalPOI',
                    'snapshot_nuis': 'nominalNuis',
                    'snapshot_glob': 'nominalGlobs'
                }
            ],
            'binned_dataset': False,
            'blind': True,
            'data_storage_type': 'vector'
        }

    def create_temp_file(self, suffix, content):
        with tempfile.NamedTemporaryFile('w', suffix=suffix, delete=False) as temp_file:
            if suffix.endswith('.json'):
                json.dump(content, temp_file)
            elif suffix.endswith('.yaml') or suffix.endswith('.yml'):
                yaml.dump(content, temp_file)
            temp_file.flush()
            return temp_file.name

    def tearDown(self):
        os.remove(self.temp_sample_json_file)
        os.remove(self.temp_systematic_yaml_file)
        os.remove(self.temp_category_json_file)
        os.remove(self.temp_import_item_json_file)

    def test_workspace_creation(self):
        workspace = Workspace(**self.config)
        self.assertIsNotNone(workspace)
        self.assertEqual(workspace.workspace_name, 'combWS')
        self.assertEqual(workspace.modelconfig_name, 'ModelConfig')
        self.assertEqual(workspace.dataset_name, 'obsData')

    def test_category_creation(self):
        categories = [Category(**cat) if not isinstance(cat, str) else Category(**load_json_or_yaml_file(cat)) for cat in self.config['categories']]
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0].name, 'HM')
        self.assertEqual(categories[1].name, 'new_category')

        # Test details of the first category
        hm_category = categories[0]
        self.assertEqual(hm_category.type, 'shape')
        self.assertEqual(hm_category.lumi, 1.0)
        self.assertEqual(hm_category.data.filename, 'data_HM.txt')

        # Test details of the second category
        new_category = categories[1]
        self.assertEqual(new_category.type, 'shape')
        self.assertEqual(new_category.data.filename, 'data_new_category.txt')

    def test_sample_creation(self):
        category = self.config['categories'][0]
        samples = [Sample(**sample) if not isinstance(sample, str) else Sample(**load_json_or_yaml_file(sample)) for sample in category['samples']]
        self.assertEqual(len(samples), 2)
        self.assertEqual(samples[0].name, 'ggFHH_kl1p0')
        self.assertEqual(samples[1].name, 'sample_from_json')

        # Test details of the first sample
        sample_ggfhh = samples[0]
        self.assertEqual(sample_ggfhh.model.type, 'userdef')
        self.assertEqual(sample_ggfhh.model.items[0], 'mH[125.0]')
        self.assertEqual(sample_ggfhh.xsection, 1)

        # Test details of the second sample
        sample_json = samples[1]
        self.assertEqual(sample_json.model.type, 'userdef')
        self.assertEqual(sample_json.model.modelitem, "EXPR::bkgPdf_JSON('exp((@0-100)*@1/100)', :observable:,  BKG_p0_JSON[-1,-1000,1000])")
        self.assertEqual(sample_json.xsection, 1)

    def test_data_creation(self):
        category = self.config['categories'][0]
        data = ASCIIData(**category['data'])
        self.assertEqual(data.filename, 'data_HM.txt')
        self.assertEqual(data.observable, 'atlas_invMass_HM[105,160]')
        self.assertEqual(data.binning, 220)

    def test_systematic_creation(self):
        category = self.config['categories'][0]
        systematics = [Systematic(**syst) if not isinstance(syst, str) else Systematic(**load_json_or_yaml_file(syst)) for syst in category['systematics']]
        self.assertEqual(len(systematics), 2)
        self.assertEqual(systematics[0].name, 'ATLAS_lumi_run2')
        self.assertEqual(systematics[1].name, 'systematic_from_yaml')

        # Test details of the first systematic
        systematic_lumi = systematics[0]
        self.assertEqual(systematic_lumi.constr, 'logn')
        self.assertEqual(systematic_lumi.central_value, 1)
        self.assertEqual(systematic_lumi.magnitude, 0.00830)

        # Test details of the second systematic
        systematic_yaml = systematics[1]
        self.assertEqual(systematic_yaml.constr, 'logn')
        self.assertEqual(systematic_yaml.central_value, 1)
        self.assertEqual(systematic_yaml.magnitude, 0.009)

    def test_asimov_action_creation(self):
        asimov_actions = [AsimovAction(**action) for action in self.config['asimov_actions']]
        self.assertEqual(len(asimov_actions), 3)
        self.assertEqual(asimov_actions[0].name, 'setup')

        # Test details of the first Asimov action
        action_setup = asimov_actions[0]
        self.assertEqual(action_setup.setup, 'mu_HH=1,mu_HH_ggF=1,mu_HH_VBF=1')
        self.assertEqual(action_setup.action, '')

        # Test details of the second Asimov action
        action_poisnap = asimov_actions[1]
        self.assertEqual(action_poisnap.name, 'POISnap')
        self.assertEqual(action_poisnap.action, 'savesnapshot')
        self.assertEqual(action_poisnap.snapshot_poi, 'nominalPOI')

        # Test details of the third Asimov action
        action_npsnap = asimov_actions[2]
        self.assertEqual(action_npsnap.name, 'NPSnap')
        self.assertEqual(action_npsnap.setup, 'mu_HH=0')
        self.assertEqual(action_npsnap.action, 'fixsyst:fit:float:savesnapshot:nominalPOI')
        self.assertEqual(action_npsnap.snapshot_nuis, 'nominalNuis')
        self.assertEqual(action_npsnap.snapshot_glob, 'nominalGlobs')

    def test_literal_constraints(self):
        # Test Workspace model's literal constraints
        invalid_workspace_config = self.config.copy()
        invalid_workspace_config['data_storage_type'] = 'invalid_type'
        with self.assertRaises(ValidationError):
            Workspace(**invalid_workspace_config)
    
        valid_data_storage_types = ['vector', 'tree']
        for valid_type in valid_data_storage_types:
            valid_workspace_config = self.config.copy()
            valid_workspace_config['data_storage_type'] = valid_type
            workspace = Workspace(**valid_workspace_config)
            self.assertEqual(workspace.data_storage_type, valid_type)
    
        # Test Category model's literal constraints
        invalid_category_config = self.config['categories'][0].copy()
        invalid_category_config['type'] = 'invalid_type'
        with self.assertRaises(ValidationError):
            Category(**invalid_category_config)
    
        valid_category_types = ['shape', 'counting']
        for valid_type in valid_category_types:
            valid_category_config = self.config['categories'][0].copy()
            valid_category_config['type'] = valid_type
            category = Category(**valid_category_config)
            self.assertEqual(category.type, valid_type)
    
        # Test Systematic model's literal constraints
        invalid_systematic_config = self.config['categories'][0]['systematics'][0].copy()
        invalid_systematic_config['constr'] = 'invalid_constr'
        with self.assertRaises(ValidationError):
            Systematic(**invalid_systematic_config)
    
        valid_systematic_constrs = ['logn', 'asym']
        for valid_constr in valid_systematic_constrs:
            valid_systematic_config = self.config['categories'][0]['systematics'][0].copy()
            valid_systematic_config['constr'] = valid_constr
            systematic = Systematic(**valid_systematic_config)
            self.assertEqual(systematic.constr, valid_constr)

    def test_numeric_constraints(self):
        valid_counting_data = {
            'type': 'counting',
            'num_data': 100,
            'observable': 'dummyObs'
        }

        invalid_counting_data = {
            'type': 'counting',
            'num_data': -1,
            'observable': 'dummyObs'
        }

        CountingData(**valid_counting_data)

        with self.assertRaises(ValidationError):
            CountingData(**invalid_counting_data)

    def test_aliasing(self):
        alias_config = self.config.copy()
        alias_config['WorkspaceName'] = alias_config.pop('workspace_name')
        workspace = Workspace(**alias_config)
        self.assertEqual(workspace.workspace_name, 'combWS')


if __name__ == '__main__':
    unittest.main()