from quickstats import AbstractObject

class ExtensionDataFrame(AbstractObject):

    @property
    def dataframe(self):
        return self._df
        
    def __init__(self, df:"pandas.DataFrame", verbosity:str="INFO"):
        super().__init__(verbosity=verbosity)
        self._df = df

    def __repr__(self):
        return self.dataframe.__repr__()

    def _repr_html_(self):
        return self.dataframe._repr_html_()

    def _parse_argument(self, ops_name:str, index=None, columns=None, axis=None, **kwargs):
        assert len(kwargs) == 1
        argname = list(kwargs)[0]
        argval  = kwargs[argname]
        if (argval is None) and (index is None) and (columns is None):
            raise TypeError(f"must pass an index to {ops_name}")
        if (index is not None) or (columns is not None):
            if axis is not None:
                raise TypeError("cannot specify both 'axis' and any of 'index' or 'columns'")
            if argval is not None:
                raise TypeError(f"cannot specify both '{argname}' and any or 'index' or 'columns'")
        else:
            if axis and self.df._get_axis_number(axis) == 1:
                columns = argval
            else:
                index = argval
        return index, columns
                
        
    def select_values(self, mapper=None, index=None, columns=None, axis=None, copy:bool=True, inplace:bool=False, invert:bool=False):
        df = self._df
        index, columns = self._parse_argument('select', index=index, columns=columns,
                                              axis=axis, mapper=mapper)
        # does not consider copy on write yet
        result = self._df if inplace else self._df.copy(deep=copy)
        index_ops = lambda x: result.index.get_level_values(x)
        column_ops = lambda x: result[x]
        for ops, maps in [(index_ops, index), (column_ops, columns)]:
            if maps is None:
                continue
            for attribs, selections in maps.items():
                if not isinstance(attribs, tuple):
                    attribs = (attribs,)
                    selections = (selections,)
                masks = None
                for i, attrib in enumerate(attribs):
                    selection = selections[i]
                    if not callable(selection):
                        if isinstance(selection, (tuple, list)):
                            mask = ops(attrib).isin(selection)
                        else:
                            mask = ops(attrib) == selection
                    elif attrib is not None:
                        mask = ops(attrib).apply(selection)
                    else:
                        mask = result.apply(selection)
                    if masks is None:
                        masks = mask
                    else:
                        masks &= mask
                if invert:
                    masks = ~masks
                result = result[masks]
        if inplace:
            self._df = result
            return None
        return result

    def reject_values(self, mapper=None, index=None, columns=None, axis=None, copy:bool=True, inplace:bool=False):
        return self.select_values(mapper=mapper, index=index,
                                  columns=columns, axis=axis,
                                  copy=copy, inplace=inplace,
                                  invert=True)

    def concat(self, other, copy:bool=True, inplace:bool=False, order:str="first", **kwargs):
        import pandas as pd
        result = self._df if inplace else self._df.copy(deep=copy)
        if order == "first":
            if isinstance(other, list):
                objs = [result] + other
            else:
                objs = [result, other]
        elif order == "last":
            if isinstance(other, list):
                objs = other + [result]
            else:
                objs = [other, result]
        else:
            raise TypeError('order must be either "first" or "last"')
        result = pd.concat(objs, **kwargs)
        if inplace:
            self._df = result
            return None
        return result