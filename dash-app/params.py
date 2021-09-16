from datetime import date

class Params(object):
    def __init__(self):
        self.TAX_SLABS = ((1000000, 30), (500000, 20), (250000, 5))
        self.TAX_SURCHARGE_SLABS = ((50000000, 37), (20000000, 25), (10000000, 15), (5000000, 10), (0, 0))
        self.HEALTH_AND_EDUCATION_CESS_RATE = 4.0

        self.rates = {
            'inflation_rate': 7.0,
            'income_growth_rate': 3.0,
            'nps_ror': 10.0,
            'pf_ror': 8.0,
            'ppf_ror': 7.1,
            'mf_ror': 8.0,
            'equity_ror': 8.0,
            'fd_ror': 4.0,
            'savings_ror': 3.0,
            'other_savings_ror': 3.0,
            'mf_step_up': 5.0,
            'equity_step_up': 5.0
        }
        
        self.basic_pct_contributions = {
            'nps_contribution': 5.0,          # percentage of basic
            'employer_pf_contribution': 12.0, # percentage of basic
            'employee_pf_contribution': 12.0  # percentage of basic
        }
        
        self.contributions = {
            'ppf_contribution': 150000,
            'mf_contribution': 200000,
            'equity_contribution': 0
        }

        self.current_savings_by_instrument = {
            'nps_corpus': 100000,
            'pf_corpus': 100000,
            'ppf_corpus': 300000,
            'mf_corpus': 500000,
            'equity_corpus': 500000,
            'fd_corpus': 200000,
            'savings_corpus': 100000,
            'other_savings_corpus': 5000
        }
        
        self.income_and_expenses = {
            'annual_income': 1000000,
            'annual_basic': 400000,
            'monthly_fixed_expense': 30000,
            'years_till_retirement': 25,
            'ppf_installments_left': 10,
            '80c_deductions': 150000
        }

        current_year = date.today().year
        self.years_list = list(range(current_year, current_year + self.income_and_expenses['years_till_retirement'] + 1))

    def get_var_dict(self):
        param_dict = {}
        for key, value in vars(self).items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    param_dict[sub_key] = sub_value
            else:
                param_dict[key] = value
        return param_dict

#monthly_personal_loan_emi = 7100
#monthly_home_loan_emi = 15500
#monthly_lic_premium = 3100

if __name__ == "__main__":
    configs = Params()
    for key in configs.get_var_dict():
        print(key)
