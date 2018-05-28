import numpy as np
from bokeh.models import ColumnDataSource, LabelSet, Button, HoverTool
from bokeh.models import CDSView, BooleanFilter, LinearColorMapper, Range1d
from bokeh.plotting import figure
from bokeh.palettes import magma, grey
from bokeh.transform import transform


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

def make_earning_plot(dataframe, symbol=''):
    num_of_year = len(dataframe['year'].unique())
    colors = magma(num_of_year)
    mapper = LinearColorMapper(palette=colors, low=dataframe.year.max(), high=dataframe.year.min())
    
    source = ColumnDataSource(dataframe)
    plot = figure(
        x_range=Range1d(0, 5),
        plot_height=500,
        plot_width=1000,
    )
    reported = plot.circle(
        x='quarter',
        y='reported',
        source=source,
        name='reported',
        size=20,
        color=transform('year', mapper),
        fill_color=transform('year', mapper),
    )
    estimated = plot.circle(
        x='quarter',
        y='estimate',
        source=source,
        name='estimated',
        size=15,
        color=transform('year', mapper),
        fill_alpha=0.4,
    )
    price_hover = HoverTool(
        renderers=[reported],
        tooltips=[
            ("year: ", "@year"),
            ("reported: ", "@reported"),
            ("estimate: ", "@estimate"),
            ("surprise: ", "@surprise{0.2f}"),
            ("surprise_per: ", "@surprise_per"),
        ]
    )
    
    plot.add_tools(price_hover)
    plot.title.text = f"{symbol.upper()} Earning" if symbol else "Earning"
    plot.legend.location = "top_left"
    plot.xaxis.axis_label = 'Quarter'
    plot.yaxis.axis_label = 'Price'
    plot.ygrid.band_fill_color = "olive"
    plot.ygrid.band_fill_alpha = 0.1
    plot.legend.click_policy= "mute"
    plot.xaxis.ticker = [1, 2, 3, 4]
    return plot