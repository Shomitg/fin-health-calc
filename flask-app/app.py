from flask import Flask
from flask import escape, render_template, request
from params import Params
from utils import create_input_html_content, create_usage_instructions_html, savings_calculation

app = Flask(__name__)
configs = Params()

@app.route("/")
def index():
    if "years_till_retirement" in request.args:
        current_args = request.args
    else:
        current_args = configs.get_var_dict()
    years_list, year_wise_savings, year_wise_expenses = savings_calculation(current_args, configs)
    total_yearly_savings_corpus = []
    for i in range(len(years_list)):
        total_yearly_savings_corpus.append(sum([arr[i] for arr in year_wise_savings.values()]))

    return (
        '<style>h2{text-align: center; background-color: lightgreen;}</style>'
        '<title>Financial Health Calculator by Shomit Goyal</title>'
        f'<h2>Financial Health Calculator</h2>'
        f'{create_usage_instructions_html()}'
        f'<form action="" method="get">\n'
            f'{create_input_html_content(configs, current_args)}'
            f'<input type="submit" value="Estimate Financial Health"><br>'
        f'</form>'
        f'{render_template("savings_chart.html", values=total_yearly_savings_corpus, labels=years_list, legend="Total Savings Corpus")}<br><br>'
    )
#        f'{output_formatter(years_list, year_wise_savings, year_wise_expenses)}'

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
    #current_args = configs.get_var_dict()
    #savings_calculation(current_args)

#    for key, value in year_wise_savings.items():
#        print(f'============== {key} ==============:{len(value)}')
#        print(value)
#    print(f'retirement corpus: {sum([ele[-1] for ele in year_wise_savings.values()]):,}')
