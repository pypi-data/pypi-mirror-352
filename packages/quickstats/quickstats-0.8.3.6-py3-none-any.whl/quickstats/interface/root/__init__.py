from quickstats.core.modules import require_module
require_module("ROOT")

from .macros import load_macros, load_macro
from .TObject import TObject
from .TArrayData import TArrayData
from .TMatrixSym import TMatrixSym
from .TH1 import TH1
from .TH2 import TH2
from .TF1 import TF1
from .TFile import TFile
from .TTree import TTree
from .TChain import TChain
from .RooAbsArg import RooAbsArg
from .RooRealVar import RooRealVar
from .RooAbsData import RooAbsData
from .RooDataSet import RooDataSet
from .RooDataHist import RooDataHist
from .RooCategory import RooCategory
from .RooAbsPdf import RooAbsPdf
from .RooArgSet import RooArgSet
from .RooWorkspace import RooWorkspace
from .RooMsgService import RooMsgService
from .ModelConfig import ModelConfig
from .RDataFrame import RDataFrame, RDataFrameBackend
from .RooFitResult import RooFitResult

load_macros()

from quickstats import load_corelib
load_corelib()