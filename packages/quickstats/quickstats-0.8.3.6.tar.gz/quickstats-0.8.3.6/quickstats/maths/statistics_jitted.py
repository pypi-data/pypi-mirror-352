from numba import jit, vectorize, int32, int64, float32, float64
import numpy as np

@vectorize(nopython=True)
def get_sys_rel_effect(nom_val, sys_val):
    if nom_val == 0.:
        return 0.
    return 100.*((sys_val/nom_val)-1.)

@vectorize(nopython=True)
def get_sys_err_rel_effect_full_corr(nom_val, nom_err, sys_val, sys_err):
    if nom_val == 0.:
        return 0.
    return 100*abs(nom_val*sys_err-sys_val*nom_err)/pow(nom_val, 2)

@vectorize(nopython=True)
def get_sys_err_rel_effect_part_corr(nom_val, common_nom_val, uncommon_nom_val,
                                     common_nom_err, uncommon_nom_err,
                                     uncomon_sys_val, uncomon_sys_err):
    if nom_val == 0.:
        return 0.
    return 100.*((1./nom_val)**2)*np.sqrt( 
                ((uncommon_nom_val - uncomon_sys_val)**2) * (common_nom_err**2) + \
                ((common_nom_val + uncomon_sys_val)**2) * (uncommon_nom_err**2) + \
                (nom_val**2) * (uncomon_sys_err**2))

@vectorize(nopython=True)
def get_sys_err_rel_effect_uncorr(nom_val, nom_err, sys_val, sys_err):
    if nom_val == 0.:
        return 0.
    return 100.*abs(sys_val/nom_val)* np.sqrt((nom_err/nom_val)**2 +(sys_err/sys_val)**2)

@jit(nopython=True)
def get_intersection(bin_content, bin_error, bin_center, threshold):
    q_central = q_low = q_high = 0
    found_central = found_low = found_high = False
    for i in range(len(bin_content)):
        if (found_low) and (found_central) and (found_high):
            break
        bin_val = bin_content[i]
        bin_err = bin_error[i]
        if (not found_low) and (bin_val + bin_err >= threshold):
            found_low = True
            q_low = bin_center[i]
        if (not found_central) and (bin_val >= threshold):
            found_central = True
            q_central = bin_center[i]
        if (not found_high) and (bin_val - bin_err >= threshold):
            found_high = True
            q_high = bin_center[i]
    return q_central, q_low, q_high

@jit(nopython=True)
def get_percentile_data(bin_content, bin_error, bin_center, percentile):
    bin_width = bin_center[1] - bin_center[0]
    q_central, q_low, q_high = get_intersection(bin_content, bin_error, bin_center, percentile)
    q_err = max(abs(q_central - q_low), abs(q_central - q_high))
    q_err = np.sqrt(q_err**2 + bin_width**2)
    return q_central, q_err

@jit(nopython=True)
def get_interquartile_data(bin_content, bin_error, bin_center):
    Q1_0_25_val, Q1_0_25_err = get_percentile_data(bin_content, bin_error, bin_center, 0.25)
    Q3_0_75_val, Q3_0_75_err = get_percentile_data(bin_content, bin_error, bin_center, 0.75)
    IQR_val = Q3_0_75_val - Q1_0_25_val
    IQR_err = np.sqrt(Q1_0_25_err**2 + Q3_0_75_err**2)
    return IQR_val, IQR_err
    
    
def get_rounded_extremal(value, mode):
    rounded = value
    dummy = 0
    while (int(rounded) == 0 and dummy < 10):
        rounded *= 10
        dummy += 1
    rounded = int(rounded)
    if (dummy < 10):
        if mode == "max":
            rounded += 1
        elif mode == "min":
            rounded -= 1
        rounded /= np.power(10, dummy)
    return rounded  

@jit(nopython=True)
def random_poisson_elementwise_seed(seeds, size):
    n_seed = seeds.shape[0]
    poisson_weights = np.zeros((size, n_seed), dtype=int64)
    for i, seed in enumerate(seeds):
        np.random.seed(seed % 4294967296)
        for j in range(size):
            poisson_weights[j, i] = np.random.poisson()
    return poisson_weights