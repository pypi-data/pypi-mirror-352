from quickstats import DescriptiveEnum

class BumpHuntMode(DescriptiveEnum):
    Excess = ('excess', 'Bump hunt should look for excess in data')
    Deficit = ('deficit', 'Bump hunt should look for deficit in data')

class SignalStrengthScale(DescriptiveEnum):
    __aliases__ = {
        'lin': 'linear'
    }
    Linear = ('linear', 'The signal strength should vary according to a linear scale starting from str_min with a step of str_step')
    Log = ('log', 'The signal strength should vary according to a log scale starting from 10**str_min')

class AutoScanStep(DescriptiveEnum):
    Full = ('full', 'The scan window is shifted by a number of bins equal to its width')
    Half = ('half', 'The scan window is shifted by a number of bins equal to its max(1, width // 2)')