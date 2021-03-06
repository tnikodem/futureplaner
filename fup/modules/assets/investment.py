import random
from fup.core.module import AssetModule


class Standard(AssetModule):
    def next_year(self):
        if self.config["simulation"]["random"]:
            self.asset_value *= 1 + random.gauss(mu=self.value_increase_mean, sigma=self.value_increase_std)
        else:
            self.asset_value *= 1 + self.value_increase_mean
        self.change(money=-self.money_value * self.depot_costs)

        if hasattr(self, "info_name"):
            self.df_row[self.info_name] = self.money_value
