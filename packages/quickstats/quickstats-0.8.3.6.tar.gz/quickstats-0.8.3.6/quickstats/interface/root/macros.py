from typing import List, Optional

from quickstats.interface.cppyy.core import cpp_define
#from quickstats.utils.root_utils import declare_expression

ROOT_MACROS = \
{
    "TH1Utils":
    """
    namespace TH1Utils {
        template<typename T>
        std::vector<T> GetBinErrorArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinError(bin_index));
            return result;
        }

        template<typename T>
        std::vector<T> GetBinErrorUpArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinErrorUp(bin_index));
            return result;
        }

        template<typename T>
        std::vector<T> GetBinErrorLowArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinErrorLow(bin_index));
            return result;
        }

        template<typename T>
        std::vector<T> GetBinCenterArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinCenter(bin_index));
            return result;
        }

        template<typename T>
        std::vector<T> GetBinContentArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinContent(bin_index));
            return result;
        }
      
        template<typename T>
        std::vector<T> GetBinWidthArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinWidth(bin_index));
            return result;
        }

        template<typename T>
        std::vector<T> GetBinLowEdgeArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            // the + 1 is because number of bin low edges = number of bins + 1
            const size_t bin_max = n_bin + overflow_bin + 1;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinLowEdge(bin_index));
            return result;
        }
        
        template<typename T>
        int FindBinIndexByBinEdge(TH1* h, const T &bin_edge, const double &epsilon=1e-6)
        {
            const T first_edge = h->GetBinLowEdge(1);
            if ((bin_edge < first_edge) && abs(bin_edge - first_edge) > epsilon)
                return 0;
            auto nbins = h->GetNbinsX();
            const T last_edge = h->GetBinLowEdge(nbins);
            if ((bin_edge > last_edge) && abs(bin_edge - last_edge) > epsilon)
                return nbins + 1;
            for (size_t i = 1; i < nbins + 1; i++){
                const T edge_i = h->GetBinLowEdge(i);
                if (abs(bin_edge - edge_i) < epsilon)
                    return i;
            }
            return -1;
        }
    }; 
    """,
    "TF1Utils":
    """
    namespace TF1Utils {
        std::vector<double> GetRandomArray(TF1* f, const int &size, const double &xmin, const double &xmax){
            std::vector<double> result(size);
            for (size_t i = 0; i < size; i++)
                result[i] = f->GetRandom(xmin, xmax);
            return result;
        }
        std::vector<double> GetRandomArray(TF1* f, const int &size){
            std::vector<double> result(size);
            for (size_t i = 0; i < size; i++)
                result[i] = f->GetRandom();
            return result;
        }
    }; 
    """,    
    "TAxisUtils": 
    """
    namespace TAxisUtils{
        template<typename T>
        std::vector<T> GetBinLowEdgeArray(TAxis* ax, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = ax->GetNbins();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(ax->GetBinLowEdge(bin_index));
            return result;
        }
        template<typename T>
        std::vector<T> GetBinCenterArray(TAxis* ax, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = ax->GetNbins();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(ax->GetBinCenter(bin_index));
            return result;
        }
        template<typename T>
        std::vector<T> GetBinWidthArray(TAxis* ax, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = ax->GetNbins();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(ax->GetBinWidth(bin_index));
            return result;
        }
    };
    """,    
    "THistUtils": 
    """
    namespace THistUtils{
        template<typename T>
        std::vector<double> GetPoissonError(const std::vector<T> data, const double& nSigma=1, bool offset=true){
            Double_t ym, yp;
            auto inst = RooHistError::instance();
            const int data_size = data.size();
            std::vector<double> result(2*data_size);
            for (size_t i = 0; i < data_size; i++){
                if (Int_t(data[i] + 0.5) == 0) {
                    ym = 0;
                    double beta = ROOT::Math::erf(nSigma / sqrt(2.0));
                    double alpha = 1 - beta;
                    yp = ROOT::Math::gamma_quantile_c(alpha / 2., 1, 1);
                }
                else {
                    inst.getPoissonInterval(Int_t(data[i] + 0.5), ym, yp, nSigma);
                }
                result[i] = ym;
                result[data_size + i] = yp;
            }
            if (offset){
                for (size_t i = 0; i < data_size; i++){
                    result[i] = data[i] - result[i];
                    result[data_size + i] = result[data_size + i] - data[i];
                }
            }
            return result;
        }
    };
    """,
    "RFUtils":
    """
    #include <iostream>
    #include <fstream>
    //#include <chrono>
    //using std::chrono::high_resolution_clock;
    //using std::chrono::duration;
    //using std::chrono::milliseconds;

    namespace RFUtils{
        struct DatasetStruct {
          std::vector<double> observable_values;
          std::vector<double> weights;
          std::vector<std::string> category_labels;
          std::vector<int> category_index;
          DatasetStruct(const size_t &n_entries, const size_t &n_obs){
              observable_values = std::vector<double>(n_obs * n_entries);
              weights = std::vector<double>(n_entries);
              category_labels = std::vector<std::string>(n_entries);
              category_index = std::vector<int>(n_entries);
          }
        } ;
        
        RooCategory* GetDatasetCategory(const RooAbsData* dataset){
            RooCategory* category = 0;
            const RooArgSet* argset = dataset->get();
            for (auto &arg: *argset){
                if (strcmp(((RooAbsArg*)arg)->ClassName(), "RooCategory") == 0){
                    category = (RooCategory*) arg;
                    break;
                }
            }
            return category;
        }
        
        RooArgSet GetDatasetObservables(const RooAbsData* dataset){
            RooArgSet observables;
            const RooArgSet* argset = dataset->get();
            for (auto &arg: *argset){
                if (strcmp(((RooAbsArg*)arg)->ClassName(), "RooRealVar") == 0)
                    observables.add(*arg);
            }
            return observables;
        }
        
        DatasetStruct ExtractCategoryData(const RooAbsData* dataset, const RooArgSet* observables, const RooCategory* cat){
            const size_t n_entries = dataset->numEntries();
            const size_t n_obs = observables->size();
            DatasetStruct result(n_entries, n_obs);
            RooRealVar* obs;
            for (size_t i = 0; i < n_entries; i++){
                dataset->get(i);
                for (size_t j = 0; j < n_obs; j++)
                    result.observable_values[i + j * n_entries] = ((RooRealVar*)(*observables)[j])->getVal();
                result.weights[i] = dataset->weight();
                result.category_labels[i] = cat->getLabel();
                result.category_index[i] = cat->getIndex();
            }
            return result;
        }
        
        DatasetStruct ExtractData(const RooAbsData* dataset, const RooArgSet* observables){
            const size_t n_entries = dataset->numEntries();
            const size_t n_obs = observables->size();
            DatasetStruct result(n_entries, n_obs);
            RooRealVar* obs;
            for (size_t i = 0; i < n_entries; i++){
                dataset->get(i);
                for (size_t j = 0; j < n_obs; j++)
                    result.observable_values[i + j * n_entries] = ((RooRealVar*)(*observables)[j])->getVal();
                result.weights[i] = dataset->weight();
            }
            return result;
        }
        
         void CopyData(const RooAbsData* source, RooAbsData* target, const RooRealVar* source_var,
                       RooRealVar* target_var, RooRealVar* weight){
             for (size_t i = 0; i < source->numEntries(); i++){
                 source->get(i);
                 double weight_val = source->weight();
                 weight->setVal(weight_val);
                 target_var->setVal(source_var->getVal());
                 target->add(RooArgSet(*target_var, *weight), weight_val);
             }
        }
        
        std::vector<double> GetRooRealVarBinWidths(const RooRealVar* var){
            const size_t nbins = var->numBins();
            std::vector<double> result(nbins, 0);
            for (size_t i = 0; i < nbins; i++)
                result[i] = var->getBinWidth(i);
            return result;
        }
        
        template<typename T>
        std::vector<double> GetPdfValues(const RooAbsPdf* pdf,
                                         const RooArgSet* vars,
                                         const std::vector<T> &bin_centers){
            const auto pdf_obs = pdf->getObservables(*vars);
            const auto target_obs = pdf_obs->first();
            const size_t nbins = bin_centers.size();
            std::vector<double> result(nbins, 0);
            for (size_t i = 0; i < nbins; i++){
                ((RooRealVar*)target_obs)->setVal(bin_centers[i]);
                result[i] = pdf->getVal(pdf_obs);
            }
            return result;
        }
        
        struct RooArgSetInfo {
          std::vector<std::string> class_names;
          std::vector<std::string> names;
          RooArgSetInfo(const RooArgSet* argset){
            const size_t n_obj = argset->size();
            this->class_names = std::vector<std::string>(n_obj);
            this->names = std::vector<std::string>(n_obj);
            for (size_t i = 0; i < n_obj; i++){
                this->class_names[i] = ((TObject*)(*argset)[i])->ClassName();
                this->class_names[i] = ((TObject*)(*argset)[i])->GetName();
            }
          }
        };
        
        void FillDataSetValues(RooAbsData* dataset, RooRealVar* observable,
                               double *values, const size_t &size){
            RooArgSet row(*observable);
            for (size_t i = 0; i < size; i++){
                observable->setVal(values[i]);
                dataset->add(row);
            }
        }
        
        void FillWeightedDataSetValues(RooAbsData* dataset, RooRealVar* observable,
                                       double *values, const size_t &size, RooRealVar* weightVar=0){
            RooArgSet row(*observable);
            if (weightVar){
                row.add(*weightVar);
                for (size_t i = 0; i < size; i++){
                    observable->setVal(values[2 * i]);
                    weightVar->setVal(values[2 * i + 1]);
                    dataset->add(row, values[2 * i + 1]);
                }
            }
            else {
                for (size_t i = 0; i < size; i++){
                    observable->setVal(values[2 * i]);
                    dataset->add(row, values[2 * i + 1]);
                }
            }
        }
        
        double GetPdfExpectedEventsOverRange(RooAbsPdf* pdf, const RooArgSet* observables,
                                             double rangeLo, double rangeHi,
                                             bool normalize=false){
            RooArgSet* pdfObs = pdf->getObservables(observables);
            RooRealVar* targetObs = (RooRealVar*) pdfObs->first();
            double tempRangeLo = 0.;
            double tempRangeHi = 0.;
            bool modifiedRange = false;
            // save existing range
            if (targetObs->hasRange("temp")){
                tempRangeLo = targetObs->getMin("temp");
                tempRangeHi = targetObs->getMax("temp");
                modifiedRange = true;
            }
            targetObs->setRange("temp", rangeLo, rangeHi);
            double integral = pdf->createIntegral(*pdfObs, RooFit::NormSet(*pdfObs),
                                                  RooFit::Range("temp"))->getVal();
            if (modifiedRange)
                targetObs->setRange("temp", tempRangeLo, tempRangeHi);
            else
                targetObs->removeRange("temp");
            if (!normalize)
                integral *= pdf->expectedEvents(*pdfObs);
            return integral;
        }
        
        // here the dataset is meant to be varying the NP values
        std::vector<double> GetPdfExpectedEventsOverRangeAcrossDataset(RooAbsPdf* pdf, RooAbsData* dataset,
                                                                       const RooArgSet* observables,
                                                                       double rangeLo, double rangeHi,
                                                                       bool normalize=false){
            const size_t numEntries = dataset->numEntries();
            std::vector<double> integrals(numEntries);
            RooArgSet* pdfObs = pdf->getObservables(observables);
            RooArgSet* pdfDataSetObs = pdf->getObservables(dataset->get());
            RooRealVar* targetObs = (RooRealVar*) pdfObs->first();
            double tempRangeLo = 0.;
            double tempRangeHi = 0.;
            bool modifiedRange = false;
            // save existing range
            if (targetObs->hasRange("temp")){
                tempRangeLo = targetObs->getMin("temp");
                tempRangeHi = targetObs->getMax("temp");
                modifiedRange = true;
            }
            targetObs->setRange("temp", rangeLo, rangeHi);
            for (size_t i = 0; i < numEntries; i++){
                *pdfDataSetObs = *dataset->get(i);
                double integral = pdf->createIntegral(*pdfObs, RooFit::NormSet(*pdfObs),
                                                      RooFit::Range("temp"))->getVal();
                if (!normalize)
                    integral *= pdf->expectedEvents(*pdfObs);
                integrals[i] = integral;
            }

            if (modifiedRange)
                targetObs->setRange("temp", tempRangeLo, tempRangeHi);
            else
                targetObs->removeRange("temp");
            return integrals;
        }
        
        // here the dataset is meant to be varying the observable values
        // not normalized by bin width!
        std::vector<double> GetPdfValuesAcrossObsDataset(RooAbsPdf* pdf, RooAbsData* dataset,
                                                         bool normalize=true){
            const size_t numEntries = dataset->numEntries();
            std::vector<double> values(numEntries);
            RooArgSet* pdfObs = pdf->getObservables(dataset->get());
            for (auto const& obs: *pdfObs)
                obs->recursiveRedirectServers(*pdfObs, false, false, false);
            RooArgSet projectedVars;
            RooArgSet* cloneSet = nullptr;
            const RooAbsReal *projected = pdf->createPlotProjection(*pdfObs, projectedVars, cloneSet);
            double scale_factor = 1.;
            if (normalize)
                scale_factor = pdf->expectedEvents(*pdfObs);
            for (size_t i = 0; i < numEntries; i++){
                // faster than
                // pdfObs->assignFast(*dataset->get(i));
                for (auto const& x : *dataset->get(i))
                    ((RooRealVar*)(pdfObs->find(x->GetName())))->setVal(((RooRealVar*)x)->getVal());
                values[i] = projected->getVal() * scale_factor;
            }
            delete cloneSet;
            return values;
        }

        RooCurve *createErrorBandFromArrayData(RooCurve* centralCurve, const std::vector<double> &data,
                                               const double &Z=1){
            vector<RooCurve*> variations;
            for (size_t i = 0; i < data.size(); i++){
                RooCurve *curve = new RooCurve();
                curve->addPoint(0, data[i]);
                variations.push_back(curve);
            }
            RooCurve *errorBand = centralCurve->makeErrorBand(variations, Z);
            return errorBand;
        }
        
        void GetProdPdfBaseComponents(RooProdPdf* pdf, RooArgSet* components) {
            RooArgList pdfList = pdf->pdfList();
            
            // Handle single component case
            if (pdfList.getSize() == 1) {
                components->add(pdfList);
                return;
            }
            
            // Iterate through components using range-based for loop
            for (const auto& componentObj : pdfList) {
                const RooAbsArg* component = static_cast<const RooAbsArg*>(componentObj);
                
                // Check if component is a RooProdPdf
                if (std::string(component->ClassName()) == "RooProdPdf") {
                    if (auto* nestedPdf = dynamic_cast<RooProdPdf*>(const_cast<RooAbsArg*>(component))) {
                        GetProdPdfBaseComponents(nestedPdf, components);
                    }
                } else {
                    components->add(*component);
                }
            }
        }
        
        RooArgSet GetConstantParameters(RooArgSet* args, bool isConstant=true){
            RooArgSet result;
            for (auto const *arg: *args)
                if (((RooRealVar*)arg)->isConstant() == isConstant)
                    result.add(*arg);
            return result;
        }
        
        bool ParameterCloseToMin(RooRealVar* param, float threshold=0.1){
            if ((!param->hasMin()) || (!param->hasMax()))
                return false;
            return param->getVal() < ((1. - threshold) * param->getMin() + threshold * param->getMax());
        }
        
        bool ParameterCloseToMax(RooRealVar* param, float threshold=0.1){
            if ((!param->hasMin()) || (!param->hasMax()))
                return false;
            return param->getVal() > ((1. - threshold) * param->getMax() + threshold * param->getMin());
        }
        
        bool ParameterCloseToBoundary(RooRealVar* param, float threshold=0.1){
            return ParameterCloseToMin(param, threshold) || ParameterCloseToMax(param, threshold);
        }
        
        RooArgSet GetParametersCloseToMin(RooArgSet* args, float threshold=0.1){
            RooArgSet result;
            for (auto const *arg: *args)
                if (ParameterCloseToMin((RooRealVar*)arg), threshold)
                    result.add(*arg);
            return result;
        }
        
        RooArgSet GetParametersCloseToMax(RooArgSet* args, float threshold=0.1){
            RooArgSet result;
            for (auto const *arg: *args)
                if (ParameterCloseToMax((RooRealVar*)arg), threshold)
                    result.add(*arg);
            return result;
        }
        
        RooArgSet GetParametersCloseToBoundary(RooArgSet* args, float threshold=0.1){
            RooArgSet result;
            for (auto const *arg: *args)
                if (ParameterCloseToBoundary((RooRealVar*)arg), threshold)
                    result.add(*arg);
            return result;
        }
        
        void ExpandParametersRange(RooArgSet* args, float threshold=0.1,
                                   bool expand_min=true, bool expand_max=true,
                                   RooArgSet* outOrigArgsAtMin=nullptr,
                                   RooArgSet* outNewArgsAtMin=nullptr,
                                   RooArgSet* outOrigArgsAtMax=nullptr,
                                   RooArgSet* outNewArgsAtMax=nullptr){
            for (auto *arg: *args){
                RooRealVar* param = dynamic_cast<RooRealVar*>(arg);
                if (!param)
                    continue;
                if (expand_min && ParameterCloseToMin(param, threshold)){
                    const double val = param->getVal();
                    if (outOrigArgsAtMin != nullptr)
                        outOrigArgsAtMin->add(*(RooRealVar*)param->Clone());
                    param->setMin(val - (param->getMax() - val));
                    if (outNewArgsAtMin != nullptr)
                        outNewArgsAtMin->add(*(RooRealVar*)param->Clone());
                }
                else if (expand_max && ParameterCloseToMax(param, threshold)){
                    const double val = param->getVal();
                    if (outOrigArgsAtMax != nullptr)
                        outOrigArgsAtMax->add(*(RooRealVar*)param->Clone());
                    param->setMax(val + (val - param->getMin()));
                    if (outNewArgsAtMax != nullptr)
                        outNewArgsAtMax->add(*(RooRealVar*)param->Clone());
                }
            }
        }
        
        bool ParameterAtBoundary(RooRealVar* param, float nsigma=1.0){
            const double value = param->getVal();
            return ((value - param->getMin()) < nsigma * -1. * param->getErrorLo()) ||
                   ((param->getMax() - value) < nsigma * param->getErrorHi());
        }
        
        RooArgSet GetBoundaryParameters(RooArgSet* args){
            RooArgSet result;
            for (auto const *arg: *args)
                if (ParameterAtBoundary((RooRealVar*)arg))
                    result.add(*arg);
            return result;
        }
        
        RooArgSet SelectByClass(RooArgSet* args, const char* classname){
            RooArgSet result;
            for (auto const *arg: *args)
                if (arg->InheritsFrom(classname))
                    result.add(*arg);
            return result;
        }
        
        RooArgSet ExcludeByClass(RooArgSet* args, const char* classname){
            RooArgSet result;
            for (auto const *arg: *args)
                if (!arg->InheritsFrom(classname))
                    result.add(*arg);
            return result;
        }
        
        RooArgSet SelectDependentParameters(RooArgSet* args, RooAbsArg* source){
            RooArgSet result;
            for (auto const *arg: *args)
                if (source->dependsOn(*arg))
                    result.add(*arg);
            return result;
        }
        
        RooArgSet GetRooArgSetDifference(RooArgSet* args1, RooArgSet* args2){
            RooArgSet result;
            for (auto const *arg: *args1)
                if (!args2->find(*arg))
                    result.add(*arg);
            return result;
        }

        template<typename T>
        int SetCategoryIndices(RooArgList* cats, std::vector<T> *indices){
            int changedIndex = -1;
            if (cats->size() != indices->size())
                throw std::runtime_error("category index size mismatch");
            for (size_t i = 0; i < indices->size(); ++i){
                RooCategory* cat = dynamic_cast<RooCategory*>(cats->at(i));
                if (!cat)
                    throw std::runtime_error("encountered non-RooCategory instance");
                if (cat->getIndex() != indices->at(i)){
                    changedIndex = i;
                    cat->setIndex(indices->at(i));
                }
            }
            return changedIndex;
        }

        void SaveRooArgSetDataAsTxt(const RooArgSet *args, const std::string &filename, size_t precision=8){
            std::ofstream outfile(filename, std::ofstream::trunc);
            for (auto arg: *args){
                RooRealVar* v = dynamic_cast<RooRealVar*>(arg);
                if (v)
                    outfile << v->GetName() <<" "<<std::fixed<<std::setprecision(precision)<<v->getVal()<<" "<<v->isConstant()<<" "<<
                    std::fixed<<std::setprecision(precision)<<v->getMin()<<" "<<
                    std::fixed<<std::setprecision(precision)<<v->getMax()<<std::endl;
                else{
                    RooCategory* cat = dynamic_cast<RooCategory*>(arg);
                    if (cat)
                        outfile<<cat->GetName()<<" "<<cat->getCurrentIndex()<<" "<<cat->isConstant()<<std::endl;
                }
            }
            outfile.close();
        }
        
        #if ROOT_VERSION_CODE >= ROOT_VERSION(6,26,0)
        #endif
    };
    """
}

def load_macro(macro_name:str):
    expression = ROOT_MACROS.get(macro_name, None)
    if expression is None:
        raise ValueError(f"`{macro_name}` is not a built-in quickstats macro."
                         " Available macros are: {}".format(",".join(list(ROOT_MACROS))))
    cpp_define(expression, macro_name)

def load_macros(macro_names:Optional[List[str]]=None):
    if macro_names is None:
        macro_names = list(ROOT_MACROS)
    for macro_name in macro_names:
        load_macro(macro_name)