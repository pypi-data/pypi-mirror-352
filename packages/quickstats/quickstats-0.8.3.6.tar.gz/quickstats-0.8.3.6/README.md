# Setup

Clone the repository:
```
git clone ssh://git@gitlab.cern.ch:7999/clcheng/quickstats.git
```

### 1. CERN User

To set up from lxplus, just do
```
source setup.sh
```

### 2. Genearl User

To set up locally, make sure you have pyROOT 6.24+ installed (using conda is recommended), and do
```
pip install quickstats
```

### Installing pyROOT

Simplest way to install pyROOT is via conda
```
conda install -c conda-forge ROOT
```

## Important: First-time compilation

To compile c++ dependencies, do this for first time use
```
quickstats compile
```

# Command Line Tools

## Run Nuisance Parameter Pulls and Ranking
```
quickstats run_pulls -i <input_ws_path> -d <dataset_name> -p <np_name/pattern> --poi <poi_name> --parallel -1 -o <output_dir>
```

The following options are available

| **Option** | **Description** | **Default** |
| ---------- | ---------- | ----------- | 
| `-i/--input_file` | Path to the input workspace file | - |
| `-w/--workspace` | Name of workspace. Auto-detect by default. | None |
| `-m/--model_config` | Name of model config. Auto-detect by default. | None |
| `-d/--data` | Name of dataset | "combData" |
| `-p/--parameter` | Nuisance parameter(s) to run pulls on. Multiple parameters are separated by commas. Wildcards are accepted. All NPs will be run over by default| "" |
| `-x/--poi` | POIs to measure. If empty, impact on POI will not be calculated. | "" |
| `-r/--profile` | Parameters to profile | "" |
| `-f/--fix` | Parameters to fix | "" |
| `-s/--snapshot` | Name of initial snapshot | "nominalNuis" |
| `-o/--outdir` | Output directory | "pulls" |
| `-t/--minimizer_type` | Minimizer type | "Minuit2" |
| `-a/--minimizer_algo` | Minimizer algorithm | "Migrad" |
| `-c/--num_cpu` | Number of CPUs to use per parameter | 1 |
| `--binned/--unbinned` | Whether to use binned likelihood | True |
| `-q/--precision` | Precision for scan | 0.001 |
| `-e/--eps` | Tolerance | 1.0 |
| `-l/--log_level` | Log level | "INFO" |
| `--eigen/--no-eigen` | Compute eigenvalues and vectors | False |
| `--strategy`  | Default fit strategy | 0 |
| `--fix-cache/--no-fix-cache` | Fix StarMomentMorph cache | True |
| `--fix-multi/--no-fix-multi` |  Fix MultiPdf level 2 | True |
| `--offset/--no-offset` | Offset likelihood | True |
| `--optimize/--no-optimize` | Optimize constant terms | True |
| `--max_calls` | Maximum number of function calls | -1 |
| `--max_iters` | Maximum number of Minuit iterations | -1 |
| `--parallel` | Parallelize job across different nuisanceparameters using N workers. Use -1 for N_CPU workers. | 0 |
| `--cache/--no-cache` | Cache existing result | True |
| `--exclude` | Exclude NPs (wildcard is accepted) | "" |

## Plot Nuisance Parameter Pulls and Ranking

```
quickstats plot_pulls --help
```

## Likelihood Fit (Best-fit)
```
quickstats likelihood_fit --help
```

## Run Likelihood Scan

```
quickstats likelihood_scan --help
```

## Asymptotic CLs Limit

```
quickstats cls_limit --help
```

## CLs Limit Scan

```
quickstats limit_scan --help
```


## Generate Asimov dataset
```
quickstats generate_standard_asimov --help
```

## Inspect Workspace
```
quickstats inspect_workspace --help
```

## Create Workspace from XML Cards
```
quickstats build_xml_ws --help
```


## Modify Workspace from XML Cards or Json Config
```
quickstats modify_ws --help
```


## Combine Workspace from XML Cards or Json Config
```
quickstats combine_ws --help
```

## Compare Workspaces
```
quickstats compare_ws --help
```

## Run Event Loop from Custom Config File
```
quickstats process_rfile --help
```


## Syntax for setting parameter values

One may modify the values and/or range of variables in a ROOT workspace via a so-called parameter expression. This is used in the class `AnalysisBase` (or `ExtendedModel`) via the method `set_parameters`, or through the CLIs `likelihood_fit`, `likelihood_scan`, `significance_scan`, `cls_limit`, `limit_scan` via the arguments `--fix` and `--profile`. 

A parameter expression is a comma-separated string with the general syntax "\<parameter_name\>=\<value_expression\>,...". Here, \<parameter_name\> can be a string that matches the name of a given variable in the workspace, or a wildcard pattern that matches a collection of variables. There are also special magic keywords that allows matching a specific type of variables via the use of angular brackets. Currently, the following special keywords are supported:

- `<poi>`: matches all Parameters of Interests (POIs)
- `<global_observable>`: matches all Global Observables (GOs)
- `<nuisance_parameter>`: matches all Nuisance Parameters (NPs)
- `<constrained_nuisance_parameter>`: matches all NPs with associated constraint pdfs
- `<unconstrained_nuisance_parameter>`: matches all NPs without associated constraint pdfs
- `<gaussian_constraint_np>`: matches all NPs with Gaussian constraint pdfs
- `<poisson_constraint_np>`: matches all NPs with Poisson constraint pdfs

The \<value_expression\> supports the following syntax:

- Set only the nominal value: `"<parameter_name>=<nominal_value>"`
- Set only the range: `"<parameter_name>=<min_value>_<max_value>"`
- Set both nominal value and range: `"<parameter_name>=<nominal_value>_<min_value>_<max_value>"`
- Set nominal value, range, and error: `"<parameter_name>=<nominal_value>_<min_value>_<max_value>_<error_value>"`

Note that one can ommit values if you do not want to modify a particular data, i.e.:

- Set only the nominal value and the minimal range: `"<parameter_name>=<nominal_value>_<min_value>_"`
- Set only the error value: `"<parameter_name>=___<error_value>"`

Additional, if you want to change only the state of the variable(s), you may completely ommit the value expression. The state can be controlled via the `mode` argument in `set_parameters` if you are using the API. Or through the use of `--fix` (variables marked as constant) or `--profile` (variables marked as floating) if you are using the CLI.

Some CLI examples:

- Fixing the values of all NPs starting with the substring "ATLAS_" to 0 and those with substring "CMS_" to 1: `--fix "ATLAS_*=0",CMS_*=1"`
- Fixing (Floating) the values of all constrained (unconstrained) NPs: `--fix "<constrained_nuisance_parameter>" --profile "<unconstrained_nuisance_parameter>"`
- Float all POIs and setting their range to be \[-10, 10\] with value 1: `--profile "<poi>=1_-10_10"`

Some API examples:

- Fixing the values of all NPs starting with the substring "ATLAS_" to 0 and those with substring "CMS_" to 1: `analysis.set_parameters("ATLAS_*=0,CMS_*=1", mode="fix")`
- Floating all constrained NPs: `analysis.set_parameters("<constrained_nuisance_parameters>", mode="float")`
- Set all POIs' range to be \[-10, 10\] with value 1: `analysis.set_parameters("<poi>=1_-10_10", mode="unchanged")`