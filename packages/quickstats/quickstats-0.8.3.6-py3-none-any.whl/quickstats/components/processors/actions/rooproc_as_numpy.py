from typing import Optional, List

import numpy as np

from .rooproc_output_action import RooProcOutputAction
from .auxiliary import register_action

from quickstats import module_exists
from quickstats.utils.common_utils import is_valid_file
from quickstats.utils.data_conversion import ConversionMode
from quickstats.interface.root import RDataFrameBackend

@register_action
class RooProcAsNumpy(RooProcOutputAction):
    
    NAME = "AS_NUMPY"
    
    def _execute(self, rdf:"ROOT.RDataFrame", processor:"quickstats.RooProcessor", **params):
        filename = params['filename']
        if processor.cache and is_valid_file(filename):
            processor.stdout.info(f'Cached output from "{filename}".')
            return rdf, processor
        processor.stdout.info(f'Writing output to "{filename}".')
        columns = params.get('columns', None)
        exclude = params.get('exclude', None)
        save_columns = self.resolve_columns(rdf, processor, columns=columns,
                                            exclude=exclude,
                                            mode="REMOVE_NON_STANDARD_TYPE")
        array = rdf.AsNumpy(save_columns)
        #array = None
        #if module_exist('awkward'):
        #    try:
        #        import awkward as ak
        #        # NB: RDF Dask/Spark does not support GetColumnType yet
        #        if processor.backend in [RDataFrameBackend.DASK, RDataFrameBackend.SPARK]:
        #            rdf.GetColumnType = rdf._headnode._localdf.GetColumnType
        #        array = ak.from_rdataframe(rdf, columns=save_columns)
        #        array = ak.to_numpy(array)
        #    except:
        #        array = None
        #        processor.stdout.warning("Failed to convert output to numpy arrays with awkward backend. "
        #                                 "Falling back to use ROOT instead")
        #if array is None:
        #    array = rdf.AsNumpy(save_columns)
        self.makedirs(filename)
        np.save(filename, array)
        return rdf, processor