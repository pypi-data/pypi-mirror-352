
class TMatrixSym:

    @staticmethod
    def to_numpy(data: "ROOT.TMatrixTSym"):
        from quickstats.interface.cppyy.vectorize import c_array_to_np_array
        matrix = data.GetMatrixArray()
        nrows = data.GetNrows()
        ncols = data.GetNcols()
        return c_array_to_np_array(matrix, nrows * ncols, shape=(nrows, ncols))