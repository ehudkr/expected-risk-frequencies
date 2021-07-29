import altair as alt
from typing import Hashable, Optional


def forest_plot(
    x, y,
    data,
    hue=None,
    lower=None, upper=None,
    p_val=None,
    panel=None,
    neutral=None,
    logscale=False,
    tooltip=True,
    with_text=False,
    text_decimals=2,
    configure=True,
):
    """Plots a forest plot:
    A point plot surrounded with error bars.

    Parameters
    ----------
    x : str, int, Hashable
        x-axis variable in `data` (should be a continuous effect)
    y : str, int, Hashable
        y-axis variable in `data` (should be categorical)
    data : pd.DataFrame
        Long format DataFrame with columns mapping to the parameters here
        `x`, `y`, `hue`, `lower`, `upper`, `panel`.
    hue : str, int, Hashable, optional
        Color variable in `data`
    lower : str, int, Hashable, optional
        Lower bound of confidence interval variable in `data`
    upper : str, int, Hashable, optional
        Upper bound of confidence interval variable in `data`
    p_val : str, int, Hashable, optional
        P-value vriable in `data`.
    panel : str, int, Hashable, optional
        Specifying column panels, a variable in `data
    neutral : float, optional
        Specifying a value of no-effect (e.g., 1.0 for odds-ratio or risk-ratios)
    logscale : bool
        Whether to plot the x-axis in log-scale
    tooltip : bool
        Add interactive tooltip overlay with data
    with_text : bool
        Whether to add textual description of the effect.
        Only works if `hue` or `panel` are not specified.
    text_decimals : int
        How many decimals to use in the text.
    configure : bool
        Whether to do some prettifying of the chart
        (like remove panels' borders).
        Can make the Chart less editable if do.

    Returns
    -------
    alt.Chart: a forest plot.
    """
    is_multi_facet = ((panel is not None) or (hue is not None))
    if with_text and is_multi_facet:
        raise NotImplementedError(
            "Can either add text or create multi-panel plot but not both.\n"
            "If providing `hue` or `panel` then `with_text` should be `False`."
        )
    if is_multi_facet:
        chart = plot_facet_forest(
            x=x, y=y,
            data=data,
            hue=hue,
            lower=lower, upper=upper,
            panel=panel,
            neutral=neutral,
            logscale=logscale,
            tooltip=tooltip,
        )
    else:
        chart = plot_single_forest(
            x=x, y=y,
            data=data,
            lower=lower, upper=upper,
            neutral=neutral,
            logscale=logscale,
            tooltip=tooltip,
            with_text=with_text,
            text_decimals=text_decimals,
        )
    # chart = chart.properties(
    #     title={
    #         'text': title,
    #         # 'anchor': 'middle'
    #     }  # Avoid explicit `configure_title`
    # )
    if configure:
        chart = chart.configure_view(
            strokeWidth=0
        )
    return chart


def plot_single_forest(
    x, y,
    data,
    lower=None, upper=None,
    neutral=None,
    logscale=False,
    tooltip=True,
    with_text=False,
    text_decimals=2,
):
    if tooltip:
        tooltip = data.columns.tolist()

    base = alt.Chart(data)

    forest_chart = _get_forest_points(x, y, logscale, tooltip, base)

    if lower and upper:
        error_bars = _get_error_bars(y, lower, upper, base)
        forest_chart = error_bars + forest_chart

    if neutral:
        neutral_threshold = _get_no_effect_rule(neutral, base)
        forest_chart = neutral_threshold + forest_chart

    if with_text:
        data['text'] = data.apply(
            _format_effect_text,
            axis='columns',
            # kwargs:
            x=x,
            lower=lower, upper=upper,
            text_decimals=text_decimals,
        )
        text_chart = base.mark_text(
            align='left'
        ).encode(
            x=alt.value(0),
            y=alt.Y(
                y,
                title=None,
                axis=None,
            ),
            text=alt.Text('text'),
        ).properties(
            title={"text": f"{x} {'[95% CI]' if lower and upper else ''}",
                   "fontWeight": "bold",
                   "anchor": "start",
                   "fontSize": 12},
        )

        forest_chart = alt.hconcat(
            forest_chart, text_chart,
            spacing=7,
        ).resolve_scale(
            y='shared',
            x="shared",
        )

    return forest_chart


def plot_facet_forest(
    x, y,
    data,
    hue=None,
    lower=None, upper=None,
    panel=None,
    neutral=None,
    logscale=False,
    tooltip=True,
):
    base = alt.Chart(
        data=data,
        height=10 * data[hue].nunique() if hue else alt.Undefined,
        width=600 / data[panel].nunique() if panel else alt.Undefined,
    )

    if tooltip:
        tooltip = data.columns.tolist()

    if hue:
        # Altair has a counter-seaborn approach, where the `hue` is an outer facet (`row`),
        # rather than an inner groupby.
        # to conform to (the more intuitive) seaborn approach, and keep code general,
        # Color and y-axis are swapped
        hue, y = y, hue

    forest_chart = _get_forest_points(x, y, logscale, tooltip, base)
    if hue:
        forest_chart = forest_chart.encode(
            y=alt.Y(
                y,
                title=None,  # Remove color-related axis, so it's legend-only
                axis=None,
            ),
            color=alt.Color(y),
        )

    if lower and upper:
        error_bars = _get_error_bars(y, lower, upper, base)
        if hue:
            error_bars = error_bars.encode(
                color=alt.Color(y),
            )
        forest_chart = error_bars + forest_chart

    if neutral:
        neutral_threshold = _get_no_effect_rule(neutral, base)
        forest_chart = neutral_threshold + forest_chart

    row = alt.Undefined
    column = alt.Undefined
    if hue:
        row = alt.Row(
            hue,
            title=None,
            header=alt.Header(
                labelAngle=0,
                labelAlign='left',
                # labelFontSize=12,
                labelFontWeight='bold',
                # labelPadding=5,
            ),
        )
    if panel:
        column = alt.Column(
            panel,
            title=None,
            header=alt.Header(
                labelFontSize=12,
                labelFontWeight='bold',
                labelPadding=5,
            ),
        )
    forest_chart = forest_chart.facet(
        row=row,
        column=column,
        spacing=13,
    )

    return forest_chart


def _get_forest_points(x, y, logscale, tooltip=None, chart=None):
    forest_chart = chart.mark_point(
        filled=True,
        opacity=1,
        size=80,
        # color='black',
    ).encode(
        x=alt.X(
            x,
            title=x,
            # Can't define a x_scale = alt.Scale() variable before, for unknown reason:
            scale=alt.Scale(
                type="log",
                nice=False,
                padding=10,
            ) if logscale else alt.Undefined,
        ),
        y=alt.Y(
            y,
        ),
        # size=alt.value(80),  # size=alt.Size(p_val_name)
        tooltip=tooltip if tooltip else [],
    )
    return forest_chart


def _get_error_bars(y, lower, upper, chart=None):
    if chart is None:
        chart = alt.Chart()
    error_bars = chart.mark_errorbar(
        ticks={"size": 6},
        color='black'
    ).encode(
        x=alt.X(lower, title=''),
        x2=alt.X2(upper, title=''),
        y=alt.Y(y),
    )
    return error_bars


def _get_no_effect_rule(neutral, chart=None):
    if chart is None:
        chart = alt.Chart()
    neutral_threshold = chart.transform_calculate(
        neutral=f'{neutral}'
    ).mark_rule(
        color='grey',  # '#c5c6c7',
        strokeDash=[8, 8],
        strokeWidth=1.3,
    ).encode(
        x=alt.X('neutral:Q')
    )
    return neutral_threshold


def _format_effect_text(
    row,
    x,
    lower=None,
    upper=None,
    text_decimals=2,
):
    text = f"{row[x]:.{text_decimals}f}"
    if lower and upper:
        text += " "
        text += f"[{row[lower]:.{text_decimals}f}, {row[upper]:.{text_decimals}f}]"
    return text

