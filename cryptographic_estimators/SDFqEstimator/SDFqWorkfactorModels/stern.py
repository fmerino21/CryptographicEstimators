import collections
from .scipy_model import ScipyModel
from ..sdfq_problem import SDFqProblem
from .workfactor_helper import representations_asymptotic, binomial_approximation, may_ozerov_near_neighbor_time


class SternScipyModel(ScipyModel):
    def __init__(self, par_names: list, problem: SDFqProblem, iterations, accuracy):
        """
        Optimization model for workfactor computation of Stern's algorithm over Fq
        """
        super().__init__(par_names, problem, iterations, accuracy)

    def _build_model_and_set_constraints(self):
        self.L1 = lambda x: binomial_approximation(self.rate(x) / 2, x.p / 2)

        self.constraints = [
            {'type': 'ineq', 'fun': self._inject_vars(lambda x: self.rate(x) - x.p)},
            {'type': 'ineq', 'fun': self._inject_vars(lambda x: (1. - self.rate(x) - x.l) - (self.w(x) - x.p))},
            {'type': 'ineq', 'fun': self._inject_vars(lambda x: self.w(x) - x.p)},
        ]

    def _memory(self, x):
        return self.L1(x)

    def _time_lists(self, x):
        return [max(self.L1(x), 2 * self.L1(x) - x.l)]

    def _time_perms(self, x):
        return max(0,
                   binomial_approximation(1., self.w(x))
                   - binomial_approximation(self.rate(x), x.p)
                   - binomial_approximation(1 - self.rate(x) - x.l, self.w(x) - x.p)
                   - self.nsolutions
                   )

    def _time(self, x):
        x = self.set_vars(*x)
        return self._time_perms(x) + max(self._time_lists(x))
