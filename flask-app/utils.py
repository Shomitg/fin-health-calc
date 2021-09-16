from datetime import date

from params import Params
from tax import Tax

def calc_compound_interest_final_amount(p, r, t, n = 1):
    p, r, t = int(p), float(r), int(t)
    return int(p * ((1 + (r/n)) ** (n*t)))

def new_corpus_value_at_year_end(starting_value, rate, additional_investment):
    return calc_compound_interest_final_amount(p=starting_value, r=rate / 100, t=1) + additional_investment

def create_input_text_boxes(names, lookup_dict, suffix='', boxes_per_row=4):
    html = ''
    for i, name in enumerate(names):
        value = lookup_dict[name]
        display_name = name.replace('_', ' ').title()
        html += f'\
            <label for="{name}"><strong>{display_name}:</strong></label>\
            <input tpye="text" name="{name}" value="{value}">{suffix}\
        '
        if i % boxes_per_row == boxes_per_row - 1 and i != len(names)-1:
            html += '<br><br>'
    return f'{html}<br>'

def create_usage_instructions_html():
    html = '<style>h3{background-color: powderblue;}</style>'
    html += '<h3>Instructions for using this Calculator</h3>'
    html += 'There are 5 input sections where you can provide your financial details:'
    html += '\
        <ul>\
            <li><strong>Current Savings By Instrument</strong>: Provide the current value of your investments in various options, such as mutual funds, FD, PF etc.</li>\
            <li><strong>Contributions (% basic salary)</strong>: Provide the amount in terms of the % of your basic salary that is deducted towards NPS and PF.</li>\
            <li><strong>Yearly Contributions</strong>: Provide the total amount that you intend to investment in various instruments in the coming year.</li>\
            <li><strong>Income and Expenses</strong>: Provide your income, expenses and other details.</li>\
            <li><strong>Rates</strong>: Various rates of returns (slightly pessimistic common defaults have been used), you may leave them unchanged if not sure about the rates.</li>\
        </ul>\
    '
    html += 'The graph at the bottom of the page will show you the value of your savings corpus every year, untill your retirement.'
    return html

def create_input_html_content(configs, current_args, boxes_per_row=4):
    """
    we'll create 5 sections
      * current_savings_by_instrument
      * basic_pct_contributions
      * contributions
      * income_and_expenses
      * rates
    """
    input_boxes_html = '<style>h3{background-color: powderblue;}</style>'

    input_boxes_html += '<h3>Current Savings By Instrument</h3>'
    input_boxes_html += create_input_text_boxes(list(configs.current_savings_by_instrument.keys()), current_args)

    input_boxes_html += '<h3>Contributions (% basic salary)</h3>'
    input_boxes_html += create_input_text_boxes(list(configs.basic_pct_contributions.keys()), current_args, suffix='%')

    input_boxes_html += '<h3>Yearly Contributions</h3>'
    input_boxes_html += create_input_text_boxes(list(configs.contributions.keys()), current_args)
    
    input_boxes_html += '<h3>Income and Expenses</h3>'
    input_boxes_html += create_input_text_boxes(list(configs.income_and_expenses.keys()), current_args)

    input_boxes_html += '<h3>Rates</h3>'
    input_boxes_html += create_input_text_boxes(list(configs.rates.keys()), current_args, suffix='%')
    
    return input_boxes_html + '<br>'

def savings_calculation(args, configs):
    '''
    ASSUMPTIONS
        1. NPS and PF investments are made at the same %basic till retirement
        2. Fixed expenses grow at the rate of inflation
    '''
    current_year = date.today().year
    no_of_years = int(args['years_till_retirement'])
    years_list = list(range(current_year, current_year + no_of_years + 1))

    # compute yearly savings by instrument
    # initialize all instruments with current savings
    year_wise_savings = {
        'nps_corpus': [int(args['nps_corpus'])],
        'pf_corpus': [int(args['pf_corpus'])],
        'ppf_corpus': [int(args['ppf_corpus'])],
        'mf_corpus': [int(args['mf_corpus'])],
        'equity_corpus': [int(args['equity_corpus'])],
        'fd_corpus': [int(args['fd_corpus'])],
        'savings_corpus': [int(args['savings_corpus'])],
        'other_savings_corpus': [int(args['other_savings_corpus'])]
    }
    
    # contains the list of expenses for the next year, i.e. year starting at the corresponding index in <years_list>
    year_wise_expenses = [12 * int(args['monthly_fixed_expense'])]

    # compute year wise basic for the number of years of service left
    for i in range(no_of_years):
        current_annual_basic = calc_compound_interest_final_amount(p=int(args['annual_basic']), r=float(args['income_growth_rate']) / 100, t=i)
        current_nps_contribution = int(current_annual_basic * (float(args['nps_contribution']) / 100))
        
        current_employer_pf_contribution = int(current_annual_basic * (float(args['employer_pf_contribution']) / 100))
        current_employee_pf_contribution = int(current_annual_basic * (float(args['employee_pf_contribution']) / 100))
        current_pf_contribution = current_employer_pf_contribution + current_employee_pf_contribution
        
        current_mf_contribution = calc_compound_interest_final_amount(p=int(args['mf_contribution']), r=float(args['mf_step_up']) / 100, t=i)
        current_equity_contribution = calc_compound_interest_final_amount(p=int(args['equity_contribution']), r=float(args['equity_step_up']) / 100, t=i)

        current_ppf_contribution = int(args['ppf_contribution']) if i < int(args['ppf_installments_left']) else 0
        
        current_income = calc_compound_interest_final_amount(p=int(args['annual_income']), r=float(args['income_growth_rate']) / 100, t=i)
        
        tax = Tax(current_income, current_employer_pf_contribution, int(args['80c_deductions']), current_nps_contribution, configs)
        current_after_tax_income = tax.after_tax_income

        current_expense = calc_compound_interest_final_amount(p=12 * int(args['monthly_fixed_expense']), r=float(args['inflation_rate']) / 100, t=i)
        
        current_fd_contribution = current_after_tax_income - current_expense - current_nps_contribution - current_pf_contribution - current_mf_contribution - current_equity_contribution - current_ppf_contribution

        # update the value of different investment instruments at the end of the year
        year_wise_savings['nps_corpus'].append(new_corpus_value_at_year_end(starting_value=year_wise_savings['nps_corpus'][-1], rate=float(args['nps_ror']), additional_investment=current_nps_contribution))
        year_wise_savings['pf_corpus'].append(new_corpus_value_at_year_end(starting_value=year_wise_savings['pf_corpus'][-1], rate=float(args['pf_ror']), additional_investment=current_pf_contribution))
        year_wise_savings['mf_corpus'].append(new_corpus_value_at_year_end(starting_value=year_wise_savings['mf_corpus'][-1], rate=float(args['mf_ror']), additional_investment=current_mf_contribution))
        year_wise_savings['equity_corpus'].append(new_corpus_value_at_year_end(starting_value=year_wise_savings['equity_corpus'][-1], rate=float(args['equity_ror']), additional_investment=current_equity_contribution))
        year_wise_savings['fd_corpus'].append(new_corpus_value_at_year_end(starting_value=year_wise_savings['fd_corpus'][-1], rate=float(args['fd_ror']), additional_investment=current_fd_contribution))
        year_wise_savings['savings_corpus'].append(new_corpus_value_at_year_end(starting_value=year_wise_savings['savings_corpus'][-1], rate=float(args['savings_ror']), additional_investment=0))
        year_wise_savings['other_savings_corpus'].append(new_corpus_value_at_year_end(starting_value=year_wise_savings['other_savings_corpus'][-1], rate=float(args['other_savings_ror']), additional_investment=0))

        # when we reach the end of ppf term, we will transfer the ppf amount to fd and the ppf corpus will become 0 from that year onwards
        if i == int(args['ppf_installments_left']) - 1:
            year_wise_savings['fd_corpus'][-1] = year_wise_savings['fd_corpus'][-1] + new_corpus_value_at_year_end(starting_value=year_wise_savings['ppf_corpus'][-1], rate=float(args['ppf_ror']), additional_investment=current_ppf_contribution)
            year_wise_savings['ppf_corpus'].append(0)
        else:
            year_wise_savings['ppf_corpus'].append(new_corpus_value_at_year_end(starting_value=year_wise_savings['ppf_corpus'][-1], rate=float(args['ppf_ror']), additional_investment=current_ppf_contribution))
        
        # next year's expense
        year_wise_expenses.append(calc_compound_interest_final_amount(p=12 * int(args['monthly_fixed_expense']), r=float(args['inflation_rate']) / 100, t=i+1))
    return years_list, year_wise_savings, year_wise_expenses

def output_formatter(years_list, year_wise_savings, year_wise_expenses):
    return(
        '<style>h3{text-decoration-line: underline;text-decoration-style: double;background-color: powderblue;}</style>'
        f'<h3>Savings</h3>'
        f'{"<br>".join([key+": "+", ".join(map(str, value)) for key, value in year_wise_savings.items()])}<br>'
        f'Total savings at retirement: {sum([ele[-1] for ele in year_wise_savings.values()]):,}'
    )

if __name__ == "__main__":
    from params import Params
    configs = Params()
    lac = 100000
    for income in [10*lac, 50*lac, 51*lac, 52*lac, 53*lac, 55*lac, 70*lac, 150*lac]:
        tax = Tax(income, 0, 0, 0, configs)
        print(tax.total_income_tax, tax.after_tax_income)
