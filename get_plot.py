import numpy as np
from bokeh.models import ColumnDataSource, LabelSet, Button, HoverTool
from bokeh.models import CDSView, BooleanFilter, LinearColorMapper, Range1d
from bokeh.plotting import figure
from bokeh.palettes import magma, grey
from bokeh.transform import transform


def make_price_plot(data, symbol='', add_div=True):
    source = ColumnDataSource(data)
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

    if 'div_amount' in data.columns and add_div:
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
            size=5,
            name='div'
        )
        dividend_hover = HoverTool(
            renderers=[dividend], 
            tooltips=[
                ("dividend amount: ", "@div_amount"),
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


def make_div_plot(data, symbol=''):
    data['formatted_ex_date'] = \
        [x.strftime("%Y-%m-%d") for x in data.index]
    source = ColumnDataSource(data)
    booleans = [not np.isnan(amount) for amount in source.data['div_amount']]
    div_view = CDSView(source=source, filters=[BooleanFilter(booleans)])
    plot = figure(
        x_axis_type='datetime',
        plot_height=500,
        plot_width=1000,
    )
    div_circle = plot.circle(
        x='index', 
        y='div_amount', 
        source=source, 
        view=div_view,
        name='Divident Amount',
        size=7.5,
        color='maroon',
    )
    hover = HoverTool(
        renderers=[div_circle], 
        tooltips=[
            ("ex_date", "@formatted_ex_date"),
            ("amount", "@div_amount")],
    )
    plot.add_tools(hover)
    plot.title.text = f"{symbol.upper()} Dividend History" if symbol else "Dividend History" 
    plot.legend.location = "top_left"
    plot.xaxis.axis_label = 'Date'
    plot.yaxis.axis_label = 'Dividend Amount'
    plot.ygrid.band_fill_color = "olive"
    plot.ygrid.band_fill_alpha = 0.1
    return plot


def make_earning_plot(data, symbol=''):
    num_of_year = len(data['year'].unique())
    colors = magma(num_of_year)
    mapper = LinearColorMapper(palette=colors, low=data.year.max(), high=data.year.min())
    
    source = ColumnDataSource(data)
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
        legend='Reported',
        size=20,
        color=transform('year', mapper),
        fill_color=transform('year', mapper),
    )
    estimated = plot.circle(
        x='quarter',
        y='estimate',
        source=source,
        name='estimated',
        legend='Estimated',
        size=15,
        color=transform('year', mapper),
        fill_alpha=0.4,
        muted_alpha=0.1,
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
    plot.legend.click_policy = "mute"
    plot.xaxis.ticker = [1, 2, 3, 4]
    return plot
