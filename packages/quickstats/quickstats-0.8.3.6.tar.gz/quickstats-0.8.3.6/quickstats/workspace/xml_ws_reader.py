from typing import Dict, Any, Optional, List, Union
import os

from quickstats import AbstractObject, PathManager
from quickstats.maths.numerics import is_float, pretty_value
from quickstats.utils.xml_tools import TXMLTree
from quickstats.utils.string_utils import split_str
from quickstats.workspace.settings import (
    DATA_SOURCE_COUNTING,
    DATA_SOURCE_ASCII,
    DATA_SOURCE_HISTOGRAM,
    DATA_SOURCE_NTUPLE,
    CATEGORY_KEYWORD,
    USERDEF_MODEL,
    EXTERNAL_MODEL,
    HISTOGRAM_MODEL,
    SELF_SYST_DOMAIN_KEYWORD,
    SampleFactorType
)
from quickstats.workspace.elements import Workspace

from .translation import (
    fetch_xml_node,
    get_xml_node_attrib,
    translate_special_keywords,
    translate_xml_node_attrib,
    get_object_name_type
)

class XMLWSReader(AbstractObject):

    def __init__(self, apply_fix: bool=False,
                 verbosity: Optional[Union[int, str]] = "INFO"):
        super().__init__(verbosity=verbosity)
        self.path_manager = PathManager()
        self.apply_fix = apply_fix

    def set_basedir(self, basedir: Optional[str] = None):
        self.path_manager.set_base_path(basedir)

    def get_relpath(self, filename: str) -> str:
        return self.path_manager.get_relpath(filename)
        
    def read_xml_file(self, filename: str, basedir: Optional[str] = None) -> Dict[str, Any]:
        self.set_basedir(basedir or os.path.dirname(filename))
        root_node = TXMLTree.load_as_dict(filename)
        self.stdout.debug(f'Reading root XML file "{filename}".')

        root_config = {
            'categories': [],
            'pois': [],
            'asimov_actions': [],
            'workspace_name': get_xml_node_attrib(root_node, 'WorkspaceName'),
            'modelconfig_name': get_xml_node_attrib(root_node, 'ModelConfigName'),
            'dataset_name': get_xml_node_attrib(root_node, 'DataName'),
            'blind': get_xml_node_attrib(root_node, 'Blind', required=False, default=False, dtype="bool"),
            'scale_lumi': get_xml_node_attrib(root_node, 'ScaleLumi', required=False, default=-1., dtype="float"),
            'integrator': get_xml_node_attrib(root_node, 'Integrator', required=False, default=""),
            'generate_binned_data': get_xml_node_attrib(root_node, 'GenBinnedData', required=False, default=True, dtype="bool"),
            'generate_hist_data': get_xml_node_attrib(root_node, 'GenHistData', required=False, default=False, dtype="bool"),
            'binned_fit': get_xml_node_attrib(root_node, 'BinnedFit', required=False, default=False, dtype="bool"),
        }

        class_decl_import_dir = get_xml_node_attrib(root_node, 'ClassDeclImportDir', required=False, default=None)
        if class_decl_import_dir:
            root_config['class_decl_import_dir'] = self.path_manager.get_relpath(class_decl_import_dir)

        class_impl_import_dir = get_xml_node_attrib(root_node, 'ClassImplImportDir', required=False, default=None)
        if class_impl_import_dir:
            root_config['class_impl_import_dir'] = self.path_manager.get_relpath(class_impl_import_dir)
        
        child_nodes = root_node['children']
        for child_node in child_nodes:
            tag = child_node['tag']
            if tag == "Input":
                self.read_category_node(child_node, root_config)
            elif tag == "POI":
                self.read_poi_node(child_node, root_config)
            elif tag == "Asimov":
                self.read_asimov_action_node(child_node, root_config)
            else:
                raise RuntimeError(f'Unknown XML item: {tag}')
        return root_config

    def read_poi_node(self, node: Dict[str, Any], root_config: Dict[str, Any]) -> None:
        root_config['pois'] = split_str(node['text'], sep=',', remove_empty=True)
        
    def read_asimov_action_node(self, node: Dict[str, Any], root_config: Dict[str, Any]) -> None:
        asimov_action_config = {
            'name': get_xml_node_attrib(node, 'Name'),
            'setup': get_xml_node_attrib(node, 'Setup'),
            'action': get_xml_node_attrib(node, 'Action'),
            'snapshot_nuis': get_xml_node_attrib(node, 'SnapshotNuis', required=False, default=None),
            'snapshot_glob': get_xml_node_attrib(node, 'SnapshotGlob', required=False, default=None),
            'snapshot_poi': get_xml_node_attrib(node, 'SnapshotPOI', required=False, default=None),
            'snapshot_all': get_xml_node_attrib(node, 'SnapshotAll', required=False, default=None),
            'data': get_xml_node_attrib(node, 'Data', required=False, default=None),
            'algorithm': get_xml_node_attrib(node, 'Algorithm', required=False, default='roostats')
        }
        root_config['asimov_actions'].append(asimov_action_config)
    
    def read_category_node(self, node: Dict[str, Any], root_config: Dict[str, Any]) -> None:
        filename = self.get_relpath(node['text'])
        if not os.path.exists(filename):
            raise FileNotFoundError(f'Category XML file "{filename}" does not exist.')
        self.stdout.debug(f'Reading category XML file "{filename}".')
        category_node = TXMLTree.load_as_dict(filename)
        category = category_node['attrib']["Name"]
        if category in root_config['categories']:
            raise RuntimeError(f'Duplicated category name: {category}')
        
        category_type = get_xml_node_attrib(category_node, 'Type').lower()
        luminosity = get_xml_node_attrib(category_node, "Lumi", required=False, default=1., dtype="float")
        category_config = {
            'name': category,
            'type': category_type,
            'data': {},
            'lumi': luminosity,
            'samples': [],
            'systematics': [],
            'correlate': [],
            'items': []
        }
        
        child_nodes = category_node['children']
        
        data_node = fetch_xml_node(child_nodes, "Data", "Channel", filename, allow_multiple=False, allow_missing=False)
        self.read_data_node(data_node, category_config)
        
        correlate_node = fetch_xml_node(child_nodes, "Correlate", "Channel", filename, allow_multiple=False, allow_missing=True)
        self.read_correlate_node(correlate_node, category_config)

        remaining_nodes = [node for node in child_nodes if node['tag'] not in ["Data", "Correlate"]]
        self.read_category_subnodes(remaining_nodes, category_config)
        root_config['categories'].append(category_config)

    def read_data_node(self, node: Dict[str, Any], category_config: Dict[str, Any]) -> None:
        category = category_config['name']
        self.stdout.debug(f'Reading data node under the category node "{category}".')
        data_config = {
            'observable': get_xml_node_attrib(node, "Observable"),
        }
        
        is_counting = category_config['type'] == DATA_SOURCE_COUNTING
        if is_counting:
            data_config.update({
                'type': str(DATA_SOURCE_COUNTING).lower(),
                'binning': 1,
                'num_data': get_xml_node_attrib(node, "NumData", dtype="int")
            })
        else:
            data_config.update({
                'binning': get_xml_node_attrib(node, "Binning", dtype="int"),
                'filename': get_xml_node_attrib(node, "InputFile"),
                'type': get_xml_node_attrib(node, "FileType", required=False, default=DATA_SOURCE_ASCII).lower()
            })

            if data_config['type'] == DATA_SOURCE_ASCII:
                data_config['has_weight'] = get_xml_node_attrib(node, "HasWeight", required=False, default=False, dtype="bool")
            elif data_config['type'] == DATA_SOURCE_HISTOGRAM:
                data_config['histname'] = get_xml_node_attrib(node, ["HistName", "HistoName"])
            elif data_config['type'] == DATA_SOURCE_NTUPLE:
                data_config.update({
                    'treename': get_xml_node_attrib(node, "TreeName"),
                    'varname': get_xml_node_attrib(node, "VarName"),
                    'selection': get_xml_node_attrib(node, "Cut", required=False, default=None),
                    'weightname': get_xml_node_attrib(node, "WeightName", required=False, default=None)
                })

        data_config.update({
            'inject_ghost': get_xml_node_attrib(node, "InjectGhost", required=False, default=False, dtype="bool"),
            'scale_data': get_xml_node_attrib(node, "ScaleData", required=False, default=1, dtype="float"),
            'blind_range': get_xml_node_attrib(node, "BlindRange", required=False, default=None, dtype="float_list")
        })
        category_config['data'] = data_config

    def read_correlate_node(self, node: Optional[Dict[str, Any]], category_config: Dict[str, Any]) -> None:
        if node:
            category = category_config['name']
            self.stdout.debug(f'Reading correlate node under the category node "{category}".')
            category_config['correlate'] = split_str(node['text'], sep=',', remove_empty=True)

    def read_category_subnodes(self, subnodes: List[Dict[str, Any]], category_config: Dict[str, Any]) -> None:
        for subnode in subnodes:
            tag = subnode['tag']
            if tag == "Item":
                self.read_item_node(subnode, category_config)
            elif tag == "Systematic":
                self.read_systematic_node(subnode, category_config)
            elif tag == "Sample":
                self.read_sample_node(subnode, category_config)
            elif tag in ["ImportItems", "IncludeSysts"]:
                self.read_category_import_node(subnode, category_config)
            else:
                raise RuntimeError(f"Unknown category item: {tag}")

    def read_category_import_node(self, node: Dict[str, Any], category_config: Dict[str, Any]) -> None:
        category = category_config['name']
        observable, _ = get_object_name_type(category_config['data']['observable'])
        filename = translate_xml_node_attrib(node, "FileName", category=category, observable=observable)
        filename = self.get_relpath(filename)
        if not os.path.exists(filename):
            raise FileNotFoundError(f'Import failed: XML file "{filename}" not found.')
        self.stdout.debug(f'Reading import XML file "{filename}".')
        root_node = TXMLTree.load_as_dict(filename)
        child_nodes = root_node['children']
        self.read_category_subnodes(child_nodes, category_config)      
                              
    def read_item_node(self, node: Dict[str, Any], category_config: Dict[str, Any]) -> None:
        name = get_xml_node_attrib(node, "Name")
        category_config['items'].append(name)

    def read_sample_node(self, node: Dict[str, Any], category_config: Dict[str, Any]) -> None:
        category = category_config['name']
        sample_config = {
            'name': get_xml_node_attrib(node, "Name"),
            'model': None,
            'import_syst': get_xml_node_attrib(node, "ImportSyst", required=False, default=SELF_SYST_DOMAIN_KEYWORD),
            'shared_pdf': get_xml_node_attrib(node, "SharePdf", required=False, default=None, dtype="float"),
            'multiply_lumi': get_xml_node_attrib(node, "MultiplyLumi", required=False, default=1, dtype="bool"),
            'norm_factors': [],
            'shape_factors': [],
            'systematics': [],
            'norm': get_xml_node_attrib(node, "Norm", required=False, default=None, dtype="float"),
            'xsection': get_xml_node_attrib(node, "XSection", required=False, default=None, dtype="float"),
            'selection_eff': get_xml_node_attrib(node, "SelectionEff", required=False, default=None, dtype="float"),
            'branching_ratio': get_xml_node_attrib(node, "BR", required=False, default=None, dtype="float"),
            'acceptance': get_xml_node_attrib(node, "Acceptance", required=False, default=None, dtype="float"),
            'correction': get_xml_node_attrib(node, "Correction", required=False, default=None, dtype="float")
        }
        sample_config['import_syst'] = split_str(sample_config['import_syst'], sep=',', remove_empty=True)
        is_counting = category_config['type'] == DATA_SOURCE_COUNTING
        resolvers = {
            'category': category,
            'observable': get_object_name_type(category_config['data']['observable'])[0]
        }
        # only translate it here when parsing the input filename to avoid altering the original expression
        resolvers['process'] = translate_special_keywords(sample_config['name'], **resolvers)
        model_filename = translate_xml_node_attrib(node, "InputFile", required=not is_counting,
                                                   default=None, **resolvers)
        if model_filename:
            model_filename = self.get_relpath(model_filename)
            if not os.path.exists(model_filename):
                raise FileNotFoundError(f'Model XML file "{model_filename}" not found.')
            self.stdout.debug(f'Reading model XML file "{model_filename}".')
            model_node = TXMLTree.load_as_dict(model_filename)
            self.read_model_node(model_node, sample_config)
        
        subnodes = node['children']
        self.read_sample_subnodes(subnodes, sample_config, **resolvers)
        category_config['samples'].append(sample_config)

    def read_sample_subnodes(self, subnodes: List[Dict[str, Any]], sample_config: Dict[str, Any],
                             **resolvers) -> None:
        for subnode in subnodes:
            tag = subnode['tag']
            if tag == "Systematic":
                method = self.read_systematic_node
            elif SampleFactorType.has_member(tag):
                method = self.read_sample_factor_node
            elif tag in ["ImportItems", "IncludeSysts"]:
                method = self.read_sample_import_node
            else:
                raise RuntimeError(f"Unknown sample item: {tag}")
            method(subnode, sample_config, **resolvers)


    def read_model_node(self, node: Dict[str, Any], sample_config: Dict[str, Any]) -> None:
        model_type = get_xml_node_attrib(node, "Type").lower()
        if model_type == USERDEF_MODEL:
            self.read_userdef_model_node(node, sample_config)
        elif model_type == EXTERNAL_MODEL:
            self.read_external_model_node(node, sample_config)
        elif model_type == HISTOGRAM_MODEL:
            self.read_histogram_model_node(node, sample_config)
        else:
            raise RuntimeError(f"Unknown model type: {model_type}. Available choices: {USERDEF_MODEL}, {EXTERNAL_MODEL}, {HISTOGRAM_MODEL}")

    def read_userdef_model_node(self, node: Dict[str, Any], sample_config: Dict[str, Any]) -> None:
        model_config = {
            'type': USERDEF_MODEL,
            'modelitem': None,
            'items': [],
            'cache_binning': get_xml_node_attrib(node, "CacheBinning", required=False, default=-1, dtype="int")
        }
        
        subnodes = node['children']
        for subnode in subnodes:
            tag = subnode['tag']
            if tag == "Item":
                model_config['items'].append(get_xml_node_attrib(subnode, "Name"))
            elif tag == "ModelItem":
                if model_config['modelitem'] is not None:
                    raise ValueError('Found multiple "ModelItem" nodes.')
                model_config['modelitem'] = get_xml_node_attrib(subnode, "Name")
            else:
                raise RuntimeError(f'Unknown user-defined model node "{tag}".')
        
        if model_config['modelitem'] is None:
            raise RuntimeError('Missing node "ModelItem" from model XML.')
        
        sample_config['model'] = model_config

    def read_external_model_node(self, node: Dict[str, Any], sample_config: Dict[str, Any]) -> None:
        model_config = {
            'type': EXTERNAL_MODEL,
            'filename': get_xml_node_attrib(node, "Input"),
            'workspace': get_xml_node_attrib(node, "WSName", required=False, default=None),
            'model': get_xml_node_attrib(node, "ModelName"),
            'observable': get_xml_node_attrib(node, "ObservableName"),
            'actions': []
        }

        subnodes = node['children']
        for subnode in subnodes:
            tag = subnode['tag']
            action = {}
            if tag == "Item":
                action = {'type': 'item', 'name': get_xml_node_attrib(subnode, "Name")}
            elif tag == "Fix":
                action = {'type': 'item', 'name': get_xml_node_attrib(subnode, "Name"), 'value': get_xml_node_attrib(subnode, "Value", required=False, default=None)}
            elif tag == "Rename":
                action = {'type': 'rename', 'old_name': get_xml_node_attrib(subnode, "OldName"), 'new_name': get_xml_node_attrib(subnode, "NewName")}
            elif tag == "ExtSyst":
                action = {
                    'type': 'ext_syst',
                    'nuis_name': get_xml_node_attrib(subnode, "NPName"),
                    'glob_name': get_xml_node_attrib(subnode, "GOName", required=False, default=None),
                    'constr_name': get_xml_node_attrib(subnode, "ConstrName", required=action['glob_name'] is not None, default=None)
                }
            else:
                raise RuntimeError(f'Unknown external model action node: {tag}')
            model_config['actions'].append(action)
        
        sample_config['model'] = model_config
        
    def read_histogram_model_node(self, node: Dict[str, Any], sample_config: Dict[str, Any]) -> None:
        model_config = {
            'type': HISTOGRAM_MODEL,
            'filename': get_xml_node_attrib(node, "Input"),
            'histname': get_xml_node_attrib(node, "ModelName"),
            'rebin': get_xml_node_attrib(node, "Rebin", required=False, default=-1, dtype="int")
        }
        sample_config['model'] = model_config

    def read_systematic_node(self, node: Dict[str, Any], parent_config: Dict[str, Any], **resolvers) -> None:
        syst_config = {
            'name': get_xml_node_attrib(node, "Name"),
            'constr': get_xml_node_attrib(node, "Constr"),
            'magnitude': get_xml_node_attrib(node, "Mag", dtype="str_list"),
            'whereto': get_xml_node_attrib(node, "WhereTo"),
            'central_value': get_xml_node_attrib(node, "CentralValue", dtype="float"),
            'process': get_xml_node_attrib(node, "Process", required=False, default=None),
            'apply_fix': self.apply_fix
        }

        if len(syst_config['magnitude']) == 1:
            syst_config['magnitude'] = syst_config['magnitude'][0]
        
        parent_config['systematics'].append(syst_config)

    def read_sample_factor_node(self, node: Dict[str, Any], sample_config: Dict[str, Any], **resolvers) -> None:
        factor_type = SampleFactorType.parse(node["tag"])
        sample_factor_config = {
            'name': get_xml_node_attrib(node, "Name"),
            'correlate': get_xml_node_attrib(node, "Correlate", required=False, default=0, dtype="int")
        }

        if factor_type == SampleFactorType.NormFactor:
            sample_config['norm_factors'].append(sample_factor_config)
        elif factor_type == SampleFactorType.ShapeFactor:
            sample_config['shape_factors'].append(sample_factor_config)

    def read_sample_import_node(self, node: Dict[str, Any], sample_config: Dict[str, Any], **resolvers) -> None:
        filename = get_translated_xml_node_attrib(node, "FileName", **resolvers)
        filename = self.get_relpath(filename)
        if not os.path.exists(filename):
            raise FileNotFoundError(f'Sample import XML file "{filename}" not found')
        self.stdout.debug(f'Reading sample import XML file "{filename}".')
        root_node = TXMLTree.load_as_dict(filename)
        subnodes = root_node['children']
        self.read_sample_subnodes(subnodes, sample_config, category=category)
