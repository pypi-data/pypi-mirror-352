class RooVectorDataStore:
    
    @staticmethod
    def to_numpy(store:"ROOT.RooVectorDataStore",
                 copy: bool = True):
        if hasattr(store, 'to_numpy'):
            return store.to_numpy(copy=copy)
        from quickstats.interface.cppyy.vectorize import c_array_to_np_array
        size = store.size()
        batches = store.getBatches(0, size)
        variables = store.get()
        data = {}
        for variable in variables:
            name = variable.GetName()
            batch = batches.getBatch(variable)
            data[name] = c_array_to_np_array(batch.data(), size=size, copy=copy)
        weight_batch = store.getWeightBatch(0, size)
        weights = c_array_to_np_array(weight_batch.data(), size=size, copy=copy)
        data['weight'] = weights
        return data