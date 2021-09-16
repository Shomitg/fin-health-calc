from params import Params

class Tax(object):
    '''
    A Tax computer object.
    Attributes:
        annual_income_before_tax
        contribution_employer_pf
        contribution_80c
        contribution_nps
        configs: Params
    '''
    def __init__(self, annual_income_before_tax, contribution_employer_pf, contribution_80c, contribution_nps, configs: Params):
        self.annual_income_before_tax = int(annual_income_before_tax)
        self.contribution_employer_pf = contribution_employer_pf
        self.deduction_80c = min(150000, contribution_80c)
        self.deduction_nps = min(50000, contribution_nps)

        self.TAX_SLABS = configs.TAX_SLABS
        self.TAX_SURCHARGE_SLABS = configs.TAX_SURCHARGE_SLABS
        self.HEALTH_AND_EDUCATION_CESS_RATE = configs.HEALTH_AND_EDUCATION_CESS_RATE
        
        self.total_income_tax = self.calculate_income_tax()
        self.after_tax_income = int(self.annual_income_before_tax - self.total_income_tax)

    def calculate_income_tax(self):
        taxable_income = self.annual_income_before_tax - self.contribution_employer_pf - self.deduction_80c - self.deduction_nps
        income_tax = self.calculate_primary_income_tax(taxable_income)
        income_tax_with_surcharge = self.add_surcharge_tax(taxable_income, income_tax)
        health_and_education_cess = income_tax_with_surcharge * (self.HEALTH_AND_EDUCATION_CESS_RATE / 100)
        total_income_tax = income_tax_with_surcharge + health_and_education_cess
        return total_income_tax

    def calculate_primary_income_tax(self, taxable_income):
        income_tax = 0
        for threshold, rate in self.TAX_SLABS:
            if taxable_income > threshold:
                income_tax += (taxable_income - threshold) * (rate / 100)
                taxable_income = threshold
        return income_tax

    def add_surcharge_tax(self, taxable_income, income_tax):
        tax_surcharge_rate, threshold = self.find_surcharge_rate(taxable_income)
        surcharge_tax = income_tax * (tax_surcharge_rate / 100)
        total_tax = income_tax + surcharge_tax
        
        income_tax_for_marginal_computation = self.calculate_primary_income_tax(threshold)
        tax_surcharge_rate_for_marginal_computation, _ = self.find_surcharge_rate(threshold)
        marginal_tax = income_tax_for_marginal_computation + (income_tax_for_marginal_computation * (tax_surcharge_rate_for_marginal_computation / 100)) + (taxable_income - threshold)
        
        return min(total_tax, marginal_tax)

    def find_surcharge_rate(self, taxable_income):
        tax_surcharge_rate = 0
        for threshold, rate in self.TAX_SURCHARGE_SLABS:
            if taxable_income > threshold:
                tax_surcharge_rate = rate
                break
        return tax_surcharge_rate, threshold
