from typing import Optional, List

import numpy as np

from .rooproc_output_action import RooProcOutputAction
from .auxiliary import register_action

from quickstats.utils.common_utils import is_valid_file
from quickstats.utils.data_conversion import ConversionMode
from quickstats.interface.root import RDataFrameBackend

@register_action
class RooProcAsParquet(RooProcOutputAction):
    
    NAME = "AS_PARQUET"

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
        import awkward as ak
        try:
            # NB: RDF Dask/Spark does not support GetColumnType yet
            if processor.backend in [RDataFrameBackend.DASK, RDataFrameBackend.SPARK]:
                rdf.GetColumnType = rdf._headnode._localdf.GetColumnType
            array = ak.from_rdataframe(rdf, columns=save_columns)
        except:
            array = ak.Array(rdf.AsNumpy(save_columns))
        self.makedirs(filename)
        ak.to_parquet(array, filename)
        return rdf, processor