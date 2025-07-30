#include "RooFitExt.h"

using QStringUtils::join;
using QVecUtils::ptrToVec;
using QVecUtils::vecNumToStr;

namespace RooFitExt{

    std::vector<std::string> getArgNames(const RooAbsCollection& args){
        std::vector<std::string> names;
        names.reserve(args.size());
        for (const auto arg : args)
            names.emplace_back(arg->GetName());
        return names;
    }
        
    void unfoldProdPdfComponents(const RooProdPdf& prod_pdf, RooArgSet& components, int recursion_count,
                                const int& recursion_limit){
        
        if (recursion_count >= recursion_limit)
            throw std::runtime_error( "failed to unfold product pdf components: recusion limit reached" );

        const RooArgList & pdf_list = prod_pdf.pdfList();
        if (pdf_list.getSize() == 1)
            components.add(pdf_list);
        else{
            for (auto pdf : pdf_list){
                if (strcmp(pdf->ClassName(), "RooProdPdf") == 0)
                    unfoldProdPdfComponents(*((RooProdPdf*)pdf), components, recursion_count, recursion_limit);
                else
                    components.add(*pdf);
            }
        }
    }
    RooRealVar* isolateConstraintEx(const RooAbsPdf& pdf, const RooArgSet& constraints){
        RooArgSet* components =  pdf.getComponents();
        components->remove(pdf);
        if (components->getSize()){
            for (auto c1: *components){
                for (auto c2: *components){
                    if (c1 == c2)
                        continue;
                    if (c2->dependsOn(*c1))
                        components->remove(*c1);
                }
            }
            if (components->getSize() > 1)
                throw std::runtime_error("failed to isolate proper nuisance parameter");
            else if (components->getSize() == 1)
                return (RooRealVar*) components->first();
        }
        else
            return isolateConstraint(pdf, constraints);
        return NULL;
    }

    RooRealVar* isolateConstraint(const RooAbsPdf& pdf, const RooArgSet& constraints){
        for (auto np : constraints)
            if (pdf.dependsOn(*np))
                return (RooRealVar*) np;
        return NULL;        
    }
    ConstraintSet pairConstraints(const RooArgSet& constraintPdfs, const RooArgSet& nuisanceParams,
                                  const RooArgSet& globalObs){
        ConstraintSet ret;
        for (const auto pdf : constraintPdfs){
            RooArgSet* dependentNuis = pdf->getDependents(nuisanceParams);
            if ((dependentNuis->size() > 1) || (dependentNuis->size() == 0))
                throw std::runtime_error("failed to isolate proper nuisance parameter");
            RooArgSet* dependentGlobs = pdf->getDependents(globalObs);
            if ((dependentGlobs->size() > 1) || (dependentGlobs->size() == 0))
                throw std::runtime_error("failed to isolate proper global observables");
            ret.pdfs.add(*pdf);
            ret.nuis.add(*dependentNuis->first());
            ret.globs.add(*dependentGlobs->first());
        }
        return ret;
    }
    
    void unfoldConstraints(const RooArgSet& constraintPdfs, RooArgSet& observables,
                           RooArgSet& nuisanceParams, RooArgSet* unfoldedConstraintPdfs,
                           const std::vector<std::string>constrPdfClsList,
                           int recursion_count, const int& recursion_limit,
                           const bool& stripDisconnected){
        
        if (recursion_count >= recursion_limit)
            throw std::runtime_error( "failed to unfold constraints: recusion limit reached" );
        
        for (const auto pdf : constraintPdfs){
            bool isProperConstraintPdf = false;
            for (const auto class_name : constrPdfClsList){
                if (pdf->InheritsFrom(class_name.c_str())){
                    isProperConstraintPdf = true;
                    break;
                }
            }
            if (!isProperConstraintPdf){
                RooArgSet* allConstraints = ((RooAbsPdf *)pdf)->getAllConstraints(observables, nuisanceParams, stripDisconnected);
                unfoldConstraints(*allConstraints, observables, nuisanceParams, unfoldedConstraintPdfs,
                                  constrPdfClsList, recursion_count + 1, recursion_limit, stripDisconnected);
            }
            else
                unfoldedConstraintPdfs->add(*pdf);
        }
    }
    
    std::string formatFunctionStr(const std::string class_name, const std::string name, 
                                  const std::string formula_str){
        std::string ret = class_name + "::" + name + "[ " + formula_str + " ]";
        return ret;
    }
    std::string getFunctionStrRepr(RooFormulaVar &formula_var){
        std::string formula_str = RooFormulaVarExt::getFormulaStr(formula_var);
        const RooArgSet dependents = RooFormulaVarExt::getDependents(formula_var);
        for (unsigned int i = 0; i < dependents.size(); ++i) {
            const auto& var = dependents[i];
            std::stringstream regexStr;
            regexStr << "x\\[" << i << "\\]|@" << i;
            std::regex regex(regexStr.str());
            std::string replacement = var->GetName();
            formula_str = std::regex_replace(formula_str, regex, replacement);
        }
        std::string ret = formatFunctionStr(formula_var.ClassName(), formula_var.GetName(), formula_str );
        return ret;
    }
    std::string getFunctionStrRepr(RooProduct &product_func){
        const RooArgList components = product_func.components();
        std::string formula_str = "";
        unsigned int n_component = components.size();
        for (unsigned int i = 0; i < n_component; ++i) {
            const auto& var = components[i];
            formula_str += var.GetName();
            if (i != n_component - 1)
                formula_str += " * ";
        }
        std::string ret = formatFunctionStr(product_func.ClassName(), product_func.GetName(), formula_str);
        return ret;
    }
    
    std::string getCorrectPrintArgs(RooFormulaVar& arg){
        std::string dependent_str = "";
        std::string formula_str = RooFormulaVarExt::getFormulaStr(arg);
        const RooArgSet dependents = RooFormulaVarExt::getDependents(arg);
        unsigned int n_dependent = dependents.size();
        for (unsigned int i = 0; i < n_dependent; ++i) {
            const auto& var = dependents[i];
            dependent_str += var->GetName();
            if (i != n_dependent - 1)
                dependent_str += ",";
        }
        std::string args_str = "[ actualVars=(" + dependent_str + ") formula=\"" + formula_str + "\" ]";
        return args_str;
    }
    
    std::string getCorrectPrintArgs(RooStats::HistFactory::FlexibleInterpVar& arg){
        std::string var_str = "";
        const RooListProxy& variables = arg.variables();
        unsigned int n_variable = variables.size();
        for (unsigned int i = 0; i < n_variable; ++i) {
            const auto& var = variables[i];
            var_str += var.GetName();
            if (i != n_variable - 1)
                var_str += ",";
        }
        std::string args_str = "[ paramList=(" + var_str + ") ]";
        return args_str;
    }
    
    std::string getCorrectPrintArgs(RooHistFunc& arg){
        // dependent variables
        std::vector<std::string> depList = getArgNames(*arg.getVariables());
        // binnings
        RooDataHist dataHist = arg.dataHist();
        std::vector<std::string> binningList;
        for (auto & binning : dataHist.getBinnings()){
            std::vector<std::string> edgeList = vecNumToStr(ptrToVec(binning->array(), binning->numBoundaries()), 6);
            std::string binningStr = "{" + join(edgeList, ",") + "}";
            binningList.push_back(binningStr);
        }
        // nominal histogram
        #if ROOT_VERSION_CODE < ROOT_VERSION(6,26,00)
            std::string args_str = "[ binningList=(" + join(binningList, ",") + ") depList=(" + join(depList, ",")  + ") ]";
        #else
            std::vector<std::string> weightArray = vecNumToStr(ptrToVec(dataHist.weightArray(), dataHist.numEntries()), 6);
            std::string args_str = "[ nominalHist={" + join(weightArray, ",") 
                                   + "} binningList=(" + join(binningList, ",")
                                   + ") depList=(" + join(depList, ",")  + ") ]";
        #endif        
        
        return args_str;
    }
    
    std::string getCorrectPrintArgs(RooPrintable& arg){
        std::stringstream s;
        arg.printArgs(s);
        std::string ret = s.str();
        return ret;
    }

    std::string getCorrectPrintArgs(const PiecewiseInterpolation & arg){
        std::vector<std::string> lowList = getArgNames(arg.lowList());
        std::vector<std::string> highList = getArgNames(arg.highList());
        std::vector<std::string> paramList = getArgNames(arg.paramList());
        std::string nominal = arg.nominalHist()->GetName();
        std::string result = "[ nominal=" + nominal + " lowList=(" + join(lowList, ",")
                             + ") highList=(" + join(highList, ",") + ") paramList=("
                             + join(paramList, ",") + ") ]";
        return result;
    }
    
    std::string getPrintStr(RooAbsArg *printableObj, Int_t  contents, Int_t  style,
                            const TString &indent, const bool& strip_newline,
                            const bool& correction){
        std::stringstream s;
        if (contents < 0){
            Option_t *options= 0;
            contents = printableObj->defaultPrintContents(options);
        }
        if (style < 0){
            Option_t *options= 0;
            style = printableObj->defaultPrintStyle(options);
        }
        printableObj->printStream(s, contents, RooPrintable::StyleOption(style), indent);
        std::string ret = s.str();
        if (strip_newline)
            ret.erase(std::remove(ret.begin(), ret.end(), '\n'), ret.end());
        if (correction && (contents & RooPrintable::kArgs)){
            std::string class_name = printableObj->ClassName();
            std::string correct_args_str = "";
            if (class_name.compare("RooFormulaVar") == 0)
                correct_args_str = getCorrectPrintArgs(*((RooFormulaVar*) printableObj));
            else if (class_name.compare("RooStats::HistFactory::FlexibleInterpVar") == 0)
                correct_args_str = getCorrectPrintArgs(*((RooStats::HistFactory::FlexibleInterpVar*) printableObj));
            else if (class_name.compare("PiecewiseInterpolation") == 0)
                correct_args_str = getCorrectPrintArgs(*((PiecewiseInterpolation*) printableObj));
            else if (class_name.compare("RooHistFunc") == 0)
                correct_args_str = getCorrectPrintArgs(*((RooHistFunc*) printableObj));
            else
                return ret;
            // clear stringstream
            s.str("");            
            printableObj->printArgs(s);
            const std::string default_args_str = s.str();
            if (default_args_str.compare(correct_args_str) != 0)
                ret = (std::string) TString(ret).ReplaceAll(default_args_str, correct_args_str);
        }
        return ret;
    }
    
    RooArgSetStrData getStrData(RooArgSet & components, const bool& fill_classes,
                                const bool& fill_definitions, Int_t contents,
                                Int_t style, const TString &indent,
                                const bool& correction){
        unsigned int n_component = components.size();
        RooArgSetStrData ret(n_component);
        for (unsigned i=0; i < n_component; ++i){
            const auto& component = components[i];
            ret.names[i] = component->GetName();
            if (fill_classes)
                ret.classes[i] = component->ClassName();
            if (fill_definitions)
                ret.definitions[i] = getPrintStr(component, contents, style, indent, true, correction);     
        }
        return ret;
    }
};

