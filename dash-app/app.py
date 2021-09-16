import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import date
import pandas as pd
import plotly.express as px

from params import Params
from utils import create_input_text_boxes, savings_calculation
from helper_functions_callbacks import savings_chart_filter, base_chart_template

RUPEE_SYMBOL = u'\u20B9'

configs = Params()

usage_instructions = [
    'Current Savings By Instrument: Provide the current value of your investments in various options, such as mutual funds, FD, PF etc.',
    'Contributions (% basic salary): Provide the amount in terms of the % of your basic salary that is deducted towards NPS and PF.',
    'Yearly Contributions: Provide the total amount that you intend to investment in various instruments in the coming year.',
    'Income and Expenses: Provide your income, expenses and other details.',
    'Rates: Various rates of returns (slightly pessimistic common defaults have been used), you may leave them unchanged if not sure about the rates.',
]

all_savings_instruments = [
    "Total Savings",
    "NPS",
    "PF",
    "PPF",
    "MF",
    "Equity",
    "FD",
    "Savings",
    "Other Savings",
    "Next Year's Expenses",
]

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Financial Health Calculator'
server = app.server

app.layout = html.Div(
    children=[
        # header
        html.Div(
            children=[
                html.P(children='🧩', className='header-emoji'),
                html.H1(children='Financial Health Calculator', className='header-title'),
                html.P(
                    children='road to financial freedom: estimate your financial health',
                    className='header-description'
                ),
            ],
            className='header',
        ),
        # usage instructions
        html.Div(
            children=[
                html.Div(
                    children='Instructions for using this Calculator',
                    className='descriptor-title'
                ),
                html.Div(
                    children="There are 5 input sections where you can provide your financial details:",
                    className='descriptor-description'
                ),
                html.Ul([html.Li(x, className='descriptor-description') for x in usage_instructions]),
                html.Div(
                    children='The graph at the bottom of the page will show you the value of your savings corpus every year, untill your retirement.',
                    className='descriptor-description'
                )
            ],
            className='descriptor',
        ),
        # current savings by instrument
        html.Div(
            children=[
                html.Div(
                    children='Current Savings By Instrument',
                    className='subsection-title'
                ),
                html.Div(
                    children=create_input_text_boxes(tuple(configs.current_savings_by_instrument.items())),
                    className='menu'
                )
            ],
            className='menu-descriptor',
        ),
        # contributions (% basic salary)
        html.Div(
            children=[
                html.Div(
                    children='Contributions (% basic salary)',
                    className='subsection-title'
                ),
                html.Div(
                    children=create_input_text_boxes(tuple(configs.basic_pct_contributions.items()), suffix=' (%)'),
                    className='menu'
                )
            ],
            className='menu-descriptor',
        ),
        # yearly contributions
        html.Div(
            children=[
                html.Div(
                    children='Yearly Contributions',
                    className='subsection-title'
                ),
                html.Div(
                    children=create_input_text_boxes(tuple(configs.contributions.items())),
                    className='menu'
                )
            ],
            className='menu-descriptor',
        ),
        # income and expenses
        html.Div(
            children=[
                html.Div(
                    children='Income and Expenses',
                    className='subsection-title'
                ),
                html.Div(
                    children=create_input_text_boxes(tuple(configs.income_and_expenses.items())),
                    className='menu'
                )
            ],
            className='menu-descriptor',
        ),
        # rates
        html.Div(
            children=[
                html.Div(
                    children='Rates',
                    className='subsection-title'
                ),
                html.Div(
                    children=create_input_text_boxes(tuple(configs.rates.items())[:6], suffix=' (%)'),
                    className='menu'
                ),
                html.Div(
                    children=create_input_text_boxes(tuple(configs.rates.items())[6:], suffix=' (%)'),
                    className='menu'
                ),
            ],
            className='menu-descriptor',
        ),
        # timeframe slider
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children='Timeframe', className='center-align'),
                        dcc.RangeSlider(
                            id="timeframe_slider",
                            min=configs.years_list[0],
                            max=configs.years_list[-1],
                            step=1,
                            value=[configs.years_list[0], configs.years_list[-1]],
                            marks={year: str(year) for year in configs.years_list},
                            allowCross=False,
                            className='margin10',
                        ),
                    ],
                ),
            ],
            className='temp',
        ),
        # checklist
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children='Savings Instrument', className='center-align'),
                        dcc.Checklist(
                            id="savings_instrument_checklist",
                            options=[{"label": savings_instrument, "value": savings_instrument} for savings_instrument in all_savings_instruments],
                            value=[all_savings_instruments[0]]+[all_savings_instruments[-1]],
                            labelStyle={'display': 'inline-block'},
                            className='checklist',
                        ),
                    ],
                ),
            ],
            className='menu',
        ),
        # plot
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id='savings_chart',
                        config={'displayModeBar': False},
                    ),
                    className='card',
                ),
            ],
            className='wrapper'
        ),
    ]
)

# timeframe slider
@app.callback(
    [Output("timeframe_slider", "min"), Output("timeframe_slider", "max"), Output("timeframe_slider", "value"), Output("timeframe_slider", "marks")],
    [Input("years_till_retirement", "value")]
)
def update_timeframe_slider(years_till_retirement):
    current_year = date.today().year
    years_list = list(range(current_year, current_year + years_till_retirement + 1))
    return years_list[0], years_list[-1], [years_list[0], years_list[-1]], {year: str(year) for year in years_list}

# chart filtering for trend analysis
@app.callback(
    Output("savings_chart", "figure"),
    [
        Input("savings_instrument_checklist", "value"),
        Input("timeframe_slider", "value"),
        *[Input(id, "value") for id in configs.current_savings_by_instrument.keys()],
        *[Input(id, "value") for id in configs.basic_pct_contributions.keys()],
        *[Input(id, "value") for id in configs.contributions.keys()],
        *[Input(id, "value") for id in configs.income_and_expenses.keys()],
        *[Input(id, "value") for id in configs.rates.keys()],
    ]
)
def update_savings_chart(*values):
    selected_savings_instruments = values[0]
    start_year, end_year = values[1]
    inputs = values[2:]
    
    keys = [
        *list(configs.current_savings_by_instrument.keys()),
        *list(configs.basic_pct_contributions.keys()),
        *list(configs.contributions.keys()),
        *list(configs.income_and_expenses.keys()),
        *list(configs.rates.keys()),
    ]
    current_args = dict(zip(keys, inputs))
    df = savings_calculation(current_args, configs)
    filtered_data = savings_chart_filter(df.copy(), selected_savings_instruments, start_year, end_year)

    fig = base_chart_template(
        filtered_data,
        x = 'Year',
        y = 'Amount',
        color_col = 'Savings Instrument',
        custom_data_list = ['# Guests'],
        hovertemplate = "<br>".join([
            "Year: %{x}",
            "Amount: %{y:,.0f}",
            #"# Guests: %{customdata[0]:,}",
        ]),
        title_text = 'Yearly Savings Chart'
    )
    return(fig)

if __name__ == '__main__':
    app.run_server(debug=True)

# Emojis: 🧩, 🧠, 💡