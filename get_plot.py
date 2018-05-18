import numpy as np
from bokeh.models import ColumnDataSource, LabelSet, Button, HoverTool
from bokeh.models import CDSView, BooleanFilter
from bokeh.plotting import figure, output_notebook, show


def make_price_plot(dataframe, symbol='', add_div=True):
    source = ColumnDataSource(dataframe)
    plot = figure(
        x_axis_type='datetime',
        plot_height=500,
        plot_width=1000,
    )
    price_line = plot.line(
        x='index', 
        y='ohlc_avg', 
        source=source, 
        legend='OHLC AVG', 
        muted_alpha=0.2, 
        name='price'
    )
    price_hover = HoverTool(
        renderers=[price_line], 
        mode='vline', 
        tooltips=[
            ("open: ", "@open"),
            ("close: ", "@close"),
            ("high: ", "@high"),
            ("low: ", "@low"),
        ]
    )
    plot.add_tools(price_hover)

    if 'div_amount' in dataframe.columns and add_div:
        booleans = [not np.isnan(amount) 
            for amount in source.data['div_amount']]
        div_view = CDSView(source=source, filters=[BooleanFilter(booleans)])
        dividend = plot.circle(
            x='index', 
            y='ohlc_avg', 
            source=source, 
            view=div_view, 
            color='maroon', 
            legend='Dividend', 
            muted_alpha=0.2, 
            name='div'
        )
        dividend_hover = HoverTool(
            renderers=[dividend], 
            tooltips=[
                ("dividend amount: ", "@amount"),
            ]
        )
        plot.add_tools(dividend_hover)

    plot.title.text = f"{symbol.upper()} Price" if symbol else "Price" 
    plot.legend.location = "top_left"
    plot.xaxis.axis_label = 'Date'
    plot.yaxis.axis_label = 'Price'
    plot.ygrid.band_fill_color = "olive"
    plot.ygrid.band_fill_alpha = 0.1
    plot.legend.click_policy= "mute"
    return plot
