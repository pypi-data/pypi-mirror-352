from typing import List, Optional

from .core import cpp_define

CPP_MACROS = \
{
   "VecUtils":
    """
    #include <fstream>
    #include <iterator>
    #include <vector>
    #include <stdexcept>
    namespace VecUtils{
        template <typename T>
        std::vector<T> as_vector(const T* data, size_t size) {
            return std::vector<T>(data, data + size);
        }
        template <typename T>
        void* as_pointer(std::vector<T> data) {
             T* result = new T[data.size()];
             std::copy(data.begin(), data.end(), result);
             return result;
        }
        template<typename T>
        std::vector<double> linspace(const T &start, const T &stop, const size_t &num)
        {
            std::vector<double> result;
            double start_d = static_cast<double>(start);
            double stop_d = static_cast<double>(stop);
            if (num == 0) { 
                return result;
            }
            else if (num == 1) {
                result.push_back(start_d);
                return result;
            }
            double delta = (stop_d - start_d) / (num - 1);
            for(int i=0; i < num - 1; ++i)
                result.push_back(start + delta * i);
            result.push_back(stop_d);
            return result;
        }
        template<typename T>
        std::vector<T> read_from_file(const std::string filename){
            std::ifstream file(filename.c_str());
            if (!file.is_open())
                throw std::runtime_error(((std::string)"error while opening file " + filename).c_str());
            std::istream_iterator<T> start_iter(file), end_iter;
            std::vector<T> results(start_iter, end_iter);
            file.close();
            return results;
        }
        
        template<typename T>
        std::vector<T> make_strictly_ascending(const std::vector<T> &vec, T epsilon){
            std::vector<T> results = vec;
            const int vec_size = vec.size();
            if ((vec_size == 0) || (vec_size == 1))
                return results;
            std::sort(results.begin(), results.end());
            for (int i = 1; i < vec_size; ++i){
                if (results[i - 1] >= results[i])
                    results[i] = results[i - 1] + epsilon;
            }
            return results;
        }
    };
    """
}

SUPPLEMENTARY_CPP_MACROS = \
{
   "PreprocessingUtils":
    """
       #include <cmath>
       #include <vector>
       #include <algorithm>
       #include <functional> 
       using namespace ROOT::Math;
       namespace PreprocessingUtils{
           class QuantileTransformer {
               public:
                   QuantileTransformer(const std::vector<double> &quantiles,const std::vector<double> &references,
                   const Interpolation::Type &interpType=Interpolation::Type::kLINEAR){
                       init(quantiles, references, interpType);
                    }
                   QuantileTransformer(const std::vector<double> &quantiles,
                   const Interpolation::Type &interpType=Interpolation::Type::kLINEAR){
                       init(quantiles, interpType);
                   }
                   QuantileTransformer(std::string quantile_filename, std::string reference_filename,
                   const Interpolation::Type &interpType=Interpolation::Type::kLINEAR){
                       init(quantile_filename, reference_filename, interpType);
                   }

                   QuantileTransformer(std::string filename,
                   const Interpolation::Type &interpType=Interpolation::Type::kLINEAR){
                       init(filename, interpType);
                   }

                   double transform(const double &value){
                       if (value <= m_quantiles.front())
                           return 0.;
                       else if (value >= m_quantiles.back())
                           return 1.;
                       return 0.5 * (m_interpolator->Eval(value) - m_compl_interpolator->Eval(-value));
                   }
               private:
                   void init(const std::vector<double> &quantiles, const std::vector<double> &references,
                             const Interpolation::Type &interpType=Interpolation::Type::kLINEAR){
                       m_quantiles = VecUtils::make_strictly_ascending(quantiles, 1e-10);
                       m_references = VecUtils::make_strictly_ascending(references, 1e-10);
                       if (!m_quantiles.size())
                           throw std::runtime_error("no quantiles defined");
                       if (m_quantiles.size() != m_references.size())
                           throw std::runtime_error("quantiles and references must have the same size");
                       const double epsilon = 1e-8;
                       if ((fabs(m_references.front() - 0) > epsilon * fabs(m_references.front())) ||
                           (fabs(m_references.back() - 1) > epsilon * fabs(m_references.back())))
                           throw std::runtime_error("quantile references must start with 0 and end with 1");
                       m_interpolator = std::unique_ptr<Interpolator>(new Interpolator(m_quantiles, m_references, interpType));
                       m_compl_quantiles = make_compl(m_quantiles);
                       m_compl_references = make_compl(m_references);
                       m_compl_interpolator = std::unique_ptr<Interpolator>(new Interpolator(m_compl_quantiles, m_compl_references, interpType));
                   }
                   void init(const std::vector<double> &quantiles,
                             const Interpolation::Type &interpType=Interpolation::Type::kLINEAR){
                       std::vector<double> references = VecUtils::linspace(0., 1., quantiles.size());
                       init(quantiles, references, interpType);
                   }
                   void init(std::string quantile_filename, std::string reference_filename,
                             const Interpolation::Type &interpType=Interpolation::Type::kLINEAR){
                       std::vector<double> quantiles = VecUtils::read_from_file<double>(quantile_filename);
                       std::vector<double> references = VecUtils::read_from_file<double>(reference_filename);
                       init(quantiles, references, interpType);
                   }
                   void init(std::string filename,
                             const Interpolation::Type &interpType=Interpolation::Type::kLINEAR){
                       std::vector<double> quantiles = VecUtils::read_from_file<double>(filename);
                       init(quantiles, interpType);
                   }
                   std::vector<double> make_compl(const std::vector<double>  &vec){
                       std::vector<double> result = vec;
                       std::reverse(result.begin(), result.end());
                       std::transform(result.cbegin(), result.cend(), result.begin(), std::negate<double>());
                       return result;
                   }
                   std::vector<double> m_quantiles;
                   std::vector<double> m_references;
                   std::vector<double> m_compl_quantiles;
                   std::vector<double> m_compl_references;
                   std::unique_ptr<Interpolator> m_interpolator;
                   std::unique_ptr<Interpolator> m_compl_interpolator;
           };
       };
    """,
   "XGBoostUtils": 
    """
    #include "xgboost/c_api.h"
    #include <vector>
    #include <string>
    #include <iostream>
    namespace XGBoostUtils{
        class XGBoostHandle {
            public:
                XGBoostHandle(const std::string &model_path, const bool &multithread=false, 
                              const bool &use_best_ntree_limit=false){
                    // load xgboost model
                    m_booster = std::unique_ptr<BoosterHandle>(new BoosterHandle());
                    XGBoosterCreate(0, 0, m_booster.get());
                    auto status = XGBoosterLoadModel(*m_booster.get(), model_path.c_str());
                    if (status != 0)
                        throw std::runtime_error(((std::string)"failed to load xgboost model from " + model_path).c_str());
                    // control multithreading
                    if (!multithread)
                        XGBoosterSetParam(*m_booster.get(), "nthread", "1");
                    if (use_best_ntree_limit){
                        const char* out;
                        int success;
                        XGBoosterGetAttr(*m_booster.get(), "best_iteration", &out, &success);
                        m_bst_ntree_limit = atoi(out);
                    }
                    else
                        m_bst_ntree_limit = 0;
                }
                
                std::vector<float> getWeightsFromDMatrix(std::vector<float> &vars, const int &size=1, int option_mask=0){
                    const int nvars = vars.size();
                    std::vector<float> weights = getWeightsFromDMatrix(vars.data(), nvars, size, option_mask);
                    return weights;
                }
                
                std::vector<float> getWeightsFromDMatrix(float* vars, const int nvars, const int &size=1, int option_mask=0){
                    DMatrixHandle dmat;
                    XGDMatrixCreateFromMat(vars, size, nvars, -1, &dmat);
                    bst_ulong out_len;
                    const float *f;
                    XGBoosterPredict(*m_booster.get(), dmat, option_mask, m_bst_ntree_limit, 0, &out_len, &f);
                    XGDMatrixFree(dmat);
                    std::vector<float> weights(size);
                    weights.assign(f, f + size);
                    return weights;
                }
                
                std::vector<float> getWeightsFromDense(std::vector<float> &vars, const int &size=1, int option_mask=0){
                    const int nvars = vars.size();
                    std::vector<float> weights = getWeightsFromDense(vars.data(), nvars, size, option_mask);
                    return weights;
                }

                std::vector<float> getWeightsFromDense(float* vars, const int nvars, const int &size=1, int option_mask=0){
                    const char str_format[] = "{\\"data\\": [%lu, true], \\"shape\\": [%lu, %lu], "
                                              "\\"typestr\\": \\"<f4\\", \\"version\\": 3}";
                    std::string config = (std::string)("{\\"type\\": " + std::to_string(option_mask) + 
                                                       ", \\"training\\": false, \\"iteration_begin\\": 0,"
                                                       "\\"iteration_end\\": 0, \\"strict_shape\\": true,"
                                                       "\\"cache_id\\": 0, \\"missing\\": NaN}");
                    char array_interface[256];
                    memset(array_interface, '\\0', sizeof(array_interface));
                    sprintf(array_interface, str_format, (size_t) vars, (size_t)size, (size_t)nvars);
                    const float *f;
                    bst_ulong out_len;
                    uint64_t const *out_shape;
                    XGBoosterPredictFromDense(*m_booster.get(), array_interface, config.c_str(), NULL,
                                              &out_shape, &out_len, &f);
                    std::vector<float> weights(size);
                    weights.assign(f, f + size);
                    return weights;
                }
            private:
                std::unique_ptr<BoosterHandle> m_booster;
                unsigned m_bst_ntree_limit;
        };
        
        std::vector<float> getXGBoostWeightsFromDMatrix(XGBoostHandle & handle, std::vector<float> &vars, const int &size=1){
            std::vector<float> result = handle.getWeightsFromDMatrix(vars, size);
            return result;
        }
        
        std::vector<float> getXGBoostWeightsFromDense(XGBoostHandle & handle, std::vector<float> &vars, const int &size=1){
            std::vector<float> result = handle.getWeightsFromDense(vars, size);
            return result;
        }
    };
    """
}

def load_macro(macro_name:str):
    expression = CPP_MACROS.get(macro_name, None)
    if expression is None:
        raise ValueError(f"`{macro_name}` is not a built-in quickstats cpp macro."
                         " Available macros are: {}".format(",".join(list(CPP_MACROS))))
    cpp_define(expression, macro_name)

def load_macros(macro_names:Optional[List[str]]=None):
    if macro_names is None:
        macro_names = list(CPP_MACROS)
    for macro_name in macro_names:
        load_macro(macro_name)