import plotly.express as px

def savings_chart_filter(df, selected_savings_instruments, start_year, end_year):
    mask = (
        (df['Savings Instrument'].isin(selected_savings_instruments))
        & (df['Year'] >= start_year)
        & (df['Year'] <= end_year)
    )
    return df.loc[mask, :]

def base_chart_template(df, x, y, color_col, custom_data_list, hovertemplate, title_text, yaxis_format = {"fixedrange": True}):
    fig = px.line(
        df, x=x, y=y,
        color=color_col,
    )
#        custom_data=custom_data_list,
    fig.update_traces(
        hovertemplate=hovertemplate
    )
    fig.update_layout(
        title={
            'text': title_text,
            'y':0.95,
            'x':0.2,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis={"fixedrange": True},
        yaxis=yaxis_format,
        colorway=["#17B897"],
    )
    return fig
