from quickstats import CaseInsensitiveStrEnum

# keywords
SELF_SYST_DOMAIN_KEYWORD = ":self:"
COMMON_SYST_DOMAIN_KEYWORD = ":common:"
NORM_SYST_KEYWORD = "yield"
SHAPE_SYST_KEYWORD = "shape"
PROCESS_KEYWORD = ":process:"
RESPONSE_KEYWORD = "response::"
OBSERVABLE_KEYWORD = ":observable:"
CATEGORY_KEYWORD = ":category:"

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

# data sources
class DataSourceType(CaseInsensitiveStrEnum):
    DATA_SOURCE_COUNTING = "counting"
    DATA_SOURCE_ASCII = "ascii"
    DATA_SOURCE_HISTOGRAM = "histogram"
    DATA_SOURCE_NTUPLE = "ntuple"
DATA_SOURCE_COUNTING = DataSourceType.DATA_SOURCE_COUNTING
DATA_SOURCE_ASCII = DataSourceType.DATA_SOURCE_ASCII
DATA_SOURCE_HISTOGRAM = DataSourceType.DATA_SOURCE_HISTOGRAM
DATA_SOURCE_NTUPLE = DataSourceType.DATA_SOURCE_NTUPLE

# pdfs
class PDFType(CaseInsensitiveStrEnum):
    PDF_USERDEF = "userdef"
    PDF_EXTERNAL = "external"
PDF_USERDEF = PDFType.PDF_USERDEF
PDF_EXTERNAL = PDFType.PDF_EXTERNAL

# constraints
class ConstrType(CaseInsensitiveStrEnum):
    CONSTR_GAUSSIAN = "gaus"
    CONSTR_LOGN = "logn"
    CONSTR_ASYM = "asym"
    CONSTR_DFD = "dfd"
CONSTR_GAUSSIAN = ConstrType.CONSTR_GAUSSIAN
CONSTR_LOGN = ConstrType.CONSTR_LOGN
CONSTR_ASYM = ConstrType.CONSTR_ASYM
CONSTR_DFD = ConstrType.CONSTR_DFD

class DataStorageType(CaseInsensitiveStrEnum):
    Tree      = 'tree'
    Vector    = 'vector'
    Composite = 'composite'

class ExternalModelActionType(CaseInsensitiveStrEnum):
    Item = 'item'
    Fix = 'fix'
    Rename = 'rename'
    ExtSyst = 'extsyst'
    
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
OBS_DATASET_NAME = "obsdata"
LUMI_NAME = "_luminosity"
NORM_PREFIX = "_norm"
XS_PREFIX = "_xs"
BR_PREFIX = "_br"
EFFICIENCY_PREFIX = "_eff"
ACCEPTANCE_PREFIX = "_A"
CORRECTION_PREFIX = "_C"
COMMON_SYST_DOMAIN_NAME = "_allproc_"
PRODTAG = "__prod"
BETATAG = "__beta"


COMBINED_PDF_NAME = "CombinedPdf"

#model sources
class ModelType(CaseInsensitiveStrEnum):
    USERDEF_MODEL = "userdef"
    EXTERNAL_MODEL = "external"
    HISTOGRAM_MODEL = "histogram"
USERDEF_MODEL = ModelType.USERDEF_MODEL
EXTERNAL_MODEL = ModelType.EXTERNAL_MODEL
HISTOGRAM_MODEL = ModelType.HISTOGRAM_MODEL

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