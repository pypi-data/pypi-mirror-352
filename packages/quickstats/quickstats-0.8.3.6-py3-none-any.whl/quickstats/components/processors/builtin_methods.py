BUILTIN_METHODS = \
{
    "Namespace_ROOT_VecOps": "using namespace ROOT::VecOps;", 
    "Namespace_ROOT_Math": "using namespace ROOT::Math;",
    "RVecExtension": 
    """
    
    template<typename T>
    auto SizeOf(const T &vec){
        return vec.size();
    }
    
    template<typename T>
    int InStrictRange(const T &value, const T &vmin, const T &vmax){
        return (value > vmin) && (value < vmax);
    }
    
    template<typename T>
    int InLooseRange(const T &value,const T &vmin,const T &vmax){
        return (value >= vmin) && (value <= vmax);
    }
    
    
    LorentzVector<PtEtaPhiM4D<double>> PtEtaPhiM4DVector(const float &pt, const float &eta, const float &phi, const float &M,
                                                         const float &pt_threshold=0.){
        if (pt > pt_threshold)
            return LorentzVector<PtEtaPhiM4D<double>>{pt, eta, phi, M};
        return LorentzVector<PtEtaPhiM4D<double>>{};
    }
    
    LorentzVector<PtEtaPhiE4D<double>> PtEtaPhiE4DVector(const float &pt, const float &eta, const float &phi, const float &E,
                                                         const float &pt_threshold=0.){
        if (pt > pt_threshold)
            return LorentzVector<PtEtaPhiE4D<double>>{pt, eta, phi, E};
        return LorentzVector<PtEtaPhiE4D<double>>{};
    }
    
    RVec<LorentzVector<PtEtaPhiM4D<double>>> PtEtaPhiM4DVectorArray(const RVec<float> &pt, const RVec<float> &eta, 
                                                                    const RVec<float> &phi, const RVec<float> &M){
        RVec<LorentzVector<PtEtaPhiM4D<double>>> result;
        for (size_t i=0; i < pt.size(); i++){
            LorentzVector<PtEtaPhiM4D<double>> lv{pt[i], eta[i], phi[i], M[i]};
            result.push_back(lv);
        }
        return result;
    }
    
    RVec<LorentzVector<PtEtaPhiM4D<double>>> PtEtaPhiM4DVectorArray(const RVec<float> &pt, const RVec<float> &eta, 
                                                                    const RVec<float> &phi, const float &M){
        RVec<LorentzVector<PtEtaPhiM4D<double>>> result;
        for (size_t i=0; i < pt.size(); i++){
            LorentzVector<PtEtaPhiM4D<double>> lv{pt[i], eta[i], phi[i], M};
            result.push_back(lv);
        }
        return result;
    }
    
    RVec<LorentzVector<PtEtaPhiE4D<double>>> PtEtaPhiE4DVectorArray(const RVec<float> &pt, const RVec<float> &eta, 
                                                                    const RVec<float> &phi, const RVec<float> &E){
        RVec<LorentzVector<PtEtaPhiE4D<double>>> result;
        for (size_t i=0; i<pt.size(); i++){
            LorentzVector<PtEtaPhiE4D<double>> lv{pt[i], eta[i], phi[i], E[i]};
            result.push_back(lv);
        }
        return result;
    }

    RVec<LorentzVector<PtEtaPhiE4D<double>>> PtEtaPhiE4DVectorArray(const RVec<float> &pt, const float &eta, 
                                                                    const RVec<float> &phi, const RVec<float> &E){
        RVec<LorentzVector<PtEtaPhiE4D<double>>> result;
        for (size_t i=0; i<pt.size(); i++){
            LorentzVector<PtEtaPhiE4D<double>> lv{pt[i], eta, phi[i], E[i]};
            result.push_back(lv);
        }
        return result;
    }
    
    template<typename T>
    T VectorSum(const RVec<T> &vec, int n=0){
        T result;
        if ((n==0) || (n > vec.size()))
            n = vec.size();
        for (size_t i=0; i < n; i++)
            result += vec[i];
        return result;
    }
    
    // deprecated
    LorentzVector<PtEtaPhiM4D<double>> getLV_PtEtaPhiM(const float &pt, const float &eta, const float &phi, const float &M){
        LorentzVector<PtEtaPhiM4D<double>> result{pt, eta, phi, M};
        return result;
    }
    
    // deprecated
    LorentzVector<PtEtaPhiM4D<double>> getLV_PtEtaPhiM(const float &pt, const float &eta, const float &phi, const float &M,
                                                       const float &pt_threshold){
        if (pt > pt_threshold)
            return LorentzVector<PtEtaPhiM4D<double>>{pt, eta, phi, M};
        return LorentzVector<PtEtaPhiM4D<double>>{};
    }
    
    // deprecated
    LorentzVector<PtEtaPhiE4D<double>> getLV_PtEtaPhiE(const float &pt, const float &eta, const float &phi, const float &E){
        LorentzVector<PtEtaPhiE4D<double>> result{pt, eta, phi, E};
        return result;
    }
    
    // deprecated
    LorentzVector<PtEtaPhiE4D<double>> getLV_PtEtaPhiE(const float &pt, const float &eta, const float &phi, const float &E,
                                                       const float &pt_threshold){
        if (pt > pt_threshold)
            return LorentzVector<PtEtaPhiE4D<double>>{pt, eta, phi, E};
        return LorentzVector<PtEtaPhiE4D<double>>{};
    }
    
    // deprecated
    RVec<LorentzVector<PtEtaPhiM4D<double>>> getLVArray_PtEtaPhiM(const RVec<float> &pt, const RVec<float> &eta, 
                                                                 const RVec<float> &phi, const RVec<float> &M){
        RVec<LorentzVector<PtEtaPhiM4D<double>>> result;
        for (size_t i=0; i<pt.size(); i++){
            LorentzVector<PtEtaPhiM4D<double>> lv{pt[i], eta[i], phi[i], M[i]};
            result.push_back(lv);
        }
        return result;
    }
    
    // deprecated
    RVec<LorentzVector<PtEtaPhiM4D<double>>> getLVArray_PtEtaPhiM(const RVec<float> &pt, const RVec<float> &eta, 
                                                                 const RVec<float> &phi, const float &M){
        RVec<LorentzVector<PtEtaPhiM4D<double>>> result;
        for (size_t i=0; i<pt.size(); i++){
            LorentzVector<PtEtaPhiM4D<double>> lv{pt[i], eta[i], phi[i], M};
            result.push_back(lv);
        }
        return result;
    }
    
    // deprecated
    RVec<LorentzVector<PtEtaPhiE4D<double>>> getLVArray_PtEtaPhiE(const RVec<float> &pt, const RVec<float> &eta, 
                                                                 const RVec<float> &phi, const RVec<float> &E){
        RVec<LorentzVector<PtEtaPhiE4D<double>>> result;
        for (size_t i=0; i<pt.size(); i++){
            LorentzVector<PtEtaPhiE4D<double>> lv{pt[i], eta[i], phi[i], E[i]};
            result.push_back(lv);
        }
        return result;
    }
    
    // deprecated
    RVec<LorentzVector<PtEtaPhiE4D<double>>> getLVArray_PtEtaPhiE(const RVec<float> &pt, const float &eta, 
                                                                  const RVec<float> &phi, const RVec<float> &E){
        RVec<LorentzVector<PtEtaPhiE4D<double>>> result;
        for (size_t i=0; i<pt.size(); i++){
            LorentzVector<PtEtaPhiE4D<double>> lv{pt[i], eta, phi[i], E[i]};
            result.push_back(lv);
        }
        return result;
    }
    template<typename T>
    LorentzVector<PtEtaPhiE4D<double>> getLVSum_PtEtaPhiE(const RVec<LorentzVector<T>> &lv_vec, int n=0){
        LorentzVector<PtEtaPhiE4D<double>> result;
        if ((n==0)||(n>lv_vec.size()))
            n = (int)lv_vec.size();
        for (size_t i=0; i<n; i++)
            result += lv_vec[i];
        return result;
    }
    template<typename T>
    LorentzVector<PtEtaPhiM4D<double>> getLVSum_PtEtaPhiM(const RVec<LorentzVector<T>> &lv_vec, int n=0){
        LorentzVector<PtEtaPhiM4D<double>> result;
        if ((n==0)||(n>lv_vec.size()))
            n = (int)lv_vec.size();
        for (size_t i=0; i<n; i++)
            result += lv_vec[i];
        return result;
    }
    template<typename T>
    RVec<float> getArrayPt(const RVec<LorentzVector<T>> &lv_vec){
        RVec<float> result;
        for (auto &lv: lv_vec)
            result.push_back(lv.pt());
        return result;
    }
    template<typename T>
    RVec<float> getArrayEta(const RVec<LorentzVector<T>> &lv_vec){
        RVec<float> result;
        for (auto &lv: lv_vec)
            result.push_back(lv.eta());
        return result;
    }
    template<typename T>
    RVec<float> getArrayPhi(const RVec<LorentzVector<T>> &lv_vec){
        RVec<float> result;
        for (auto &lv: lv_vec)
            result.push_back(lv.phi());
        return result;
    }
    template<typename T>
    RVec<float> getArrayE(const RVec<LorentzVector<T>> &lv_vec){
        RVec<float> result;
        for (auto &lv: lv_vec)
            result.push_back(lv.E());
        return result;
    }
    template<typename T>
    RVec<float> getArrayM(const RVec<LorentzVector<T>> &lv_vec){
        RVec<float> result;
        for (auto &lv: lv_vec)
            result.push_back(lv.M());
        return result;
    }
    template<typename T>
    float getPt(const LorentzVector<T> &lv_vec){
        return lv_vec.pt();
    }
    template<typename T>
    float getEta(const LorentzVector<T> &lv_vec){
        return lv_vec.eta();
    }
    template<typename T>
    float getPhi(const LorentzVector<T> &lv_vec){
        return lv_vec.phi();
    }
    template<typename T>
    float getM(const LorentzVector<T> &lv_vec){
        return lv_vec.M();
    }
    template<typename T>
    float getE(const LorentzVector<T> &lv_vec){
        return lv_vec.E();
    }
    template<typename T>
    float getRapidity(const LorentzVector<T> &lv_vec){
        return lv_vec.Rapidity();
    }
    template<typename T>
    std::vector<T> RVec2Vec(const RVec<T> v){
        return std::vector<T>{v.begin(), v.end()};
    }
    template <typename T>
    RVec<typename RVec<T>::size_type> StableArgsortExt(const RVec<T> &v)
    {
       using size_type = typename RVec<T>::size_type;
       RVec<size_type> i(v.size());
       std::iota(i.begin(), i.end(), 0);
       std::stable_sort(i.begin(), i.end(), [&v](size_type i1, size_type i2) { return v[i1] < v[i2]; });
       return i;
    }
    Double_t Phi_mpi_pi(Double_t x)
    {
       return TVector2::Phi_mpi_pi(x);
    }
    template <typename T>
    RVec<T> TakeExt(const RVec<T> &v, const RVec<typename RVec<T>::size_type> &index, const int &size, const T &default_val){
        RVec<T> result = Take(v, index);
        for (int i=0; i < size - (int)result.size(); i++)
            result.push_back(default_val);
        return result;
    }
    
    template <typename T>
    T ProductExt(const RVec<T> &v, const T init = T(1)) // initialize with identity
    {
       return std::accumulate(v.begin(), v.end(), init, std::multiplies<T>());
    }
    
    template<typename T>
    RVec<LorentzVector<T>> SortLVByPT(const RVec<LorentzVector<T>> &lv_vec, const bool descending=true){
        if (descending)
            return Sort(lv_vec, [](LorentzVector<T> x, LorentzVector<T> y){return x.Pt() > y.Pt();});
        return Sort(lv_vec, [](LorentzVector<T> x, LorentzVector<T> y){return x.Pt() < y.Pt();});
    }
    
    template<typename T>
    RVec< typename RVec< T >::size_type > ArgSortLVByPT(const RVec<LorentzVector<T>> &lv_vec, const bool &descending=true){
        if (descending)
            return Argsort(lv_vec, [](LorentzVector<T> x, LorentzVector<T> y){return x.Pt() > y.Pt();});
        return Argsort(lv_vec, [](LorentzVector<T> x, LorentzVector<T> y){return x.Pt() < y.Pt();});
    }
    
    template<typename T>
    RVec< typename RVec< T >::size_type > GetP4RankedByPT(const RVec<LorentzVector<T>> &p4_vec, const size_t &rank, const bool descending=true){
        auto sort_indices = ArgSortLVByPT(p4_vec, descending);
        
    }
    
    template<typename T>
    LorentzVector<T> GetP4RankedByPT(const RVec<LorentzVector<T>> &p4_vec, const RVec< typename RVec< T >::size_type > &sort_indices, const size_t &rank){
        if (p4_vec.size() != sort_indices.size())
            throw std::runtime_error("size mismatch between p4 vectors and sort indices");
        if (rank >= p4_vec.size())
            return LorentzVector<T>{};
        return p4_vec[sort_indices[rank]];
    }

    template<typename T>
    LorentzVector<T> GetP4RankedByPT(const RVec<LorentzVector<T>> &p4_vec, const size_t &rank, const bool descending=true){
         RVec< typename RVec< T >::size_type > sort_indices = ArgSortLVByPT(p4_vec, descending);
        return GetP4RankedByPT(p4_vec, sort_indices, rank);
    }
    
    template<typename T1, typename T2>
    T1 PairFirst(const std::pair<T1, T2> &p){
        return p.first;
    }
    
    template<typename T1, typename T2>
    T2 PairSecond(const std::pair<T1, T2> &p){
        return p.second;
    }
    
    """,
    "CosineThetaStar":
    """
    template<typename T1, typename T2>
    auto GetCosineThetaStar(const LorentzVector<T1> &p1, const LorentzVector<T2> &p2, const bool sign=true){
        auto p12 = p1 + p2;
        auto p1p = (p1.E() + p1.Pz());
        auto p2p = (p2.E() + p2.Pz());
        auto p1m = (p1.E() - p1.Pz());
        auto p2m = (p2.E() - p2.Pz());
        auto m12 = p12.M();
        auto m12_squared = m12 * m12;
        auto pt12 = p12.Pt();
        auto pt12_squared = pt12 * pt12;
        auto result = ((p1p * p2m - p1m * p2p) / sqrt(m12_squared * (m12_squared + pt12_squared)));
        if (sign)
            result *= (p12.Pz()/abs(p12.Pz()));
        return result;
    }
    
    """
}