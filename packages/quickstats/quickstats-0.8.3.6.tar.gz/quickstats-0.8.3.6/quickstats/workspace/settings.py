from quickstats import CaseInsensitiveStrEnum, DescriptiveEnum

# keywords
SELF_SYST_DOMAIN_KEYWORD = ":self:"
COMMON_SYST_DOMAIN_KEYWORD = ":common:"
PROCESS_KEYWORD = ":process:"
RESPONSE_KEYWORD = "response::"
OBSERVABLE_KEYWORD = ":observable:"
CATEGORY_KEYWORD = ":category:"

NORM_SYST_KEYWORD = "yield"
SHAPE_SYST_KEYWORD = "shape"

# logic operations
LT_OP = ":lt:"
LE_OP = ":le:"
GT_OP = ":gt:"
GE_OP = ":ge:"
AND_OP = ":and:"
OR_OP = ":or:"

class AnalysisType(CaseInsensitiveStrEnum):
    Shape = 'shape'
    Counting = 'counting'
SHAPE_ANALYSIS = AnalysisType.Shape.value
COUNTING_ANALYSIS = AnalysisType.Counting.value

# data sources
class DataSourceType(CaseInsensitiveStrEnum):
    DATA_SOURCE_COUNTING = "counting"
    DATA_SOURCE_ASCII = "ascii"
    DATA_SOURCE_HISTOGRAM = "histogram"
    DATA_SOURCE_NTUPLE = "root"
    DATA_SOURCE_ARRAY = "array"
DATA_SOURCE_COUNTING = DataSourceType.DATA_SOURCE_COUNTING.value
DATA_SOURCE_ASCII = DataSourceType.DATA_SOURCE_ASCII.value
DATA_SOURCE_HISTOGRAM = DataSourceType.DATA_SOURCE_HISTOGRAM.value
DATA_SOURCE_NTUPLE = DataSourceType.DATA_SOURCE_NTUPLE.value
DATA_SOURCE_ARRAY = DataSourceType.DATA_SOURCE_ARRAY.value

# pdfs
class PDFType(CaseInsensitiveStrEnum):
    PDF_USERDEF = "userdef"
    PDF_EXTERNAL = "external"
PDF_USERDEF = PDFType.PDF_USERDEF.value
PDF_EXTERNAL = PDFType.PDF_EXTERNAL.value

# constraints
class ConstrType(CaseInsensitiveStrEnum):
    CONSTR_GAUSSIAN = "gaus"
    CONSTR_LOGN = "logn"
    CONSTR_ASYM = "asym"
    CONSTR_DFD = "dfd"
CONSTR_GAUSSIAN = ConstrType.CONSTR_GAUSSIAN.value
CONSTR_LOGN = ConstrType.CONSTR_LOGN.value
CONSTR_ASYM = ConstrType.CONSTR_ASYM.value
CONSTR_DFD = ConstrType.CONSTR_DFD.value

class DataStorageType(CaseInsensitiveStrEnum):
    Tree      = 'tree'
    Vector    = 'vector'
    Composite = 'composite'

class ExternalModelActionType(CaseInsensitiveStrEnum):
    Item = 'item'
    Fix = 'fix'
    Rename = 'rename'
    ExtSyst = 'extsyst'
EXT_MODEL_ACTION_ITEM = ExternalModelActionType.Item.value
EXT_MODEL_ACTION_FIX = ExternalModelActionType.Fix.value
EXT_MODEL_ACTION_RENAME = ExternalModelActionType.Rename.value
EXT_MODEL_ACTION_EXTSYST = ExternalModelActionType.ExtSyst.value

class SampleFactorType(DescriptiveEnum):
    NormFactor  = (0, "Normalization factor")
    ShapeFactor = (1, "Shape factor")
    
# naming
RESPONSE_PREFIX = "expected__"
CONSTRTERM_PREFIX = "constr__"
GLOBALOBS_PREFIX = "RNDM__"
VARIATIONHI_PREFIX = "varHi__"
VARIATIONLO_PREFIX = "varLo__"
YIELD_PREFIX = "yield__"
PDF_PREFIX = "pdf__"
EXPECTATION_PREFIX = "expectation__"
UNCERT_HI_PREFIX = "uncertHi__"
UNCERT_LO_PREFIX = "uncertLo__"
UNCERT_SYM_PREFIX = "uncertSymm__"
SUM_PDF_NAME = "_modelSB"
FINAL_PDF_NAME = "_model"
CATEGORY_STORE_NAME = "channellist"
OBS_DATASET_NAME = "obsdata"
LUMI_NAME = "_luminosity"
NORM_PREFIX = "_norm"
XS_PREFIX = "_xs"
BR_PREFIX = "_br"
EFFICIENCY_PREFIX = "_eff"
ACCEPTANCE_PREFIX = "_A"
CORRECTION_PREFIX = "_C"
COMMON_SYST_DOMAIN_NAME = "_allproc_"

COMBINED_PDF_NAME = "CombinedPdf"

#model sources
class ModelType(CaseInsensitiveStrEnum):
    USERDEF_MODEL = "userdef"
    EXTERNAL_MODEL = "external"
    HISTOGRAM_MODEL = "histogram"
    COUNTING_MODEL = "counting"
USERDEF_MODEL = ModelType.USERDEF_MODEL.value
EXTERNAL_MODEL = ModelType.EXTERNAL_MODEL.value
HISTOGRAM_MODEL = ModelType.HISTOGRAM_MODEL.value
COUNTING_MODEL = ModelType.COUNTING_MODEL.value

#blinding
RANGE_NAME_SB_LO = "SBLo"
RANGE_NAME_SB_HI = "SBHi"
RANGE_NAME_BLIND = "Blind"

# variable sets
OBS_SET = "Observables"
POI_SET = "POI"
NUIS_SET = "nuisanceParameters"
GLOB_SET = "globalObservables"
CONSTR_SET = "constraintPdfs"

# asimov generation
GEN_ASIMOV_ACTION = "genasimov"
FLOAT_ASIMOV_ACTION = "float"
RAW_ASIMOV_ACTION = "raw"
FIT_ASIMOV_ACTION = "fit"
RESET_ASIMOV_ACTION = "reset"
FIX_SYST_ASIMOV_ACTION = "fixsyst"
FIX_ALL_ASIMOV_ACTION = "fixall"
MATCH_GLOB_ASIMOV_ACTION = "matchglob"
SAVE_SNAPSHOT_ASIMOV_ACTION = "savesnapshot"

OTHER = "other"

class SystematicType(DescriptiveEnum):
    Norm  = (0, "Normalization sysetmatic", NORM_SYST_KEYWORD)
    Shape = (1, "Shape systematic", SHAPE_SYST_KEYWORD)
    Other = (2, "Unclassified systematic type", OTHER)
    
    def __new__(cls, value:int, description:str, keyword:str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.keyword = keyword
        return obj

class ConstraintType(DescriptiveEnum):
    LogN  = (0, "Lognormal constraint", CONSTR_LOGN, 1)
    Asym  = (1, "Asymmetric constraint", CONSTR_ASYM, 4)
    Gaus  = (2, "Gaussian constraint", CONSTR_GAUSSIAN, 0)
    DFD   = (3, "Double Fermi-Dirac", CONSTR_DFD, 0)
    Other = (4, "Unclassified constraint type", OTHER, -1)
    
    def __new__(cls, value:int, description:str, keyword:str, interp_code:int):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.keyword = keyword
        obj.interp_code = interp_code
        return obj

class AsimovAlgorithmType(CaseInsensitiveStrEnum):
    ROOSTATS = "roostats"
    QUICKSTATS = "quickstats"
ASIMOV_ALGO_ROOSTATS = AsimovAlgorithmType.ROOSTATS.value
ASIMOV_ALGO_QUICKSTATS = AsimovAlgorithmType.QUICKSTATS.value