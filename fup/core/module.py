from fup.core.functions import get_full_class_name


class Module:
    def __init__(self, name="", manager=None, **kwargs):
        self.name = name
        self.manager = manager
        self.depends_on_modules = set()
        self.modifies_modules = set()
        self.dependency_check = False
        self.reset_values = dict()

        for k, v in kwargs.items():
            assert isinstance(k, str)
            setattr(self, k, v)

    @property
    def config(self):
        return self.manager.config

    def get_prop(self, module_name, prop_name):
        if self.dependency_check:
            self.depends_on_modules.add(module_name)
        return getattr(self.manager.get_module(module_name), prop_name)

    def change_prop(self, prop_name, change_value):
        prop_value = getattr(self, prop_name)
        prop_value *= change_value
        setattr(self, prop_name, prop_value)

    def get_prop_changer(self, module_name, prop_name):
        if self.dependency_check:
            self.modifies_modules.add(module_name)
        return lambda x: self.manager.get_module(module_name).change_prop(prop_name=prop_name, change_value=x)

    # wrapper which can be overwritten by submodule class
    def calc_next_year(self):
        self.next_year()

    # Implemented by each module definition
    def next_year(self):
        pass

    def add_info(self, info_dict):
        pass

    def get_extra_info(self):
        return ""

    def info_dict(self):
        return {
            "name": self.name,
            "class": get_full_class_name(self.__class__),
            "info": self.get_extra_info()
        }

    def __repr__(self):
        return f"""{get_full_class_name(self.__class__)}"""


class AssetModule(Module):
    def __init__(self, name="", manager=None, start_money_value=0, gains_tax=0, exchange_fee=0, **kwargs):
        super().__init__(name=name, manager=manager, **kwargs)
        self.count = start_money_value
        self.asset_value = 1
        self.gains_tax = gains_tax
        self.exchange_fee = exchange_fee

    @property
    def money_value(self):
        return self.count * self.asset_value

    def change(self, money):
        if money > 0:
            add_money_value = money * (1 - self.exchange_fee)
            self.asset_value = (self.count * self.asset_value + add_money_value) / (self.count + add_money_value)
            self.count += add_money_value
            return -money
        else:
            asset_count = abs(money) / self.asset_value
            self.count -= asset_count
            asset_value_with_fee = self.asset_value * (1 - self.exchange_fee)
            return_money = asset_value_with_fee * asset_count
            if asset_value_with_fee > 1:
                return_money *= 1 - (asset_value_with_fee - 1) / asset_value_with_fee * self.gains_tax
            return return_money

    def change_value(self, relative_change):
        self.asset_value *= relative_change

    def info_dict(self):
        out_dict = super().info_dict()
        out_dict["value"] = self.money_value
        return out_dict

    def __repr__(self):
        return f"""{get_full_class_name(self.__class__)}: {int(self.money_value)}€"""


class EventModule(Module):
    def __init__(self, name="", manager=None, start_year=None, probability=None, **kwargs):
        super().__init__(name=name, manager=manager, **kwargs)
        self.start_year = start_year
        self.probability = probability
        self.active = False

    def get_extra_info(self):
        return f"start: {self.start_year}"

    def add_info(self, info_dict):
        if self.active:
            if "event" in info_dict:
                info_dict["event"] += "," + self.name
            else:
                info_dict["event"] = self.name

    def __repr__(self):
        return f"{get_full_class_name(self.__class__)}: active: {int(self.active)} start: {self.start_year}" \
               f" prob: {self.probability}"


class ChangeModule(Module):
    def __init__(self, name="", manager=None, **kwargs):
        super().__init__(name=name, manager=manager, **kwargs)
        self._expenses = 0
        self._expense_modifier = 1
        self._income = 0
        self._income_modifier = 1

    @property
    def expenses(self):
        return self._expenses * self._expense_modifier

    @expenses.setter
    def expenses(self, value):
        self._expenses = value

    @property
    def income(self):
        return self._income * self._income_modifier

    @income.setter
    def income(self, value):
        self._income = value

    def calc_next_year(self):
        self.income = 0
        self.expenses = 0
        self.next_year()

        # TODO write better
        self.manager.get_module("assets.money.Money").count += self.income - self.expenses

        self.manager.income += self.income
        self.manager.expenses += self.expenses

    def info_dict(self):
        out_dict = super().info_dict()
        out_dict["income"] = self.income
        out_dict["expenses"] = self.expenses
        return out_dict

    def __repr__(self):
        return f"""{get_full_class_name(self.__class__)}: income: {int(self.income)}€ expenses: {int(self.expenses)}€"""
