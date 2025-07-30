from typing import Optional, Union, List, Dict

import numpy as np

from quickstats import AbstractObject

class RootFindingAlgorithm(AbstractObject):

    @property
    def minimizer(self):
        return self._minimizer

    @property
    def poi(self):
        return self.minimizer.poi
        
    def __init__(self, name:str,
                 minimizer:"ExtendedMinimizer",
                 expansion_rate:float=0.1,
                 precision:float = 0.05,
                 rel_accuracy:float=0.005,
                 abs_accuracy:float=0.0005,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self._minimizer = minimizer
        self.name   = name
        self.status = None
        self.rel_accuracy = rel_accuracy
        self.abs_accuracy = abs_accuracy
        self.precision = precision
        self.expansion_rate = expansion_rate

    def update(self, kwargs:Dict):
        raise NotImplementedError

    def exit_criteria(self, kwargs:Dict):
        mu_guess, mu_err = kwargs['mu_guess'], kwargs['mu_err']
        criteria =  mu_err <= np.max(self.rel_accuracy * mu_guess, self.abs_accuracy)
        return criteria

    def convergence_criteria(self, kwargs:Dict):
        dnll_ref, eps = kwargs['dnll_ref'], kwargs['eps']
        criteria = np.abs(dnll_ref) < self.precision * eps
        return criteria

    def on_loop_begin(self, kwargs:Dict):
        vmin, vmax = kwargs['vmin'], kwargs['vmax']
        kwargs.update({
            'mu_guess' : 0.5 * (vmin + vmax),
            'mu_err'   : 0.5 * (vmax - vmin)
        })

    def on_loop_end(self, kwargs:Dict):
        pass

    def on_step_begin(self, kwargs:Dict):
        mu_guess = kwargs['mu_guess']
        self.expand_range(mu_guess)

    def on_step_end(self, kwargs:Dict):
        pass

    def expand_range(self, mu:float):
        if (mu >= self.poi.getMax()):
            self.poi.setMax(mu * (1 + self.expansion_rate))

    def run_step(self, kwargs:Dict):
        mu_guess = kwargs['mu_guess']
        self.poi.setVal(mu_guess)
        status = self.minimizer.minimize()
        nll_prefit = self.minimizer.nom_nll
        nll_postfit = self.minimizer.min_nll
        dnll_0   = nll_postfit - kwargs['nll_0']
        dnll_ref = nll_postfit - kwargs['nll_ref']
        kwargs.update({
            'status'      : status,
            'nll_prefit'  : nll_prefit,
            'nll_postfit' : nll_postfit,
            'dnll_0'      : dnll_0,
            'dnll_ref'    : dnll_ref
        })
        return kwargs

    def find_crossing(self, nll_0:float, nll_ref:float,
                      vmin:Optional[float]=None,
                      vmax:Optional[float]=None,
                      **kwargs):
        """
        nll_0   : unconditional NLL
        nll_ref : target NLL at 95% CL
        """
        self.poi.setConstant(True)
        from quickstats.utils.roofit_utils import switch_var_range
        with switch_var_range(self.poi, vmin, vmax):
            kwargs = {
                "step"      : 0,
                "nll_0"     : nll_0,
                "nll_ref"   : nll_ref,
                "vmin"      : self.poi.getMin(),
                "vmax"      : self.poi.getMax(),
                "eps"       : self.minimizer.config["eps"],
                "converged" : False,
                "status"    : None
            }
            self.stdout.info(f'Finding NLL crossing with the {self.name} method')
            self.on_loop_begin(kwargs)
            while (not self.exit_criteria(kwargs)):
                kwargs["step"] += 1
                self.on_step_begin(kwargs)
                self.run_step(kwargs)
                self.on_step_end(kwargs)
                kwargs["converegd"] = self.convergence_criteria(kwargs)
                if kwargs["converegd"]:
                    break
                self.update(kwargs)
            self.on_loop_end(kwargs)
        return kwargs

    def print_iteration_summary(self, attributes:List, kwargs:Dict):
        pass
        #self.stdout.info(f'Iteration {i}: \n'
        #                 f'\t{self.poi.GetName()} = {mu_guess}\n'
        #                 f'\tNLL_0     = {nll_0}\n'
        #                 f'\tNLL       = {nll}\n'
        #                 f'\tdNLL_0    = {dnll}\n'
        #                 f'\tdNLL_ref  = {dnll_ref}')