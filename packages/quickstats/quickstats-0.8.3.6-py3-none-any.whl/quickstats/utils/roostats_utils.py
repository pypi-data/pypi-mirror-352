from typing import Optional, Union, List, Dict

import numpy as np
import ctypes
import cppyy
from cppyy.gbl.std import vector

from quickstats import DescriptiveEnum, cached_import

class PriorPdfType(DescriptiveEnum):
    NONE     = (0, "No prior")
    FLAT     = (1, "Uniform prior")
    UNIFORM  = (2, "Uniform prior")
    INV_SQRT = (3, "Reciprocal of square root of POI")

def get_null_distribution(htr:"ROOT.RooStats.HypoTestResult")->np.ndarray:
    return np.array(htr.GetNullDistribution().GetSamplingDistribution().data())

def get_alt_distribution(htr:"ROOT.RooStats.HypoTestResult")->np.ndarray:
    return np.array(htr.GetAltDistribution().GetSamplingDistribution().data())

def get_merged_null_distribution(htr_list:List["ROOT.RooStats.HypoTestResult"])->np.ndarray:
    return np.sort(np.concatenate(tuple([get_null_distribution(htr) for htr in htr_list])))

def get_merged_alt_distribution(htr_list:List["ROOT.RooStats.HypoTestResult"])->np.ndarray:
    return np.sort(np.concatenate(tuple([get_alt_distribution(htr) for htr in htr_list])))

def process_hypotest_results(htr_list:List["ROOT.RooStats.HypoTestResult"],
                             remove_unconverged_toys:bool=True, 
                             use_qmu:bool=False,
                             do_invert:bool=True):
    ROOT = cached_import("ROOT")
    if not isinstance(htr_list, list):
        htr_list = [htr_list]
    teststat_list = [htr.GetTestStatisticData() for htr in htr_list]
    if len(set(teststat_list)) > 1:
        raise RuntimeError("inconsistent test statistic values among hypotest results")
    teststat = teststat_list[0]
    if (teststat < 0.):
        print("WARNING: HypoTestResult has negative test statistic indicating a failed fit.")
    null_dist = get_merged_null_distribution(htr_list)
    alt_dist = get_merged_alt_distribution(htr_list)

    if remove_unconverged_toys:
        null_dist = null_dist[null_dist >= 0.]
        alt_dist  = alt_dist[alt_dist >= 0.]

    if use_qmu:
        null_dist *= 2
        alt_dist  *= 2
        teststat  *= 2
    null_dist_vec = vector['double'](null_dist)
    alt_dist_vec  = vector['double'](alt_dist)
    null_sampling_dist = ROOT.RooStats.SamplingDistribution("null_dist", "", null_dist_vec)
    alt_sampling_dist  = ROOT.RooStats.SamplingDistribution("alt_dist", "", alt_dist_vec)
    new_htr = htr_list[0].Clone()
    new_htr.SetNullDistribution(null_sampling_dist)
    new_htr.SetAltDistribution(alt_sampling_dist)
    new_htr.SetTestStatisticData(teststat)
    if do_invert:
        new_htr.SetBackgroundAsAlt()
    return new_htr

def merge_toy_results(results:List[Union["ROOT.RooStats.HypoTestInverterResult",
                      "ROOT.RooStats.HypoTestResult"]],
                      poi:Optional["ROOT.RooRealVar"]=None,
                      interpolation_method:Optional[int]=None,
                      remove_mu_with_failed_teststat:bool=True,
                      remove_unconverged_toys:bool=True, 
                      use_qmu:bool=True,
                      do_invert:bool=True,
                      silent:bool=False):
    ROOT = cached_import("ROOT")
    if interpolation_method is None:
        interpolation_method = ROOT.RooStats.HypoTestInverterResult.kLinear
    hypotest_inverter_results = [r for r in results if r.ClassName() == 'RooStats::HypoTestInverterResult']
    hypotest_results          = [r for r in results if r.ClassName() == 'RooStats::HypoTestResult']

    if (not hypotest_inverter_results) and (not hypotest_results):
        raise ValueError("toy results must be either instance of "
                         "RooStats::HypoTestInverterResult or RooStats::HypoTestResult")
    if poi is None:
        if len(hypotest_inverter_results) > 0:
            base_result = hypotest_inverter_results[0]
            poi = base_result.GetParameters().first()
        else:
            base_result = hypotest_results[0]
            poi_name    = '_'.join(base_result.GetName().split('_')[:-1])
            poi         = ROOT.RooRealVar(poi_name, poi_name, 0)
            print("WARNING: POI information not given. New POI variable will be constructed "
                  " using name inferred from toy result (\"{}\"={}[{}, {}]).".format(
                      poi_name, poi.getVal(), poi.getRange()[0], poi.getRange()[1]))
    merged_result = ROOT.RooStats.HypoTestInverterResult("merged_result", poi, 0.95)
    merged_result.SetConfidenceLevel(0.95)
    merged_result.UseCLs()
    merged_result.SetInterpolationOption(interpolation_method)
    if not silent:
        if interpolation_method == ROOT.RooStats.HypoTestInverterResult.kLinear:
            interpolation_str = "Linear"
        elif interpolation_method == ROOT.RooStats.HypoTestInverterResult.kSpline:
            interpolation_str = "Spline"        
        print("INFO: Constructing HypoTestInverterResult with the following settings")
        print("                  CL: 0.95")
        print("             Use CLs: True")
        print("Interpolation Method: {}".format(interpolation_str))
    temp_results = {}
    for result in hypotest_inverter_results:
        r_poi = result.GetParameters().first()
        if r_poi.GetName() != poi.GetName():
            raise RuntimeError("inconsistent POI used across toy results")
        for i in range(result.ArraySize()):
            htr = result.GetResult(i)
            mu = result.GetXValue(i)
            if mu not in temp_results:
                temp_results[mu] = []
            temp_results[mu].append(htr)
        
    for result in hypotest_results:
        try:
            mu = float(result.GetName().split('_')[-1])
        except Exception:
            raise RuntimeError("failed to extract mu value from HypoTestResult name "
                               "(expect <poi_name>_<mu_value>)")
        if mu not in temp_results:
            temp_results[mu] = []
        temp_results[mu].append(result)

    for mu, htr_list in temp_results.items():
        teststat_list = [htr.GetTestStatisticData() for htr in htr_list]
        if any(teststat < 0 for teststat in teststat_list) and remove_mu_with_failed_teststat:
            print(f"WARNING: Removed results from mu = {mu} due to negative teststat value")
            continue
        new_htr = process_hypotest_results(htr_list,
                  remove_unconverged_toys=remove_unconverged_toys, 
                  use_qmu=use_qmu,
                  do_invert=do_invert)
        merged_result.Add(mu, new_htr)
    return merged_result

def get_array_quantiles_deprecated(array):
    ROOT = cached_import("ROOT")
    import cppyy.ll
    q = cppyy.ll.array_new['double'](7)
    p = cppyy.ll.array_new['double'](7)
    p[0] = ROOT.Math.normal_cdf(-2)
    p[1] = ROOT.Math.normal_cdf(-1)
    p[2] = 0.5
    p[3] = ROOT.Math.normal_cdf(1)
    p[4] = ROOT.Math.normal_cdf(2)
    ROOT.TMath.Quantiles(len(array), 5, array, q, p, False)
    quantiles = {
        -2 : q[0],
        -1 : q[1],
         0 : q[2],
        +1 : q[3],
        +2 : q[4]
    }
    # free memory
    cppyy.ll.array_delete(p)
    cppyy.ll.array_delete(q)
    return quantiles

def get_array_quantiles(array):
    ROOT = cached_import("ROOT")
    q = [ROOT.Math.normal_cdf(-2), ROOT.Math.normal_cdf(-1), 0.5, ROOT.Math.normal_cdf(1), ROOT.Math.normal_cdf(2)]
    quantiles = np.quantile(array, q)
    quantiles_dict = {
        -2 : quantiles[0],
        -1 : quantiles[1],
         0 : quantiles[2],
        +1 : quantiles[3],
        +2 : quantiles[4]
    }
    return quantiles_dict


def get_hypotest_data(htr):
    ROOT = cached_import("ROOT")
    data = {}
    data['null'] = {
        'dist': htr.GetNullDistribution()
    }
    data['alt'] = {
        'dist': htr.GetAltDistribution()
    }
    for dtype in data:
        dist = data[dtype]['dist']
        data[dtype]['data'] = np.array(dist.GetSamplingDistribution().data())
        data[dtype]['weight'] = np.array(dist.GetSampleWeights().data())        
        data[dtype]['size'] = len(data[dtype]['data'])
        data[dtype]['xmin'] = np.min(data[dtype]['data'])
        data[dtype]['xmax'] = np.max(data[dtype]['data'])
    data['observed'] = {
        'teststat': htr.GetTestStatisticData(),
        'CLsplusb': htr.CLsplusb(),
        'CLsplusbError': htr.CLsplusbError(),
        'CLb': htr.CLb(),
        'CLbError': htr.CLbError(),
        'CLs': htr.CLs(),
        'CLsError': htr.CLsError(),
    }
    data['expected'] = {}
    # calculate expected intervals for teststat
    alt_data = data['alt']['dist'].GetSamplingDistribution().data()
    data['expected']['teststat'] = get_array_quantiles(alt_data)
    qmu_exp = data['expected']['teststat'][0]
    perror = ctypes.c_double()
    
    data['expected']['CLsplusb'] = data['null']['dist'].IntegralAndError(perror, qmu_exp, 
                                                                         ROOT.RooNumber.infinity(), 
                                                                         True, True, True)
    data['expected']['CLsplusbError'] = perror.value
    
    data['expected']['CLb'] = data['alt']['dist'].IntegralAndError(perror, qmu_exp, 
                                                                   ROOT.RooNumber.infinity(), 
                                                                   True, True, True)
    data['expected']['CLbError'] = perror.value
    
    if data['expected']['CLb'] == 0.:
        data['expected']['CLs'] = -1.
        data['expected']['CLsError'] = -1.
    else:
        data['expected']['CLs'] = data['expected']['CLsplusb'] / data['expected']['CLb']
        cl_b_err2 = pow(data['expected']['CLbError'], 2)
        cl_sb_err2 = pow(data['expected']['CLsplusbError'], 2)
        data['expected']['CLsError'] = np.sqrt(cl_sb_err2 + cl_b_err2 * pow(data['expected']['CLs'], 2)) / data['expected']['CLb']

    return data

def set_prior_pdf(ws: "ROOT.RooWorkspace",
                  mc: "ROOT.RooStats.ModelConfig",
                  pois: "ROOT.RooArgSet",
                  prior_type:Optional[Union[PriorPdfType, str]]="flat",
                  prior_name:str="prior_pdf"):
    ROOT = cached_import("ROOT")
    if prior_type is None:
        return
    try:
        prior_type = PriorPdfType.parse(prior_type)
    except Exception:
        pass
    if prior_type == PriorPdfType.NONE:
        return
    if prior_type in [PriorPdfType.UNIFORM, PriorPdfType.FLAT]:
        prior_pdf = ROOT.RooUniform(prior_name, prior_name, pois)
        ws.Import(prior_pdf)
        mc.SetPriorPdf(prior_pdf)
        return
    
    def set_prior_from_expr(expr:str):
        if len(pois) != 1:
            raise RuntimeError('number of POIs must be 1 when using the inverse square root prior')
        poi_name = pois.first().GetName()
        prior_expr = f"EXPR::{prior_name}(\"{expr}\",{poi_name})"
        ws.factory(prior_expr)
        prior_pdf = ws.pdf(prior_name)
        mc.SetPriorPdf(prior_pdf)
        
    if prior_type == PriorPdfType.INV_SQRT:
        set_prior_from_expr("1/sqrt(@0)")
    elif isinstance(prior_type, str) and ("@0" in prior_type):
        set_prior_from_expr(prior_type)
    elif (prior_type and ws.pdf(prior_type)):
        mc.SetPriorPdf(ws.pdf(prior_type))
    else:
        raise RuntimeError(f'unknown prior type: {prior_type}')