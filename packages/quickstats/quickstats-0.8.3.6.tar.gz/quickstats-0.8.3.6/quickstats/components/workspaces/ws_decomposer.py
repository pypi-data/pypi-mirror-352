###############################################################################
### This is a reimplementation of workspaceCombiner library in python
### original author: Hongtao Yang, Haoshuang Ji
###############################################################################
import os
import re
import json
import fnmatch
from typing import Optional, Union, List, Dict, Sequence
    
import numpy as np

import ROOT

import quickstats
from quickstats import AbstractObject, semistaticmethod, timer
from quickstats.maths.numerics import is_integer
from quickstats.utils.string_utils import split_str
from quickstats.utils.common_utils import remove_list_duplicates
from quickstats.components import ExtendedModel
from quickstats.components.workspaces import XMLWSBase
from quickstats.interface.root import RooAbsPdf, RooDataSet

class WSDecomposer(XMLWSBase):
    
    @semistaticmethod
    def parse_categories(self, expr:Union[List[Union[str, int]], str, int],
                         category:"ROOT.RooCategory"):
        ncat = category.size()
        if isinstance(expr, str):
            components = split_str(expr, sep=',', remove_empty=True)
        elif isinstance(expr, int):
            components = [expr]
        elif isinstance(expr, Sequence):
            components = list(expr)
        else:
            raise ValueError(f'invalid category expression: {expr}')
        category_idx_label_map = {idx_label.second: idx_label.first for idx_label in category}
        category_labels = list(category_idx_label_map.values())
        selected_categories = []
        for component in components:
            if isinstance(component, str):
                matched_categories = fnmatch.filter(category_labels, component)
                if matched_categories:
                    selected_categories.extend(matched_categories)
                    continue
                # handle the case where we have a string representation of index/indices
                if is_integer(component):
                    component = [int(component)]
                # range of index
                elif '-' in component:
                    tokens = split_str(component, sep='-', remove_empty=True)
                    if len(tokens) != 2:
                        raise ValueError(f'invalid range expression: {component}')
                    if (not is_integer(tokens[0])) or (not is_integer(tokens[1])):
                        raise ValueError(f'start and end range must be integers: {component}')
                    ranges = list(range(int(tokens[0]), int(tokens[1]) + 1))
                    if not ranges:
                        raise ValueError(f'invalid range expression: {component}')
                    component = ranges
                else:
                    raise RuntimeError(f'no category matching the expression "{component}" is found')
            if not isinstance(component, list):
                component = [component]
            for subcomponent in component:
                if not isinstance(subcomponent, int):
                    raise TypeError(f'category must be specified by index (integer) or '
                                    f'label (string), not {type(component)}')
                if subcomponent not in category_idx_label_map:
                    raise ValueError('category index out of bounds')
                selected_categories.append(category_idx_label_map[subcomponent])
        selected_categories = remove_list_duplicates(selected_categories)
        return selected_categories
    
    @semistaticmethod
    def parse_snapshots(
        self,
        ws:"ROOT.RooWorkspace",
        expr:Optional[Union[List[str], str]]=None
    ) -> List["ROOT.RooArgSet"]:
        if expr is None:
            if hasattr(ws, 'getSnapshots'):
                return [snapshot for snapshot in ws.getSnapshots()]
            else:
                return []
        if isinstance(expr, str):
            snapshot_names = split_str(expr, sep=',', remove_empty=True)
        snapshots = []
        for snapshot_name in snapshot_names:
            snapshot = ws.getSnapshot(snapshot_name)
            if not snapshot:
                self.stdout.warning(f'No snapshot named "{snapshot_name}". Skipping.')
                continue
            snapshots.append(snapshot)
        return snapshots
    
    def create_decomposed_workspace(
        self,
        infile:str,
        outfile:str,
        category_expr:Union[List[Union[str, int]], str, int]="*",
        snapshots_to_save:Optional[List[str]]=None,
        rebuild_nuis:bool=False,
        rebuild_pdf:bool=False,
        import_class_code:bool=True
    ) -> "ROOT.RooWorkspace":
        with timer() as t:
            model = ExtendedModel(infile, data_name=None, verbosity="WARNING")
            orig_cat = model.pdf.indexCat()
            categories = self.parse_categories(category_expr, orig_cat)
            snapshots = self.parse_snapshots(model.workspace, snapshots_to_save)
            if not categories:
                raise RuntimeError('no categories selected')
            new_ws  = ROOT.RooWorkspace(model.workspace.GetName(), model.workspace.GetTitle())
            new_cat = ROOT.RooCategory(orig_cat.GetName(), orig_cat.GetTitle())
            new_pdf = ROOT.RooSimultaneous(model.pdf.GetName(), model.pdf.GetTitle(), new_cat)
            new_mc  = ROOT.RooStats.ModelConfig(model.model_config.GetName(), new_ws)
            argsets = {
                'nuis' : ROOT.RooArgSet(),
                'globs': ROOT.RooArgSet(),
                'pois' : ROOT.RooArgSet(),
                'obs'  : ROOT.RooArgSet()
            }
            argsets['obs'].add(new_cat)
            self.stdout.info(f'Categories to include: {", ".join(categories)}')
            for category in categories:
                self.stdout.info(f'Processing category "{category}"')
                pdf_cat = model.pdf.getPdf(category)
                if not pdf_cat:
                    raise RuntimeError(f'Missing pdf for the category: {category}')
                #self.stdout.info(f'\tCategory Name: {category}')
                new_cat.defineType(category)
                obs_cat   = pdf_cat.getObservables(model.data)
                param_cat = pdf_cat.getParameters(obs_cat)
                pois_cat  = param_cat.selectCommon(model.pois)
                globs_cat = param_cat.selectCommon(model.global_observables)
                if rebuild_nuis:
                    nuis_cat = ROOT.RFUtils.GetConstantParameters(param_cat, False)
                    nuis_cat.remove(pois_cat, False, True)
                    nuis_cat.remove(globs_cat, False, True)
                else:
                    nuis_cat  = param_cat.selectCommon(model.nuisance_parameters)
                argsets['obs'].add(obs_cat)
                argsets['pois'].add(pois_cat)
                argsets['nuis'].add(nuis_cat)
                argsets['globs'].add(globs_cat)

                if rebuild_pdf:
                    pdf_cat = RooAbsPdf.remove_disconnected_components(pdf_cat, model.data)
                    ROOT.SetOwnership(pdf_cat, False)

                new_pdf.addPdf(pdf_cat, category)

            # import category
            new_ws.Import(new_cat, ROOT.RooFit.Silence())
            # import pdf
            new_ws.Import(new_pdf, ROOT.RooFit.RecycleConflictNodes(),
                          ROOT.RooFit.Silence())
            # import dataset
            for data in model.workspace.allData():
                py_data = RooDataSet(data)
                py_data.filter_categories(categories)
                new_data = py_data.new()
                new_ws.Import(new_data)
            proto_data = new_ws.data(model.data.GetName())
            if not proto_data:
                raise RuntimeError(f'Failed to import data "{model.data.GetName()}"')
            # import snapshot
            for snapshot in snapshots:
                new_ws.saveSnapshot(snapshot.GetName(), snapshot, 1)
            # build import import model config
            new_mc.SetWorkspace(new_ws)
            new_mc.SetPdf(new_pdf)
            new_mc.SetProtoData(proto_data)
            new_mc.SetObservables(argsets['obs'])
            new_mc.SetParametersOfInterest(argsets['pois'])
            new_mc.SetNuisanceParameters(argsets['nuis'])
            new_mc.SetGlobalObservables(argsets['globs'])
            new_ws.Import(new_mc)

            if import_class_code:
                self.import_class_code(new_ws)
                
            if outfile is not None:
                self.stdout.info(f'Saving decomposed workspace to "{outfile}"')
                new_ws.writeToFile(outfile, True)
        self.stdout.info(f"Total time taken: {t.interval:.3f}s")
        return new_ws