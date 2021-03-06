import random
from fup.core.module import Module


class Inflation(Module):
    def __init__(self, inflation_mean, inflation_std, name="", manager=None, **kwargs):
        super().__init__(name=name, manager=manager, **kwargs)
        self.inflation_mean_start = inflation_mean  # TODO find a general solution to handle start values!
        self.inflation_mean = inflation_mean
        self.inflation_std = inflation_std
        self.inflation = 1
        self.total_inflation = 1

    def next_year(self):
        if self.config["simulation"]["random"]:
            self.inflation = self.inflation_mean * max(random.gauss(mu=1, sigma=self.inflation_std), 1e-30)
        else:
            self.inflation = self.inflation_mean

        self.total_inflation *= self.inflation

        self.df_row["inflation"] = self.inflation
        self.df_row["total_inflation"] = self.total_inflation

    def get_extra_info(self):
        return f"inflation: {round((self.inflation - 1) * 100, 2)}"
