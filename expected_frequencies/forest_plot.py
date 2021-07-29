import altair as alt
from typing import Hashable, Optional


def plot_forest(
    x, y,
    data,
    hue=None,
    lower=None, upper=None,
    p_val=None,
    panel=None,
    neutral=None,
    logscale=False,
    with_text=False,
    precision=2,
    configure=True,  # TODO: rename to "remove border"?
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
    with_text : bool
        Whether to add textual description of the effect.
        Only works if `hue` or `panel` are not specified.
    precision : int
        How many decimals to use in the text.
    configure : bool
        Whether to remove panels' borders

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
            configure=configure,
        )
    else:
        chart = plot_single_forest(
            x=x, y=y,
            data=data,
            lower=lower, upper=upper,
            neutral=neutral,
            logscale=logscale,
            with_text=with_text,
            precision=precision,
            configure=configure,
        )
    chart = chart.properties(  # TODO: remove?
        title={
            'text': "Association of injectable contraceptive and discontinuation",
            # 'anchor': 'middle'
        }  # Avoid explicit `configure_title`
    )
    return chart


def plot_single_forest(
    x, y,
    data,
    lower=None, upper=None,
    neutral=None,
    logscale=False,
    with_text=False,
    precision=2,
    configure=True,
):
    base = alt.Chart(data)

    forest_chart = base.mark_point(
        filled=True,
        opacity=1,
        # size=80,
        # color='black'
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
            # title=y_name.capitalize(),
        ),
        size=alt.value(80),  # size=alt.Size(p_val_name)
    )

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
            lower=lower,
            upper=upper,
            precision=precision,
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

    if configure:
        forest_chart = forest_chart.configure_view(
            strokeWidth=0
        )
    return forest_chart


def _format_effect_text(
    row,
    x,
    lower=None,
    upper=None,
    precision=2,
):
    text = f"{row[x]:.{precision}f}"
    if lower and upper:
        text += " "
        text += f"[{row[lower]:.{precision}f}, {row[upper]:.{precision}f}]"
    return text


def plot_facet_forest(
    x, y,
    data,
    hue=None,
    lower=None, upper=None,
    panel=None,
    neutral=None,
    logscale=False,
    configure=True,
):
    base = alt.Chart(
        data=data,
        height=10 * data[hue].nunique() if hue else alt.Undefined,
        width=600 / data[panel].nunique() if panel else alt.Undefined,
    )

    if hue:  # TODO: explain
        hue, y = y, hue

    forest_chart = base.mark_point(
        filled=True,
        opacity=1,
        size=80,
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
        tooltip=data.columns.tolist(),
    )
    if hue:
        forest_chart = forest_chart.encode(
            y=alt.Y(
                y,
                title=None,
                axis=None,
            ),
            color=alt.Color(
                y,
            ),
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
    )

    if configure:
        forest_chart = forest_chart.configure_view(
            strokeWidth=0,
        ).configure_facet(
            spacing=13,  # TODO: row: 13, column: 5
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



# ######################
# ######################
# ######################
# ######################
# ######################
# ######################
# ######################
# ######################
#
# def plot_forest_text(data, plot_neutral_odds=True, precision=2, configure=True):
#     def format_table_like_odds_text(row):
#         text = f"{row[x_name]:.{precision}f} " \
#                f"[{row[ci_lower_name]:.{precision}f}, {row[ci_higher_name]:.{precision}f}]"
#         return text
#
#     x_name = 'effect'
#     y_name = 'country'
#     ci_lower_name = 'ci_lower'
#     ci_higher_name = 'ci_upper'
#
#     base = alt.Chart(data)
#
#     forest_dots = base.mark_point(
#         filled=True,
#         opacity=1,
#         # size=80,
#         # color='black'
#     ).encode(
#         x=alt.X(x_name,
#                 title="Risk ratio",
#                 scale=alt.Scale(type="log",
#                                 nice=False, padding=10),
#                 axis=alt.Axis(
#                     # tickMinStep=0.5, tickCount=5,
#                     values=[0.5, 1, 2, 4],  # Should be changed per task
#                     # grid=False,
#                 ),
#                 ),
#         y=alt.Y(y_name,
#                 title=y_name.capitalize(),
#                 ),
#         size=alt.value(80),  # size=alt.Size(p_val_name)
#     )
#     error_bars = base.mark_errorbar(
#         ticks={"size": 6},
#         color='black'
#     ).encode(
#         x=alt.X(ci_lower_name, title=''),
#         x2=alt.X2(ci_higher_name, title=''),
#         y=alt.Y(y_name),
#     )
#     forest_chart = error_bars + forest_dots
#     if plot_neutral_odds:
#         neutral_threshold = base.transform_calculate(
#             neutral_odds='1.0'
#         ).mark_rule(
#             color='grey',  # '#c5c6c7',
#             strokeDash=[8, 8],
#             strokeWidth=1.3,
#         ).encode(
#             x=alt.X('neutral_odds:Q')
#         )
#         forest_chart = neutral_threshold + forest_chart
#
#     data['text'] = data.apply(format_table_like_odds_text, axis='columns')
#     text_chart = base.transform_calculate(
#         # text=""
#     ).mark_text(
#         align='left'
#     ).encode(
#         x=alt.value(0),
#         y=alt.Y(y_name,
#                 title=None,
#                 axis=None,
#                 ),
#         # text=alt.Text(x_name, format=".2f"),
#         text=alt.Text('text'),
#     ).properties(
#         title={"text": "Risk Ratio [95% CI]",
#                "fontWeight": "bold",
#                "anchor": "start",
#                "fontSize": 12},
#     )
#
#     forest_chart = alt.hconcat(
#         forest_chart, text_chart,
#         spacing=7,
#     ).resolve_scale(
#         y='shared',
#         x="shared",
#         # x='independent'  # 'shared'
#     ).properties(
#         title={'text': "Association of injectable contraceptive and discontinuation",
#                'anchor': 'middle'}  # Avoid explicit `configure_title`
#     )
#     if configure:
#         forest_chart = forest_chart.configure_view(
#             strokeWidth=0
#         )
#
#     return forest_chart
#
#
# def plot_forest_panel(df, plot_neutral_odds=True, precision=2, configure=True):
#     x_name = 'effect'
#     y_name = 'country'
#     ci_lower_name = 'ci_lower'
#     ci_higher_name = 'ci_upper'
#     panel = "model"
#
#     base = alt.Chart(
#         width=180,
#     )
#
#     forest_dots = base.mark_point(
#         filled=True,
#         opacity=1,
#         # size=80,
#         # color='black'
#     ).encode(
#         x=alt.X(x_name,
#                 title="Risk ratio",
#                 scale=alt.Scale(type="log",
#                                 nice=False, padding=5),
#                 axis=alt.Axis(
#                     # tickMinStep=0.5, tickCount=5,
#                     values=[0, 0.5, 1, 2, 4],  # Should be changed per task
#                     # grid=False,
#                 )
#                 ),
#         y=alt.Y(f"{y_name}:N",
#                 title=y_name.capitalize(),
#                 sort="-x"),
#         size=alt.value(80),  # size=alt.Size(p_val_name)
#     )
#     error_bars = base.mark_errorbar(
#         ticks={"size": 6},
#         color='black'
#     ).encode(
#         x=alt.X(ci_lower_name, title=''),
#         x2=alt.X2(ci_higher_name, title=''),
#         y=alt.Y(y_name),
#     )
#     forest_chart = error_bars + forest_dots
#
#     if plot_neutral_odds:
#         neutral_threshold = base.transform_calculate(
#             neutral_odds='1.0'
#         ).mark_rule(
#             color='grey',  # '#c5c6c7',
#             strokeDash=[8, 8],
#             strokeWidth=1.3,
#         ).encode(
#             x=alt.X('neutral_odds:Q')
#         )
#         forest_chart = neutral_threshold + forest_chart
#
#     forest_chart = forest_chart.facet(
#         data=df,
#         column=alt.Column(
#             f"{panel}:N",
#             title=None,
#             header=alt.Header(
#                 labelFontSize=12,
#                 labelFontWeight='bold',
#                 labelPadding=5,
#             ),
#         )
#     )
#
#     forest_chart = forest_chart.properties(
#         title={'text': "Association of injectable contraceptive and discontinuation",
#                'anchor': 'start',
#                'subtitle': " ",
#                'subtitlePadding': -2}  # Avoid explicit `configure_title`
#     )
#     if configure:
#         forest_chart = forest_chart.configure_view(
#             strokeWidth=0
#         ).configure_facet(
#             spacing=5,
#         )
#
#     return forest_chart
#
#
# def plot_forest_colored(data, plot_neutral_odds=True, precision=2, configure=True):
#     def format_table_like_odds_text(row):
#         text = f"{row['effect']:.{precision}f} " \
#                f"[{row['ci_lower']:.{precision}f}, {row['ci_upper']:.{precision}f}]"
#         return text
#
#     base = alt.Chart(
#         height=30
#     )
#     dots = base.mark_point(
#         filled=True,
#         opacity=1,
#         size=80,
#     ).encode(
#         x=alt.X("effect",
#                 title="Risk ratio",
#                 scale=alt.Scale(type="log",
#                                 nice=False, padding=10,
#                                 # domain=(0.95, 2.05)
#                                 ),
#                 axis=alt.Axis(
#                     # tickMinStep=0.5,
#                     # tickCount=6,
#                     values=[0, 1, 1.5, 2],  # Should be changed per task
#                     # grid=False,
#                 )
#                 ),
#         y=alt.Y("model",
#                 title=None,
#                 axis=None,
#                 ),
#         color=alt.Color("model"),
#         tooltip=data.columns.tolist(),
#     )
#     error_bars = base.mark_errorbar(
#         ticks={"size": 6},
#         # color='black'
#     ).encode(
#         x=alt.X("ci_lower", title=''),
#         x2=alt.X2("ci_upper", title=''),
#         y=alt.Y("model"),
#         color=alt.Color("model")
#     )
#     forest_chart = error_bars + dots
#
#     if plot_neutral_odds:
#         neutral_threshold = base.transform_calculate(
#             neutral_odds='1.0'
#         ).mark_rule(
#             color='grey',  # '#c5c6c7',
#             strokeDash=[8, 8],
#             strokeWidth=1.3,
#         ).encode(
#             x=alt.X('neutral_odds:Q')
#         )
#         forest_chart = neutral_threshold + forest_chart
#
#     # data['text'] = data.apply(format_table_like_odds_text, axis='columns')
#     # text_chart = base.transform_calculate(
#     #     # text=""
#     # ).mark_text(
#     #     align='left'
#     # ).encode(
#     #     x=alt.value(0),
#     #     y=alt.Y(y_name,
#     #             title=None,
#     #             axis=None,
#     #             ),
#     #     # text=alt.Text(x_name, format=".2f"),
#     #     text=alt.Text('text'),
#     # ).properties(
#     #     title={"text": "Risk Ratio [95% CI]",
#     #            "fontWeight": "bold",
#     #            "anchor": "start",
#     #            "fontSize": 12},
#     # )
#     #
#     # forest_chart = alt.hconcat(
#     #     forest_chart, text_chart,
#     #     spacing=7,
#     # ).resolve_scale(
#     #     y='shared',
#     #     # x='independent'  # 'shared'
#     # )
#
#     forest_chart = forest_chart.facet(
#         data=data,
#         row=alt.Row(
#             "country",
#             title=None,
#             header=alt.Header(
#                 labelAngle=0,
#                 labelAlign='left',
#                 # labelFontSize=12,
#                 labelFontWeight='bold',
#                 # labelPadding=5,
#             ),
#         )
#     )
#
#     forest_chart = forest_chart.properties(
#         title={'text': "Association of injectable contraceptive and discontinuation",
#                'anchor': 'start',
#                'subtitle': " "},  # Avoid explicit `configure_title`
#     )
#     forest_chart = forest_chart.interactive()
#     if configure:
#         forest_chart = forest_chart.configure_view(
#             strokeWidth=0,
#         ).configure_facet(
#             spacing=13,
#         )
#     return forest_chart
#
#
# def plot_forest_panel_placebo(data, plot_neutral_odds=True, precision=2, configure=True):
#     base = alt.Chart(
#         height=20,
#         width=200,
#     )
#     dots = base.mark_point(
#         filled=True,
#         opacity=1,
#         size=80,
#     ).encode(
#         x=alt.X("effect",
#                 title="Risk ratio",
#                 scale=alt.Scale(type="log",
#                                 nice=False, padding=10,
#                                 # domain=(0.95, 2.05)
#                                 ),
#                 axis=alt.Axis(
#                     # tickMinStep=0.5,
#                     # tickCount=6,
#                     values=[0.6, 0.8, 1, 1.3, 1.6, 2, 3],  # Should be changed per task
#                     # grid=False,
#                 )
#                 ),
#         y=alt.Y("estimate",
#                 title=None,
#                 axis=None,
#                 ),
#         color=alt.Color(
#             "estimate",
#             scale=alt.Scale(
#                 domain=['Estimate', 'Placebo'],
#                 range=['#1f77b4', '#8aa9d4']
#             ),
#         ),
#         tooltip=data.columns.tolist(),
#     )
#     error_bars = base.mark_errorbar(
#         ticks={"size": 6},
#         # color='black'
#     ).encode(
#         x=alt.X("ci_lower", title=''),
#         x2=alt.X2("ci_upper", title=''),
#         y=alt.Y("estimate"),
#         color=alt.Color(
#             "estimate",
#             scale=alt.Scale(
#                 domain=['Estimate', 'Placebo'],
#                 range=['#1f77b4', '#8aa9d4']
#             ),
#         ),
#     )
#     forest_chart = error_bars + dots
#
#     if plot_neutral_odds:
#         neutral_threshold = base.transform_calculate(
#             neutral_odds='1.0'
#         ).mark_rule(
#             color='grey',  # '#c5c6c7',
#             strokeDash=[8, 8],
#             strokeWidth=1.3,
#         ).encode(
#             x=alt.X('neutral_odds:Q')
#         )
#         forest_chart = neutral_threshold + forest_chart
#
#     forest_chart = forest_chart.facet(
#         data=data,
#         row=alt.Row(
#             "country",
#             title=None,
#             header=alt.Header(
#                 labelAngle=0,
#                 labelAlign='left',
#                 # labelFontSize=12,
#                 labelFontWeight='bold',
#                 # labelPadding=5,
#             ),
#         ),
#         column=alt.Column(
#             "model",
#             title=None,
#             header=alt.Header(
#                 labelFontSize=12,
#                 labelFontWeight='bold',
#                 labelPadding=5,
#             ),
#         )
#     )
#
#     forest_chart = forest_chart.properties(
#         title={'text': "Association of injectable contraceptive and discontinuation",
#                'anchor': 'start',
#                'subtitle': " "},  # Avoid explicit `configure_title`
#     )
#     forest_chart = forest_chart.interactive()
#     if configure:
#         forest_chart = forest_chart.configure_view(
#             strokeWidth=0,
#         ).configure_facet(
#             spacing=13,
#         )
#     return forest_chart

