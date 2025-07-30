###############################################################################
### This is a reimplementation of workspaceCombiner library in python
### original author: Hongtao Yang
###############################################################################
import os
import re
import copy
import json
import time
import yaml
from typing import Optional, Union, List, Dict

import numpy as np

import ROOT

import quickstats
from quickstats import semistaticmethod, timer, AbstractObject, GeneralEnum
from quickstats.components import ExtendedModel
from quickstats.utils.xml_tools import TXMLTree
from quickstats.utils.common_utils import format_delimiter_enclosed_text, remove_list_duplicates
from quickstats.maths.numerics import is_float, pretty_value
from quickstats.components.basics import WSArgument
from quickstats.components.workspaces import XMLWSBase, WSObjectType, AsimovHandler
from quickstats.interface.root import RooAbsPdf
from quickstats.components.discrete_nuisance import DiscreteNuisance

class ModifierAction(GeneralEnum):
    NORMAL     = 0
    CONSTRAINT = 1
    
class XMLWSModifier(XMLWSBase):
    
    def __init__(self, source:Union[str, Dict], basedir:Optional[str]=None,
                 minimizer_config:Optional[Dict]=None,
                 unlimited_stack:bool=True,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(source=source, basedir=basedir,
                         unlimited_stack=unlimited_stack,
                         verbosity=verbosity)
        self.minimizer_config = minimizer_config
        self.load_extension()
        self.initialize(source=source)
        
    def initialize(self, source:Union[str, Dict]):
        self.config = None
        self.actions = {
            'map': [],
            'define': [],
            'redefine': [],
            'asimov': [],
            'constraint': [],
            'add_product_terms': {},
            'add_syst': []
        }
        self.actions['rename'] = {
            'workspace'   : {},
            'model_config': {},
            'dataset'     : {},
            'variable'    : {}
        }
        if isinstance(source, str):
            ext = os.path.splitext(source)[-1]
            if ext == ".xml":
                self.parse_config_xml(source)
            elif ext == ".json":
                self.parse_config_json(source)
            elif ext == ".yaml":
                self.parse_config_yaml(source)
            else:
                raise ValueError(f"unsupported file format: {ext}")
        elif isinstance(source, dict):
            self.parse_config_dict(source)
        else:
            raise ValueError(f"invalid input format: {source}")
        if len(self.actions['add_product_terms']) > 0:
            if (quickstats.root_version < (6, 26, 0)):
                raise RuntimeError("\"add product terms\" is only supported after ROOT 6.26")
            
    def parse_config_dict(self, source:Dict):
        source = copy.deepcopy(source)
        _actions = source.pop("actions", {})
        config = {
            "input_file"         : source.pop("input_file", "dummy"),
            "output_file"        : source.pop("output_file", "dummy"),
            "model_name"         : source.pop("model_name", None),
            "workspace_name"     : source.pop("workspace_name", None),
            "model_config_name"  : source.pop("model_config_name", None),
            "data_name"          : source.pop("data_name", "combData"),
            "poi_names"          : source.pop("poi_names", None),
            "snapshot_nuis"      : source.pop("snapshot_nuis", []),
            "snapshot_globs"     : source.pop("snapshot_globs", []),
            "snapshot_pois"      : source.pop("snapshot_pois", []),
            "snapshot_all"       : source.pop("snapshot_all", []),
            "snapshot_list"      : source.pop("snapshot_list", []),
            "dataset_list"       : source.pop("dataset_list", None),
            "fix_parameters"     : source.pop("fix_parameters", None),
            "profile_parameters" : source.pop("profile_parameters", None),
            "set_parameters"     : source.pop("set_parameters", None),
            "strict"             : source.pop("strict", True)
        }
        if source:
            unknown_attributes = list(source)
            self.stdout.warning(f"The following unrecognized configuration attribute(s) will be ignored: "
                                f"{', '.join(unknown_attributes)}")
        actions = {
            "map"        : _actions.pop("map", []),
            "define"     : _actions.pop("define", []),
            "redefine"   : _actions.pop("redefine", []),
            "asimov"     : _actions.pop("asimov", []),
            "constraint" : [],
            "add_product_terms": _actions.pop("add_product_terms", {}),
            'add_syst': _actions.pop("add_syst", [])
        }
        
        # handle constraint definition
        constraints = _actions.pop("constraint", [])
        for constraint_dict in constraints:
            constraint_node = {
                'attrib': constraint_dict
            }
            expr = self._get_node_attrib(constraint_node, "Name", required=True)
            constr_expr = self.parse_constr_expression(expr, constraint_node)
            if constr_expr['file'] is None:
                actions['define'].append(expr)
            actions['constraint'].append(constr_expr)

        _rename = _actions.pop("rename", {})
        rename = {
            "workspace"    : _rename.pop("workspace", {}),
            "model_config" : _rename.pop("model_config", {}),
            "dataset"      : _rename.pop("dataset", {}),
            "variable"     : _rename.pop("variable", {})
        }
        actions["rename"] = rename
        if _actions:
            unknown_attributes = list(_actions)
            self.stdout.warning(f"Unknown action type: {', '.join(unknown_attributes)}. "
                                "Ignoring...")
        if _rename:
            unknown_attributes = list(_rename)
            self.stdout.warning(f"Unknown object type in rename: {', '.join(unknown_attributes)}. "
                                "Ignoring...")
        
        self.config = config
        self.actions = actions
    
    def parse_config_json(self, filename:str):
        with open(filename, 'r') as f:
            source = json.load(f)
        self.parse_config_dict(source)
        
    def parse_config_yaml(self, filename:str):
        with open(filename, 'r') as f:
            source = yaml.safe_load(f)
        self.parse_config_dict(source)        
    
    def parse_config_xml(self, filename:str):
        root = TXMLTree.load_as_dict(filename)
        config = {
            'input_file'         : self._get_node_attrib(root, "InFile", required=True),
            'output_file'        : self._get_node_attrib(root, "OutFile", required=True),
            'model_name'         : self._get_node_attrib(root, "ModelName", required=False),
            'workspace_name'     : self._get_node_attrib(root, "WorkspaceName", required=False),
            'model_config_name'  : self._get_node_attrib(root, "ModelConfigName", required=False),
            'data_name'          : self._get_node_attrib(root, "DataName", required=False, default="combData"),
            'poi_names'          : self._get_node_attrib(root, "POINames", required=False, dtype="str_list"),
            'snapshot_nuis'      : self._get_node_attrib(root, "SnapshotNP", required=False, default=[], dtype="str_list"),
            'snapshot_globs'     : self._get_node_attrib(root, "SnapshotGO", required=False, default=[], dtype="str_list"),
            'snapshot_pois'      : self._get_node_attrib(root, "SnapshotPOI", required=False, default=[], dtype="str_list"),
            'snapshot_all'       : self._get_node_attrib(root, "SnapshotAll", required=False, default=[], dtype="str_list"),
            'snapshot_list'      : self._get_node_attrib(root, "SnapshotList", required=False, default=[], dtype="str_list"),
            'dataset_list'       : self._get_node_attrib(root, "DatasetList", required=False, default=None, dtype="str_list"),
            "fix_parameters"     : self._get_node_attrib(root, "FixParameters", required=False, default=None),
            "profile_parameters" : self._get_node_attrib(root, "ProfileParameters", required=False, default=None),
            "set_parameters"     : self._get_node_attrib(root, "SetParameters", required=False, default=None),
            'strict'             : self._get_node_attrib(root, "Strict", required=False, default="true", dtype="bool")
        }
        # for compatibility with older version of workspaceCombiner
        if config['workspace_name'] == "dummy":
            config['workspace_name'] = None
        if config['model_config_name'] == "dummy":
            config['model_config_name'] = None
        self.config = config
        
        # parse child nodes
        nodes = root['children']
        for node in nodes:
            self.parse_action_node(node)
            
    def parse_action_node(self, node:Dict):
        tag = node['tag']
        if tag == "Item":
            expr        = self._get_node_attrib(node, "Name", required=True)
            action_type = self._get_node_attrib(node, "Type", required=False,
                                                default=ModifierAction.NORMAL)
            action_type = ModifierAction.parse(action_type)
            if action_type == ModifierAction.CONSTRAINT:
                constr_expr = self.parse_constr_expression(expr, node)
                # define pdf that is not imported externally
                if constr_expr['file'] is None:
                    self.actions['define'].append(expr)
                self.actions['constraint'].append(constr_expr)
            else:
                self.actions['define'].append(expr)
        elif tag == "Map":
            expr = self._get_node_attrib(node, "Name", required=True)
            self.actions['map'].append(expr)
        elif tag == "Asimov":
            definitions = node['attrib']
            self.actions['asimov'].append(definitions)
        elif tag == "Rename":
            subnodes = node['child']
            for subnode in subnodes:
                self.parse_rename_node(subnode)
        elif tag == "AddProductTerm":
            name = self._get_node_attrib(node, "Name", required=True)
            extra_terms = self._get_node_attrib(node, "Terms", required=True, dtype="str_list")
            if name in self.actions['add_product_terms']:
                raise ValueError("AddProductTerm action defined multiple times for the variable "
                                 f"\"{name}\"")
            self.actions['add_product_terms'][name] = extra_terms
        elif tag == "AddNPSet":
            nuis_names = self._get_node_attrib(node, "Name", required=True, dtype="str_list")
            self.actions['add_syst'] += nuis_names
        else:
            raise RuntimeError(f"unknown item `{tag}`")
    
    def parse_rename_node(self, node:Dict):
        tag = node['tag']
        new_name = self._get_node_attrib(node, "New", required=True)
        if tag == 'Workspace':
            old_name_required = False
            target = 'workspace'
        elif tag == 'ModelConfig':
            old_name_required = False
            target = 'model_config'
        elif tag == 'Dataset':
            old_name_required = True
            target = 'dataset'
        elif tag == 'Variable':
            old_name_required = True
            target = 'variable'
        else:
            raise RuntimeError(f"unknown item `{tag}`")
        old_name = self._get_node_attrib(node, "Old", required=old_name_required)
        if old_name in self.actions['rename'][target]:
            raise RuntimeError(f"the {target.replace('_','')} \"{old_name}\" is renamed more than once")
        self.actions['rename'][target][old_name] = new_name
    
    def parse_constr_expression(self, expr:str, node:Dict):
        pdf_name, _ = self._get_object_name_and_type_from_expr(expr)
        nuis_name = self._get_node_attrib(node, "NP", required=False, default=[], dtype="str_list")
        glob_name = self._get_node_attrib(node, "GO", required=False, default=[], dtype="str_list")
        filename  = self._get_node_attrib(node, "FileName", required=False)
        independent  = self._get_node_attrib(node, "Independent", required=False, default="false", dtype="bool")
        result = {
            'pdf': pdf_name,
            'nuis': nuis_name,
            'glob': glob_name,
            'file': filename,
            'independent': independent
        }
        return result
    
    def sanity_check(self):
        if self.config is None:
            raise RuntimeError("core configuration not set")
        if len(self.actions['rename']['workspace']) > 1:
            raise RuntimeError("workspace is renamed more than once")
        if len(self.actions['rename']['model_config']) > 1:
            raise RuntimeError("model config is renamed more than once")
        renamed_variables = self._get_shallow_renamed_variables()
        param_components = []
        redefine_actions = []
        for expr in self.actions['redefine']:
            obj_name, obj_type = self._get_object_name_and_type_from_expr(expr)
            if obj_type == WSObjectType.CONSTRAINT:
                raise RuntimeError(f'can not redefine with a constraint expression: {expr} ; '
                                   'please use the "constraint" action instead')
            elif obj_type == WSObjectType.DEFINED:
                raise RuntimeError(f'vacuous redefine expression: {expr}')
            elif obj_type not in [WSObjectType.FUNCTION, WSObjectType.VARIABLE]:
                raise RuntimeError(f'unexpected object type in redefine expression: {expr} ; '
                                   'expression should either define a variable or a function')
            if obj_name in renamed_variables:
                new_variable = self.actions['rename']['variable'][obj_name]
                if obj_type == WSObjectType.FUNCTION:
                    raise RuntimeError('can not redefine function that will be renamed later '
                                       f'(causing a dangling function): {expr} ; '
                                       'Please use define instead.')
                assert obj_type == WSObjectType.VARIABLE
                result = re.search(r"\[(.+)\]", expr)
                if not result:
                    raise RuntimeError(f"invalid variable expression {expr}")
                self.stdout.warning('Trying to redefine a variable that will be renamed later: '
                                    f'{expr}. It will be reinterpreted as setting the attributes '
                                    f'of the renamed variable ({new_variable}) instead.')
                tokens = result.group(1).split(",")
                param_component = f'{new_variable}={"_".join(tokens)}'
                param_components.append(param_component)
                continue
            redefine_actions.append(expr)
        self.actions['redefine'] = redefine_actions
        if param_components:
            set_param_expr = ",".join(param_components)
            if self.config['set_parameters'] is None:
                self.config['set_parameters'] = set_param_expr
            else:
                self.config['set_parameters'] = f"{self.config['set_parameters']},{set_param_expr}"
        redefined_variables = self._get_redefined_variables()
        redefined_variables, counts = np.unique(redefined_variables, return_counts=True)
        duplicated_redefine_vars = redefined_variables[counts > 1]
        if len(duplicated_redefine_vars) > 0:
            raise RuntimeError("the following variables are redefined multiple times: " + \
                             ", ".join(duplicated_redefine_vars))
    
    def _get_shallow_renamed_variables(self):
        if 'variable' not in self.actions['rename']:
            return []
        return list(self.actions['rename']['variable'])
                    
    def _get_redefined_variables(self):
        redefined_variables = []
        for expr in self.actions['redefine']:
            varname, _ = self._get_object_name_and_type_from_expr(expr)
            redefined_variables.append(varname)
        return redefined_variables
    
    def correct_formula_once(self,formulaVar):
        formula = ROOT.RooFormulaVarExt.getFormulaStr(formulaVar)
        actual_vars = ROOT.RooFormulaVarExt.getDependents(formulaVar)

        # In case of something strange
        if f'@{len(actual_vars)}' in formula or f'x[{len(actual_vars)}]' in formula:
            return formula, False, actual_vars

        formula_bak = formula
        indexed_vars = [(i, var) for i, var in enumerate(actual_vars)]
        sorted_vars = sorted(indexed_vars, key=lambda item: len(item[1].GetName()), reverse=True)
        for original_index, var in sorted_vars:
            formula = formula.replace(var.GetName(), f'@{original_index}')
        formula = re.sub(r'x\[(\d+)\]', r'@\1', formula)
        
        # then remove the unused dependents
        used_indices = re.findall(r"@(\d+)", formula)
        used_indices = sorted(map(int, set(used_indices)))
        if len(used_indices) < len(indexed_vars):
            actual_vars_new = ROOT.RooArgList()
            for i in used_indices:
                actual_vars_new.add(indexed_vars[i][1])
            old_to_new = {old_idx: new_idx for new_idx, old_idx in enumerate(used_indices)}
            formula_new = re.sub(r"@(\d+)", lambda match: f"@{old_to_new[int(match.group(1))]}", formula)
        else:
            formula_new = formula
            actual_vars_new = actual_vars

        update_formula = (formula_new!=formula_bak)
        return formula_new, update_formula, actual_vars_new
    
    def correct_formula(self, ws_orig, ws_tmp, rename_map):
        old_var_expr = ",".join(list(rename_map.keys()))
        new_var_expr = ",".join(list(rename_map.values()))
        tested_vars = []
        if quickstats.root_version >=  (6, 30, 0):
            for component in ws_orig.components():
                if isinstance(component, ROOT.RooFormulaVar):
                    formula, update_formula, actual_vars = self.correct_formula_once(component)
                    # Sometimes the input variables will be a function of other variables
                    for actual_var in actual_vars:
                        if actual_var in tested_vars: continue
                        tested_vars.append(actual_var)
                        if isinstance(actual_var, ROOT.RooAddition):
                            component_list = actual_var.getComponents()
                            add_iter = component_list.createIterator()
                            add_component = add_iter.Next()
                            while add_component:
                                if isinstance(add_component, ROOT.RooFormulaVar):
                                    add_formula, add_update_formula, add_actual_vars = self.correct_formula_once(add_component)
                                    if add_update_formula:
                                        add_new_formula_var = ROOT.RooFormulaVar(add_component.GetName(), add_component.GetTitle(), add_formula, add_actual_vars)
                                        getattr(ws_tmp, "import")(add_new_formula_var, ROOT.RooFit.RenameVariable(old_var_expr, new_var_expr), ROOT.RooFit.RecycleConflictNodes())
                                add_component = add_iter.Next()
                    
                    # Update the formula only if there is any change
                    if update_formula:
                        new_formula_var = ROOT.RooFormulaVar(component.GetName(), component.GetTitle(), formula, actual_vars)
                        getattr(ws_tmp, "import")(new_formula_var, ROOT.RooFit.RenameVariable(old_var_expr, new_var_expr), ROOT.RooFit.RecycleConflictNodes())
        else:
            iter = ws_orig.componentIterator()
            obj = iter.Next()
            while obj:
                if isinstance(obj, ROOT.RooFormulaVar):
                    formula, update_formula, actual_vars = self.correct_formula_once(obj)
                    # Sometimes the input variables will be a function of other variables
                    for actual_var in actual_vars:
                        if actual_var in tested_vars: continue
                        tested_vars.append(actual_var)
                        if isinstance(actual_var, ROOT.RooAddition):
                            component_list = actual_var.getComponents()
                            add_iter = component_list.createIterator()
                            add_component = add_iter.Next()
                            while add_component:
                                if isinstance(add_component, ROOT.RooFormulaVar):
                                    add_formula, add_update_formula, add_actual_vars = self.correct_formula_once(add_component)
                                    if add_update_formula:
                                        add_new_formula_var = ROOT.RooFormulaVar(add_component.GetName(), add_component.GetTitle(), add_formula, add_actual_vars)
                                        getattr(ws_tmp, "import")(add_new_formula_var, ROOT.RooFit.RenameVariable(old_var_expr, new_var_expr), ROOT.RooFit.RecycleConflictNodes())
                                add_component = add_iter.Next()
                    
                    # Update the formula only if there is any change
                    if update_formula:
                        new_formula_var = ROOT.RooFormulaVar(obj.GetName(), obj.GetTitle(), formula, actual_vars)
                        getattr(ws_tmp, "import")(new_formula_var, ROOT.RooFit.RenameVariable(old_var_expr, new_var_expr), ROOT.RooFit.RecycleConflictNodes())
                obj = iter.Next()
    
    def create_modified_workspace(self, infile:Optional[str]=None, outfile:Optional[str]=None, import_class_code:bool=True,
                                  recreate:bool=True, float_all_nuis:bool=False, remove_fixed_nuis:bool=False):

        with timer() as t:
            self.sanity_check()
            # override path to the input workspace
            if infile is None:
                infile = self.config['input_file']
            # override path to the output workspace
            if outfile is None:
                outfile = self.config['output_file']
            ws_name  = self.config['workspace_name']
            mc_name  = self.config['model_config_name']
            self.stdout.info(f"Begin modification of the workspace \"{infile}\".")
            model    = ExtendedModel(infile, ws_name=ws_name, mc_name=mc_name,
                                     data_name=None, verbosity="WARNING")
            ws_orig  = model.workspace
            ws_name  = ws_orig.GetName()
            mc_orig  = model.model_config
            # if model config name is specified, save only that one
            if mc_name is None:
                mc_map = model.model_configs
            else:
                mc_map = {mc_name: mc_orig}

            # create temporary workspace
            ws_tmp = ROOT.RooWorkspace(ws_name)

            title_str = format_delimiter_enclosed_text("Step 1: Redefine objects", "-")
            self.stdout.info(title_str, bare=True)
            flag = self.redefine_objects(ws_orig, ws_tmp)
            # nothing is done
            if not flag:
                self.stdout.info("No objects are redefined.")

            title_str = format_delimiter_enclosed_text("Step 2: Create new objects", "-")
            self.stdout.info(title_str, bare=True)
            flag = self.implement_external_pdfs(ws_tmp)
            flag |= self.implement_objects(ws_tmp)
            # nothing is done
            if not flag:
                self.stdout.info("No new objects are defined.")

            dataset_list = self.config['dataset_list']
            # need to import datasets first so the variables are also imported into the workspace
            self.import_datasets(ws_orig, ws_tmp, dataset_list)

            title_str = format_delimiter_enclosed_text("Step 3: Rename variables", "-")
            self.stdout.info(title_str, bare=True)
            rename_map = self.get_rename_map(ws_orig, ws_tmp)
            actual_rename_map = self.get_actual_rename_map(rename_map, ws_orig, ws_tmp)

            # In case the variable exist in RooFormulaVar
            self.correct_formula(ws_orig, ws_tmp, rename_map)
            
            for mc in mc_map.values():
                self.rename_variables(mc, ws_tmp, rename_map)
                
            if not rename_map:
                self.stdout.info("No variables are renamed.")

            title_str = format_delimiter_enclosed_text("Step 4: Making output workspace", "-")
            self.stdout.info(title_str, bare=True)

            # create final workspace
            if len(self.actions['constraint']) > 0:
                ws_final = ROOT.RooWorkspace(ws_name)
                for mc in mc_map.values():
                    sim_pdf = self.remake_simultaneous_pdf(mc, ws_tmp)
                    self.import_object(ws_final, sim_pdf)
                self.import_datasets(ws_orig, ws_final, dataset_list)
            else:
                ws_final = ws_tmp        

            # post processing pdfs, functions and variables
            self.post_process_workspace(ws_final)
            
            strict = self.config['strict'] and (len(mc_map) == 1)
            mc_final_map = {}
            for mc in mc_map.values():
                mc_final = self.create_model_config(mc, ws_final, actual_rename_map,
                                                    float_all_nuis=float_all_nuis,
                                                    remove_fixed_nuis=remove_fixed_nuis,
                                                    strict=strict)
                mc_final_map[mc.GetName()] = mc_final
            self.rename_objects(ws_final, mc_final_map)
            for mc_final in mc_final_map.values():
                self.import_object(ws_final, mc_final, silent=False)
                
            if import_class_code:
                self.import_class_code(ws_final)

            if (
                len(mc_final_map) > 1
                and mc_name is None
                and (
                    self.config['snapshot_nuis']
                    or self.config['snapshot_globs']
                    or self.config['snapshot_pois']
                )
            ):
                self.stdout.warning(
                    'Attempting to create nuisnace parameter / global observable / POI snapshots '
                    'from workspace with multiple model configs. The definition of objects '
                    'from the first model config will be used.'
                )

            if mc_name is None:
                mc_final = next(iter(mc_final_map.values()))
            else:
                mc_final = mc_final_map[mc_name]
                    
            self.create_snapshots(ws_orig, mc_orig, ws_final, mc_final, rename_map)
            
            self.create_generic_objects(ws_orig, ws_final, rename_map)

            self.generate_asimov(ws_final)

            self.setup_parameters(ws_final)

            outdir  = os.path.dirname(outfile)
            if outdir and (not os.path.exists(outdir)):
                os.makedirs(outdir)

            ws_final.writeToFile(outfile, recreate)
            self.stdout.info(f'Saved output workspace as "{outfile}".')
        self.stdout.info(f"Total time taken: {t.interval:.3f}s")
    
    def post_process_workspace(self, ws:ROOT.RooWorkspace):
        self.add_product_terms(ws)
    
    def add_product_terms(self, ws:ROOT.RooWorkspace):
        for target_name, extra_terms in self.actions["add_product_terms"].items():
            prod_var = self.get_workspace_arg(ws, target_name, strict=True)
            if not isinstance(prod_var, ROOT.RooProduct):
                class_name = prod_var.ClassName()
                raise RuntimeError(f"failed to add product term to the variable \"{target_name}\": "
                                   f"expect a RooProduct instance but {class_name} received")
            for extra_term in extra_terms:
                member_var = self.get_workspace_arg(ws, extra_term, strict=True)
                prod_var.addTerm(member_var)
            self.stdout.info(f"The following product terms are added to the variable {target_name}: "
                             f"{', '.join(extra_terms)}")
    
    def setup_parameters(self, ws:ROOT.RooWorkspace):
        data_name = self.config['data_name']
        model = ExtendedModel(ws, data_name=data_name, verbosity="WARNING")
        model.stdout.verbosity = self.stdout.verbosity
        if self.config["fix_parameters"] is not None:
            model.fix_parameters(self.config["fix_parameters"])
        if self.config["profile_parameters"] is not None:
            model.profile_parameters(self.config["profile_parameters"])
        if self.config["set_parameters"] is not None:
            model.set_parameters(self.config["set_parameters"])

    def generate_asimov(self, ws:ROOT.RooWorkspace):
        n_asimov = len(self.actions['asimov'])
        if n_asimov == 0:
            return None
        data_name = self.config['data_name']
        asimov_handler = AsimovHandler(ws, data_name=data_name,
                                       minimizer_config=self.minimizer_config)
        for attributes in self.actions['asimov']:
            asimov_handler.generate_single_asimov(attributes)
            
    def copy_variable(self, old_variable:ROOT.RooRealVar, new_variable:ROOT.RooRealVar):
        copied_variable = new_variable.Clone()
        copied_variable.setVal(old_variable.getVal())
        copied_variable.setRange(old_variable.getMin(), old_variable.getMax())
        copied_variable.setConstant(old_variable.isConstant())
        copied_variable.setError(old_variable.getError())
        return copied_variable
            
    def copy_variables(self, variables:ROOT.RooArgSet, new_ws:ROOT.RooWorkspace, rename_map:Optional[Dict]=None):
        if rename_map is None:
            rename_map = {}
        renamed_variables_old = ROOT.RooArgSet()
        renamed_variables_new = ROOT.RooArgSet()
        for variable in variables:
            name = variable.GetName()
            if name in rename_map:
                new_name = rename_map[name]
                # note only renaming of RooRealVar instance will be considered
                new_variable = new_ws.var(new_name)
                if not new_variable:
                    self.stdout.warning(f'The argset variable "{name}" not found in the new workspace. Skipped.')
                # avoid modifying the original value
                copied_variable = self.copy_variable(variable, new_variable)
                renamed_variables_old.add(variable)
                renamed_variables_new.add(copied_variable)
        variables.remove(renamed_variables_old)
        variables.add(renamed_variables_new)
                               
    def copy_snapshot_variables(self, old_ws:ROOT.RooWorkspace, old_mc:ROOT.RooStats.ModelConfig,
                                new_ws:ROOT.RooWorkspace, new_mc:ROOT.RooStats.ModelConfig,
                                snapshot_name:str, variable_type:Optional[Union[WSArgument, str]]=None,
                                rename_map:Optional[Dict]=None):
        snapshot = old_ws.getSnapshot(snapshot_name)
        if not snapshot:
            self.stdout.warning(f"Snapshot {snapshot_name} not found in the original workspace")
        # get variables from orginal workspace, make sure to make a clone
        if variable_type is None:
            variables = snapshot.Clone()
        else:
            target_variables = self.get_variables(old_mc, variable_type)
            variables = snapshot.Clone().selectCommon(target_variables)
        if rename_map is None:
            rename_map = {}
        self.stdout.info(f"Copying snapshot \"{snapshot_name}\" from the original workspace "
                         "to the new workspace")
        self.copy_variables(variables, new_ws, rename_map)
        # important: the third argument decide whether to take values from the argset or from the workspace
        new_ws.saveSnapshot(snapshot_name, variables, True)
        
    def get_variables(self, mc:ROOT.RooStats.ModelConfig, variable_type:Union[WSArgument, str]):
        _variable_type = WSArgument.parse(variable_type)
        if _variable_type == WSArgument.NUISANCE_PARAMETER:
            variables = mc.GetNuisanceParameters()
        elif _variable_type == WSArgument.GLOBAL_OBSERVABLE:
            variables = mc.GetGlobalObservables()
        elif _variable_type == WSArgument.POI:
            variables = mc.GetParametersOfInterest()
        elif _variable_type == WSArgument.CORE:
            variables = ROOT.RooArgSet()
            variables.add(mc.GetNuisanceParameters())
            variables.add(mc.GetGlobalObservables())
            variables.add(mc.GetParametersOfInterest())
        else:
            raise RuntimeError(f"unsupported variable type: {variable_type}")
        return variables

    def create_snapshots(self, old_ws:ROOT.RooWorkspace, old_mc:ROOT.RooStats.ModelConfig,
                         new_ws:ROOT.RooWorkspace, new_mc:ROOT.RooStats.ModelConfig,
                         rename_map:Optional[Dict]=None):
        # nuisance parameter snapshots
        nuis_snapshot_names = self.config['snapshot_nuis']
        for nuis_snapshot_name in nuis_snapshot_names:
            self.copy_snapshot_variables(old_ws, old_mc, new_ws, new_mc, nuis_snapshot_name,
                                         WSArgument.NUISANCE_PARAMETER, rename_map)
        # global observable snapshots                  
        globs_snapshot_names = self.config['snapshot_globs']
        for globs_snapshot_name in globs_snapshot_names:
            self.copy_snapshot_variables(old_ws, old_mc, new_ws, new_mc, globs_snapshot_name,
                                         WSArgument.GLOBAL_OBSERVABLE, rename_map)
        # poi snapshots 
        pois_snapshot_names = self.config['snapshot_pois']
        for pois_snapshot_name in pois_snapshot_names:
            self.copy_snapshot_variables(old_ws, old_mc, new_ws, new_mc, pois_snapshot_name,
                                         WSArgument.POI, rename_map)
        # nuisance parameter + global observable + poi snapshots 
        vars_snapshot_names = self.config['snapshot_all']
        for vars_snapshot_name in vars_snapshot_names:
            self.copy_snapshot_variables(old_ws, old_mc, new_ws, new_mc, vars_snapshot_name,
                                         WSArgument.CORE, rename_map)
        # any variables
        vars_snapshot_names = self.config['snapshot_list']
        for vars_snapshot_name in vars_snapshot_names:
            self.copy_snapshot_variables(old_ws, old_mc, new_ws, new_mc, vars_snapshot_name,
                                         None, rename_map)
            
    def create_generic_objects(self, old_ws:ROOT.RooWorkspace, new_ws:ROOT.RooWorkspace,
                               rename_map:Optional[Dict]=None):
        generic_objects = old_ws.allGenericObjects()
        # only create objects of type RooArgSet
        generic_objects = [obj for obj in generic_objects if isinstance(obj, ROOT.RooArgSet)]
        if rename_map is None:
            rename_map = {}
        # Speicial handling for CMS DiscreteNuisance as it doesn't have a name
        get_disc_set = old_ws.genobj(DiscreteNuisance().config['disc_set_keyword'])
        if get_disc_set:
            self.stdout.info(f"Adding name for generic object {DiscreteNuisance().config['disc_set_keyword']}")
            get_disc_set.setName(DiscreteNuisance().config['disc_set_keyword'])
        for generic_object in generic_objects:
            name = generic_object.GetName()
            if not name:
                self.stdout.warning('Found generic object without name. '
                                    'The object will not be imported to the new workspace')
                continue
            self.stdout.info(f'Copying generic object "{name}" from the original workspace to the new workspace')
            if all(isinstance(obj, ROOT.RooRealVar) for obj in generic_object):
                argset = generic_object.Clone()
                self.copy_variables(argset, new_ws, rename_map)
            else:
                argset = self.recreate_argset(generic_object, new_ws, rename_map)
            new_ws.Import(argset, name, True)
            
            
    def recreate_argset(self, argset:ROOT.RooArgSet, ws:ROOT.RooWorkspace, rename_map:Optional[Dict]=None):
        argset_name = argset.GetName()
        new_argset = ROOT.RooArgSet()
        new_argset.setName(argset_name)
        for arg in argset:
            name = arg.GetName()
            name = rename_map.get(name, name)
            new_arg = ws.obj(name)
            if not new_arg:
                raise RuntimeError(f'WARNING: The variable "{name}" from the argset "{argset_name}" '
                                   f'not found in the new workspace.')
            if isinstance(new_arg, ROOT.RooRealVar):
                copied_arg = self.copy_variable(arg, new_arg)
                new_argset.add(copied_arg)
            else:
                new_argset.add(new_arg)
        return new_argset
 
    def create_model_config(
        self,
        old_mc: ROOT.RooStats.ModelConfig,
        new_ws: ROOT.RooWorkspace,
        rename_map: Optional[Dict] = None,
        float_all_nuis: bool = False,
        remove_fixed_nuis: bool = False,
        strict: bool = True
    ):
        if rename_map is None:
            rename_map = {}
        
        # start preparing model config
        mc_name = old_mc.GetName()
        mc = ROOT.RooStats.ModelConfig(mc_name, new_ws)

        # set pdf
        pdf_name = old_mc.GetPdf().GetName()
        pdf = new_ws.pdf(pdf_name)        
        mc.SetPdf(pdf)
        
        # set POIs
        self.stdout.debug("List of POIs in the new parameterization:")
        pois = ROOT.RooArgSet()
        poi_names = self.config['poi_names']
        # use old poi names if not specified
        if poi_names is None:
            poi_names = [i.GetName() for i in old_mc.GetParametersOfInterest()]
            poi_names = [rename_map.get(poi_name, poi_name) for poi_name in poi_names]
        for poi_name in poi_names:
            poi = self._get_relevant_variable(poi_name, new_ws, pdf)
            if not poi:
                if strict:
                    raise RuntimeError(
                        f"POI {poi_name} does not exist (model config = {mc_name})"
                    )
                else:
                    self.stdout.warning(
                        f"POI {poi_name} does not exist (model config = {mc_name}). Skipping."
                    )
                    continue
            pois.add(poi)
            self.stdout.info(f"Added POI \"{poi_name}\".")
        mc.SetParametersOfInterest(pois)
        
        # nuisance parameters and global observables from original workspace
        old_nuis = old_mc.GetNuisanceParameters()
        if old_nuis:
            nuis_names = [nuis.GetName() for nuis in old_nuis]
            nuis_names = [rename_map.get(nuis, nuis) for nuis in nuis_names]
        else:
            nuis_names = []
        old_globs = old_mc.GetGlobalObservables()
        if old_globs:
            glob_names = [glob.GetName() for glob in old_globs]
            glob_names = [rename_map.get(glob, glob) for glob in glob_names]
        else:
            glob_names = []
            
        # newly defined nuisance_parameters and global observables
        additional_constraints = self.actions['constraint']
        new_nuis = []
        for item in additional_constraints:
            new_nuis   += item['nuis']
            nuis_names += item['nuis']
            glob_names += item['glob']
            
        # additional (unconstrained) nuisance parameters
        extra_nuis = self.actions['add_syst']
        nuis_names += extra_nuis
        
        if len(new_nuis) > 0:
            self.stdout.info("The following newly defined nuisance parameter(s) will be added to ModelConfig")
            for nuis_name in new_nuis:
                self.stdout.info(f"    {nuis_name}", bare=True)
        if len(extra_nuis) > 0:
            self.stdout.info("The following additional nuisance parameter(s) will be added to ModelConfig")
            for nuis_name in extra_nuis:
                self.stdout.info(f"    {nuis_name}", bare=True)
        
        nuis_names = remove_list_duplicates(nuis_names)
        # set nuisance parameters
        nuisance_parameters = ROOT.RooArgSet()
        for nuis_name in nuis_names:
            nuis = self._get_relevant_variable(nuis_name, new_ws, pdf)
            if not nuis:
                self.stdout.warning(f"The nuisance parameter {nuis_name} no longer exists in "
                                    "the new workspace. It will be removed from the new ModelConfig.")
                continue
            if nuis.isConstant() and nuis not in pois:
                if float_all_nuis:
                    self.stdout.warning(f"The nuisace parameter {nuis_name} is initialized as a constant. "
                                        "It will be floated in the new workspace.")
                    nuis.setConstant(False)
                else:
                    self.stdout.warning(f"The nuisace parameter {nuis_name} is initialized as a constant.")
                    if remove_fixed_nuis:
                        self.stdout.warning(f"It will be removed from the new ModelConfig.")
                        continue
                    else:
                        self.stdout.warning("Careful!")
            nuisance_parameters.add(nuis)
        
        # set global observables
        global_observables = ROOT.RooArgSet()
        for glob_name in glob_names:
            glob = self._get_relevant_variable(glob_name, new_ws, pdf)
            if not glob:
                self.stdout.warning(f"The global observable {glob_name} no longer exists in "
                                    "the new workspace. It will be removed from the new ModelConfig.")
                continue
            if not glob.isConstant():
                self.stdout.warning(f"The global observable {glob_name} is initialized as a floating "
                                    "parameter. It will be set to constant in the new workspace.")

                glob.setConstant(True)
            global_observables.add(glob)

        # set observables
        observables = ROOT.RooArgSet()
        old_obs = old_mc.GetObservables()
        if old_obs:
            for obs in old_obs:
                obs_name = obs.GetName()
                new_obs = new_ws.obj(obs_name)
                if not new_obs:
                    raise RuntimeError(f"observable {obs_name} no longer exists in the new workspace")
                observables.add(new_obs)
        mc.SetNuisanceParameters(nuisance_parameters)
        mc.SetGlobalObservables(global_observables)
        mc.SetObservables(observables)
        
        return mc
    
    @semistaticmethod
    def extract_ws_variables(self, ws:ROOT.RooWorkspace, variables:ROOT.RooArgSet, strict:bool=True):
        extracted_variables = ROOT.RooArgSet()
        for variable in variables:
            variable_name = variable.GetName()
            extracted_variable = ws.arg(variable_name)
            if not extracted_variable:
                if strict:
                    raise RuntimeError(f"missing variable {variable_name} in the workspace {ws.GetName()}")
                else:
                    self.stdout.warning(f"No variable {variable_name} found in the workspace {ws.GetName()}")
                    continue
            extracted_variables.add(extracted_variable, True)
        return extracted_variables

    def rename_variables(self, old_mc:ROOT.RooStats.ModelConfig, new_ws:ROOT.RooWorkspace, rename_map:Dict):
        old_var_expr = ",".join(list(rename_map.keys()))
        new_var_expr = ",".join(list(rename_map.values()))
        getattr(new_ws, "import")(old_mc.GetPdf(),
                                  ROOT.RooFit.RenameVariable(old_var_expr, new_var_expr),
                                  ROOT.RooFit.RecycleConflictNodes())
        if rename_map:
            self.stdout.info("Renamed variables\n")
            rename_table = "\n".join(self.get_name_mapping_str_arrays(rename_map))
            self.stdout.info(rename_table, bare=True)
        
    def rename_objects(self, ws:ROOT.RooWorkspace, mc_map: Dict[str, ROOT.RooStats.ModelConfig]):
        if len(self.actions['rename']['workspace']) > 0:
            self.stdout.info("Renamed workspace\n")
            rename_map = {}
            for old_name, new_name in self.actions['rename']['workspace'].items():
                rename_map[ws.GetName()] = new_name
                ws.SetName(new_name)
            rename_table = "\n".join(self.get_name_mapping_str_arrays(rename_map))
            self.stdout.info(rename_table, bare=True)
        if len(self.actions['rename']['model_config']) > 0:
            self.stdout.info("Renamed model config\n")
            rename_map = {}
            for old_name, new_name in self.actions['rename']['model_config'].items():
                if old_name is None:
                    if len(mc_map) > 1:
                        raise RuntimeError(
                            'original model config name must be specified when there are multiple '
                            'model configs available in the original workspace'
                        )
                    old_name = next(iter(mc_map.keys()))
                rename_map[old_name] = new_name
                mc = mc_map.get(old_name, None)
                if not mc:
                    raise RuntimeError(f"model config \"{old_name}\" not found in the original workspace")
                mc.SetName(new_name)
            rename_table = "\n".join(self.get_name_mapping_str_arrays(rename_map))
            self.stdout.info(rename_table, bare=True)
        if len(self.actions['rename']['dataset']) > 0:
            rename_map = {}            
            for old_name, new_name in self.actions['rename']['dataset'].items():
                if old_name == new_name:
                    continue
                dataset = ws.data(old_name)
                if not dataset:
                    raise RuntimeError(f"dataset \"{old_name}\" not found in the original workspace")
                check_dataset = ws.data(new_name)
                if check_dataset:
                    raise RuntimeError(f"cannot rename dataset from \"{old_name}\" to \"{new_name}\": "
                                       f"the dataset \"{new_name}\" already exists in the original workspace")
                rename_map[old_name] = new_name
                dataset.SetName(new_name)
            if rename_map:
                self.stdout.info("Renamed dataset\n")
                rename_table = "\n".join(self.get_name_mapping_str_arrays(rename_map))
                self.stdout.info(rename_table, bare=True)                
        
    def import_datasets(self, old_ws:ROOT.RooWorkspace, new_ws:ROOT.RooWorkspace,
                        dataset_names:Optional[List[str]]=None):
        if dataset_names is None:
            datasets = old_ws.allData()
        else:
            datasets = []
            for dataset_name in dataset_names:
                dataset = old_ws.data(dataset_name)
                if not dataset:
                    raise RuntimeError(f"dataset {dataset_name} does not exist in the original workspace")
                datasets.append(dataset)
        for dataset in datasets:
            getattr(new_ws, "import")(dataset)
            self.stdout.info(f"Imported dataset \"{dataset.GetName()}\".")
            
    def redefine_objects(self, old_ws:ROOT.RooWorkspace, new_ws:ROOT.RooWorkspace):
        flag = False
        for i, expr in enumerate(self.actions['redefine']):
            self.stdout.info(f"(Item {i}) {expr}")
            obj_name, obj_type = self._get_object_name_and_type_from_expr(expr)
            arg = old_ws.arg(obj_name)
            if not arg:
                if self.config['strict']:
                    raise RuntimeError(f"object {obj_name} does not exist in the original workspace")
                else:
                    self.stdout.warning(f"object {obj_name} does not exist in the original workspace")
                    continue
            if obj_type == WSObjectType.VARIABLE:
                result = re.search(r"\[(.+)\]", expr)
                if not result:
                    raise RuntimeError(f"invalid variable expression {expr}")
                self.import_expression(new_ws, expr)
                new_var = new_ws.var(obj_name)
                tokens = result.group(1).split(",")
                # only modify the value
                if len(tokens) == 1:
                    new_var.setVal(float(tokens[0]))
                    if arg.ClassName() != "RooConstVar":
                        old_range = arg.getRange()
                        # need to restore the range
                        new_var.setRange(old_range[0], old_range[1])
                # only modify the range
                elif len(tokens) == 2:
                    # need to restore the value
                    new_var.setVal(arg.getVal())
                    new_var.setRange(float(tokens[0]), float(tokens[1]))
                # need to restore constant state
                new_var.setConstant(arg.isConstant())
            else:
                self.import_expression(new_ws, expr)
            flag = True
        return flag
        
    def implement_objects(self, ws:ROOT.RooWorkspace):
        flag = False
        for i, expr in enumerate(self.actions['define']):
            self.stdout.info(f"(Item {i}) {expr}")
            if "FlexibleInterpVar" in expr:
                self.implement_flexible_interp_var(ws, expr)
            elif "RooMultiVarGaussian" in expr:
                self.implement_multi_var_gaussian(ws, expr)
            elif "ResponseFunction" in expr:
                self.implement_response_func_var(ws, expr)
            else:
                self.import_expression(ws, expr)
            flag = True
        return flag
                
    def implement_external_pdfs(self, ws:ROOT.RooWorkspace):
        flag = False
        for i, item in enumerate(self.actions['constraint']):
            pdf_name = item['pdf']
            file = item['file']
            if file is not None:
                self.load_external_pdf(file, pdf_name, ws)
                self.stdout.info(f"Loaded external pdf {pdf_name} from {file}")
                flag = True
        return flag
                
    def load_external_pdf(self, ext_rfile:str, pdf_name:str, ws:ROOT.RooWorkspace):
        model = ExtendedModel(ext_rfile, data_name=None, verbosity="WARNING")
        pdf = model.workspace.pdf(pdf_name)
        if not pdf:
            raise RuntimeError(f"pdf {pdf_name} not found in the workspace loaded from {ext_rfile}")
        self.import_object(ws, pdf)
    
    def get_actual_rename_map(self, rename_map:Dict, old_ws:ROOT.RooWorkspace, new_ws:ROOT.RooWorkspace):
        actual_rename_map = {}
        for old_name, new_name in rename_map.items():
            # if the object with the new name is already defined, it's not a renaming
            if (old_ws.arg(new_name)) or (new_ws.arg(new_name)):
                continue
            actual_rename_map[old_name] = new_name
        return actual_rename_map
    
    def get_rename_map(self, old_ws:ROOT.RooWorkspace, new_ws:ROOT.RooWorkspace):
        rename_map = {}
        #regex = re.compile(r"\(([\w=,]+)\)")
        regex = re.compile(r"\((.+)\)")
        strict = self.config['strict']
        # rename definitions from the "Map" node
        for expr in self.actions['map']:
            match = regex.search(expr)
            if not match:
                raise RuntimeError(f"invalid expression for a map: {expr}")
            rename_str = [i for i in match.group(1).split(",") if i]
            if len(rename_str) < 2:
                raise RuntimeError(f"no members found for a map: {expr}")
            rename_str = rename_str[1:]
            for item in rename_str:
                tokens = item.split("=")
                if len(tokens) != 2:
                    raise RuntimeError(f"invalid rename syntax: {item}")
                old_name = tokens[0]
                new_name = tokens[1]
                if not old_ws.arg(old_name):
                    if strict:
                        raise RuntimeError(f"object {old_name} (-> {new_name}) does not exist in the original workspace")
                    else:
                        self.stdout.warning(f"object {old_name} does not exist in the original workspace, skipping...")
                        continue
                if not new_ws.arg(new_name):
                    raise RuntimeError(f"object {new_name} (<- {old_name}) does not exist in the temporary workspace")
                if old_name in rename_map:
                    raise RuntimeError(f"object {old_name} is renamed more than once")
                rename_map[old_name] = new_name
        # rename definitions from the "Rename" node
        for old_name, new_name in self.actions['rename']['variable'].items():
            if not old_ws.arg(old_name):
                if strict:
                    raise RuntimeError(f"object {old_name} (-> {new_name}) does not exist int the original workspace")
                else:
                    self.stdout.warning(f"object {old_name} does not exist in the original workspace, skipping...")
                    continue
            if old_name in rename_map:
                raise RuntimeError(f"object {old_name} is renamed more than once")
            rename_map[old_name] = new_name
        return rename_map
    
    def remake_simultaneous_pdf(self, old_mc:ROOT.RooStats.ModelConfig, new_ws:ROOT.RooWorkspace):
        pdf_name = old_mc.GetPdf().GetName()
        pdf = new_ws.pdf(pdf_name)
        if not pdf:
            raise RuntimeError(f"pdf {pdf_name} does not exist in workspace {new_ws.GetName()}")
        category = pdf.indexCat()
        n_cat = len(category)
        
        observables = self.extract_ws_variables(new_ws, old_mc.GetObservables(), True)
        nuisance_parameters = self.extract_ws_variables(new_ws, old_mc.GetNuisanceParameters(), False)

        pdf_map = {}
        
        for i in range(n_cat):
            category.setBin(i)
            category_name = category.getLabel()
            self.stdout.info(f"Creating new pdf for the category {category_name}")
            pdf_i = pdf.getPdf(category_name)
            
            base_components = ROOT.RooArgSet()
            obs_terms = ROOT.RooArgList()
            dis_constraints = ROOT.RooArgList()
            ROOT.RooStats.FactorizePdf(observables, pdf_i, obs_terms, dis_constraints)
            base_components.add(obs_terms)
            
            # remove constraint pdfs that are no longer needed
            if dis_constraints.getSize() > 0:
                constraints = pdf_i.getAllConstraints(observables, nuisance_parameters, True)
                base_components.add(constraints)
            
            new_pdf_name = f"{pdf_i.GetName()}__addConstr"
            # adding additional constraint pdf
            for i, item in enumerate(self.actions['constraint']):
                pdf_name = item['pdf']
                nuis_names = item['nuis']
                glob_names = item['glob']
                independent = item['independent']
                new_pdf = new_ws.pdf(pdf_name)
                if not new_pdf:
                    raise RuntimeError(f"pdf {pdf_name} does not exist in the new workspace")
                if independent:
                    base_components.add(new_pdf)
                    self.stdout.info(f"Adding independent constraint pdf \"{pdf_name}\" to "
                                     f"\"{new_pdf_name}\"")
                    continue
                # check whether the current category depends on the constraint pdf
                for nuis_name in nuis_names:
                    nuis_var = self._get_relevant_variable(nuis_name, new_ws, pdf_i)
                    if (nuis_var is not None):
                        base_components.add(new_pdf)
                        break
                        
            
            pdf_map[category_name] = ROOT.RooProdPdf(new_pdf_name, new_pdf_name, base_components)
        c_pdf_map = RooAbsPdf.get_pdf_map(pdf_map)
        pdf_name = old_mc.GetPdf().GetName()
        sim_pdf = ROOT.RooSimultaneous(pdf_name, f"{pdf_name}__addConstr", c_pdf_map, category)
        return sim_pdf
    
    @semistaticmethod
    def _get_relevant_variable(self, var_name:str, ws:ROOT.RooWorkspace, pdf:ROOT.RooAbsPdf, warn:bool=False):
        var = ws.var(var_name)
        if not var:
            if warn:
                self.stdout.warning(f"Variable {var_name} does not exist in the new workspace")
            return None
        if not pdf.dependsOn(var):
            if warn:
                self.stdout.warning(f"Variable {var_name} exists in the new workspace but is "
                                    f"not part of the provided pdf {pdf.GetName()}")
            return None
        return var
        
    def implement_flexible_interp_var(self, ws:ROOT.RooWorkspace, expr:str):
        # parse attributes
        expr = re.sub('\s+', '', expr)
        program = re.compile(r"FlexibleInterpVar::(?P<name>[\w]+)\((?P<NPName>[\w,]+),"
                             r"(?P<nominal>[\w,]+),(?P<errHi>[\w,]+),(?P<errLo>[\w,]+),"
                             r"(?P<interpolation>[\w,]+)\)")
        result = program.search(expr)
        if not result:
            raise RuntimeError(f"invalid format for FlexibleInterpVar definition: {expr}")
        groups = result.groupdict()
        response_name = groups['name']
        nuis_name     = groups['NPName']
        nominal       = float(groups['nominal'])
        error_hi      = float(groups['errHi'])
        error_lo      = float(groups['errLo'])
        interpolation = int(groups['interpolation'])
        
        sigma_var_low = np.array([nominal + error_lo])
        sigma_var_high = np.array([nominal + error_hi])
        code = np.array([interpolation])
        
        nuis_arglist = ROOT.RooArgList()
        nuis = self.get_workspace_arg(ws, nuis_name)
        nuis_arglist.add(nuis)
        
        function = ROOT.RooStats.HistFactory.FlexibleInterpVar(response_name, response_name, nuis_arglist,
                                                               nominal, sigma_var_low, sigma_var_high, code)
        self.import_object(ws, function)
        self.stdout.info(f"Implemented FlexibleInterpVar \"{response_name}\"")
    
    def implement_response_func_var(self, ws:ROOT.RooWorkspace, expr:str):
        
        if not getattr(ROOT, "ResponseFunction"):
            raise RuntimeError("ResponseFunction class undefined: may be you need to load the corresponding macro...")
        
        # parse attributes
        expr = re.sub('\s+', '', expr)
        program = re.compile(r"ResponseFunction::(?P<name>[\w]+)\((?P<NPName>[\w,]+),"
                             r"(?P<nominal>[\w,]+),(?P<errLo>[\w,]+),(?P<errHi>[\w,]+),"
                             r"(?P<interpolation>[\w,]+)\)")
        result = program.search(expr)
        if not result:
            raise RuntimeError(f"invalid format for ResponseFunction definition: {expr}")
        groups = result.groupdict()
        response_name = groups['name']
        nuis_name     = groups['NPName']
        nominal       = float(groups['nominal'])
        error_lo      = groups['errLo']
        error_hi      = groups['errHi']
        interpolation = int(groups['interpolation'])
        
        nominal_list = np.array([nominal])
        code = np.array([interpolation])
        
        nuis_arglist = ROOT.RooArgList()
        nuis = self.get_workspace_arg(ws, nuis_name)
        nuis_arglist.add(nuis)
        error_lo_arglist = ROOT.RooArgList()
        error_lo_arg = self.get_workspace_arg(ws, error_lo)
        error_lo_arglist.add(error_lo_arg)
        error_hi_arglist = ROOT.RooArgList()
        error_hi_arg = self.get_workspace_arg(ws, error_hi)
        error_hi_arglist.add(error_hi_arg)
        
        function = ROOT.ResponseFunction(response_name, response_name, nuis_arglist, nominal_list,
                                         error_lo_arglist, error_hi_arglist, code)
        self.import_object(ws, function)
        self.stdout.info(f"Implemented ResponseFunction \"{response_name}\"")
    
    def implement_multi_var_gaussian(self, ws:ROOT.RooWorkspace, expr:str):
        # parse attributes
        expr = re.sub('\s+', '', expr)
        program = re.compile(r"RooMultiVarGaussian::(?P<name>[\w]+)\({(?P<obsList>[\w,]+)}:"
                             r"{(?P<meanList>[\w,]+)}:{(?P<uncertList>[\w,]+)}:"
                             r"{(?P<correlationList>[\w,]+)}\)")
        result = program.search(expr)
        if not result:
            raise RuntimeError(f"invalid format for RooMultiVarGaussian definition: {expr}")
        groups = result.groupdict()
        function_name    = groups['name']
        obs_list         = groups['obsList'].split(",")
        mean_list        = groups['meanList'].split(",")
        uncert_list      = groups['uncertList'].split(",")
        correlation_list = groups['correlationList'].split(",")
        
        n_poi = len(obs_list)
        if not all(len(item_list) == n_poi for item_list in [obs_list, mean_list, uncert_list]):
            raise RuntimeError(f"number of items in each argument group of a RooMultiVarGaussian "
                               f"definition must be equal: {expr}")
        if len(correlation_list) != (n_poi * (n_poi - 1) // 2):
            raise RuntimeError("number of correlation matrix elements must be N * (N-1) / 2, where "
                               "N is the dimension of the matrix")
        obs_arglist = ROOT.RooArgList()
        mean_arglist = ROOT.RooArgList()
        for i in range(n_poi):
            obs_name = obs_list[i]
            mean_name = mean_list[i]
            obs = self.get_workspace_arg(ws, obs_name)
            obs_arglist.add(obs)
            mean = self.get_workspace_arg(ws, mean_name)
            mean_arglist.add(mean)
        V = ROOT.TMatrixDSym(n_poi)
        py_V = np.zeros(n_poi * n_poi).reshape(n_poi, n_poi)
        index = 0
        for i in range(n_poi):
            for j in range(i, n_poi):
                if (i == j):
                    v = float(uncert_list[i])
                    V[i, i] = v * v
                    py_V[i, i] = v * v
                elif (i < j):
                    v = float(correlation_list[index]) * float(uncert_list[i]) * float(uncert_list[j])
                    V[i, j] = v
                    V[j, i] = v
                    py_V[i, j] = v
                    py_V[j, i] = v
                    index += 1
        function = ROOT.RooMultiVarGaussian(function_name, function_name, obs_arglist, mean_arglist, V)
        self.import_object(ws, function)
        self.stdout.info(f"Implemented RooMultiVarGaussian \"{function_name}\" with correlation matrix")
        self.stdout.info(str(py_V), bare=True)