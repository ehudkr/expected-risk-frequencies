import math
import warnings
import altair as alt
# from typing import List

from .risk_conversions import calculate_exposed_absolute_risk


PERSON_SHAPE = (
        "M1.7 -1.7h-0.8c0.3 -0.2 0.6 -0.5 0.6 -0.9c0 -0.6 "
        "-0.4 -1 -1 -1c-0.6 0 -1 0.4 -1 1c0 0.4 0.2 0.7 0.6 "
        "0.9h-0.8c-0.4 0 -0.7 0.3 -0.7 0.6v1.9c0 0.3 0.3 0.6 "
        "0.6 0.6h0.2c0 0 0 0.1 0 0.1v1.9c0 0.3 0.2 0.6 0.3 "
        "0.6h1.3c0.2 0 0.3 -0.3 0.3 -0.6v-1.8c0 0 0 -0.1 0 "
        "-0.1h0.2c0.3 0 0.6 -0.3 0.6 -0.6v-2c0.2 -0.3 -0.1 "
        "-0.6 -0.4 -0.6z"
    )
CROSS_SHAPE = "M -1.7 -2.5 L 2.5 3.5"


def plot_expected_frequencies(baseline_risk, added_risk, added_risk_type, population_size=100,
                              title="", configure_chart=True,
                              icon_shape=PERSON_SHAPE, icon_size=75, stroke_color="black", stroke_width=1.3,
                              cross_shape=CROSS_SHAPE, cross_width=None,
                              chart_width=350, chart_height=400):
    """Plots an icon array (isotype grid) of expected frequencies.

    Parameters
    ----------
    baseline_risk : float
                    The fraction ([0.0, 1.0]) of samples in the control group (i.e. WITHOUT the risk-factor)
                    That also had the outcome (event) of interest.
    added_risk : float
                 The value of the association measure (e.g., the odds-ratio or hazard-ratio).
    added_risk_type : {'odds_ratio', 'hazard_ratio', 'risk_ratio', 'percentage_change'}
                      The type of association measure provided.
    population_size : int, optional
                      Size of the hypothetical population on which to calculate the expectancy.
    title : str, optional
            Chart title.
    configure_chart : bool, optional
                      Whether to configure some aesthetics of the chart.
                      Pass `False` if you wish to later concatenate several charts (e.g., `alt.vconcat()`)
    icon_shape : str
                 SVG path of an icon to plot. Defaults to a person icon.
    icon_size : float or int, optional
                The size of the person icon in the array.
                If changed consider also adjusting `chart_width` and `chart_height`.
    stroke_color : str or bool, optional
                   Contour around the person icon.
                   A legal color value Altair can read. Pass False if you wish to not draw contour.
    stroke_width : float, optional
                   The thickness of the icon's contour.
    cross_shape : str, optional
                  SVG path of some cross mark to overlay over the icon shape.
                  Default is a diagonal cross mark (\).
    cross_width : float, optional
                  Stroke thickness of the cross shape. If not provided, a reasonable one is calculated.
    chart_width : int, optional
    chart_height : int, optional

    Returns
    -------
    alt.Chart
        Icon array of expected frequencies

    """
    baseline_ef, exposed_ef = (
        _calculate_expected_frequencies(baseline_risk, added_risk, added_risk_type, population_size)
    )
    chart = _plot_isotype_array(baseline_ef, exposed_ef, population_size,
                                title, configure_chart,
                                icon_shape, icon_size, stroke_color, stroke_width,
                                cross_shape, cross_width,
                                chart_width, chart_height)
    return chart


def phrase_expected_frequencies(baseline_risk, added_risk, added_risk_type,
                                population_name, event_name, risk_factor_name,
                                followup_duration="", population_size=100, precision=0):
    """Generates a textual phrase conveying the baseline and exposed risk.

    Parameters
    ----------
    baseline_risk : float
                    The fraction ([0.0, 1.0]) of samples in the control group (i.e. WITHOUT the risk-factor)
                    That also had the outcome (or event) of interest.
    added_risk : float
                 The value of the association measure (e.g., the odds-ratio or hazard-ratio).
    added_risk_type : {'odds_ratio', 'hazard_ratio', 'risk_ratio', 'percentage_change'}
                      The type of association measure provided.
    population_name : str
                      A description of the study population. (e.g., 'hospitalized men between ages 45 to 64')
    event_name : str
                 What is the measured outcome of the analysis. (e.g., 'acute respiratory disorder')
    risk_factor_name : str
                       What is the risk-factor or treatment group tested. (e.g., 'go through surgery')
    followup_duration : str, optional
                        What was the followup time (e.g., '3 years').
    population_size : int, optional
                      Size of the hypothetical population on which to calculate the expectancy.
    precision : int, optional
                How many decimals to round the expected frequencies (the default is 0).
    Returns
    -------
    str
        A textual phrasing of the expected frequency in both risk groups.
    """
    baseline_ef, exposed_ef = (
        _calculate_expected_frequencies(baseline_risk, added_risk, added_risk_type, population_size)
    )
    text = _generate_text(
        baseline_ef, exposed_ef,
        population_size, precision,
        population_name, event_name, risk_factor_name, followup_duration
    )
    return text


def expected_frequencies(baseline_risk, added_risk, added_risk_type,
                         population_size=100, precision=0,
                         population_name="", event_name="", risk_factor_name="", followup_duration="",
                         plot_kwargs=None, plot_text=False):
    """Calculates expected frequencies, plots them as an icon-array (isotype-grid),
    and generates a textual phrase conveying the expected frequencies.

    Parameters
    ----------
    baseline_risk : float
                    The fraction ([0.0, 1.0]) of samples in the control group (i.e. WITHOUT the risk-factor)
                    That also had the outcome (or event) of interest.
    added_risk : float
                 The value of the association measure (e.g., the odds-ratio or hazard-ratio).
    added_risk_type : {'odds_ratio', 'hazard_ratio', 'risk_ratio', 'percentage_change'}
                      The type of association measure provided.
    population_size : int, optional
                      Size of the hypothetical population on which to calculate the expectancy.
    precision : int, optional
                How many decimals to round the expected frequencies (the default is 0).
    population_name : str, optional
                      A description of the study population. (e.g., 'hospitalized men between ages 45 to 64')
    event_name : str, optional
                 What is the measured outcome of the analysis. (e.g., 'acute respiratory disorder')
    risk_factor_name : str, optional
                       What is the risk-factor or treatment group tested. (e.g., 'go through surgery')
    followup_duration : str, optional
                        What was the followup time (e.g., '3 years').
    plot_kwargs : dict, optional
                  Keyword arguments for plotting an icon array.
                  See the documentation of `plot_expected_frequencies` for details.
    plot_text : bool, optional
                Whether to add the generated text as a title to the chart.

    Returns
    -------
    ExpectedFrequencies
        A result object containing:
         * `baseline_expected_frequencies` - expected frequencies without the risk factor
         * `exposed_expected_frequencies` - expected frequencies with the risk factor
         * `chart` - Altair Chart of an icon array depicting the expected frequencies
         * `text` - textual phrasing conveying the expected frequencies.

    """
    plot_kwargs = plot_kwargs if plot_kwargs else {}

    baseline_ef, exposed_ef = (
        _calculate_expected_frequencies(baseline_risk, added_risk, added_risk_type, population_size)
    )
    # baseline_ef = round(baseline_ef, precision)
    # exposed_ef = round(exposed_ef, precision)

    text = _generate_text(
        baseline_ef, exposed_ef,
        population_size, precision,
        population_name, event_name, risk_factor_name, followup_duration
    )

    plot_title = text.replace(",", ",\n").split("\n") if plot_text else None
    if "title" not in plot_kwargs.keys():  # A different title not already provided
        plot_kwargs["title"] = plot_title
    chart = _plot_isotype_array(
        baseline_ef, exposed_ef,
        population_size, **plot_kwargs
    )

    result = ExpectedFrequencies(baseline_ef, exposed_ef,
                                 chart, text)
    return result


def _calculate_expected_frequencies(baseline_risk, added_risk, added_risk_type, population_size):
    """Convert risk to absolute risk and calculate expected frequencies"""
    exposed_absolute_risk = calculate_exposed_absolute_risk(baseline_risk, added_risk, added_risk_type)

    baseline_ef = population_size * baseline_risk
    exposed_ef = population_size * exposed_absolute_risk
    return baseline_ef, exposed_ef


def _generate_text(baseline_ef, exposed_ef, population_size, precision,
                   population_name, event_name, risk_factor_name, followup_duration=""):
    base_text = (
        f"Out of {population_size:d} {population_name} who did {{exposed}}{risk_factor_name}, "
        f"we should expect {{ef:.{precision}f}} of them to also have {event_name}"
        f"{f' over {followup_duration}' if followup_duration else ''}.\n"
    )

    text = ""
    for ef, exposed in zip([baseline_ef, exposed_ef], [False, True]):
        text += base_text.format(ef=ef, exposed="" if exposed else "not ")

    return text


def _plot_isotype_array(baseline_ef, exposed_ef, population_size=100, title="", configure_chart=True,
                        icon_shape=PERSON_SHAPE, icon_size=75, stroke_color="black", stroke_width=1.3,
                        cross_shape=CROSS_SHAPE, cross_width=None,
                        chart_width=350, chart_height=400):
    if isinstance(baseline_ef, float) or isinstance(exposed_ef, float):
        warnings.warn("Can't currently plot (color) fractional icons. Rounding to nearest integer.")
    baseline_ef = round(baseline_ef)
    exposed_ef = round(exposed_ef)

    data = __generate_chart_source_data(baseline_ef, exposed_ef, population_size)

    root = round(math.sqrt(population_size))  # Create a square grid of total `population_size`

    # https://altair-viz.github.io/gallery/isotype_grid.html
    base_chart = alt.Chart(data).transform_calculate(
        row=f"ceil(datum.id/{root})",
        col=f"datum.id - datum.row*{root}",
    ).encode(
        x=alt.X("col:O", axis=None),
        y=alt.Y("row:O", axis=None),
    ).properties(
        width=chart_width,
        height=chart_height,
        title=title if title else ""
    )
    icons = base_chart.mark_point(
        filled=True,
        stroke=stroke_color,
        strokeWidth=stroke_width,  # 2,
        size=icon_size,
    ).encode(
        color=alt.Color(
            'hue:N',
            scale=alt.Scale(
                domain=[0, 1, 2],  # Explicitly specify `hue` values or coloring will fail if <3 levels exist in data
                range=[
                    "#FFFFFF",  # Population (0)
                    "#4A5568",  # Baseline (1)
                    "#FA5765",  # Exposed (2)  "#4078EF"
                ]),
            # TODO: add uncertainty using shade: lighter color fill of icons in the 95% CI.
            legend=None),
        shape=alt.ShapeValue(icon_shape),
    )
    chart = icons
    if exposed_ef < baseline_ef:
        stroke_out = base_chart.mark_point(
            # shape="cross",
            filled=True,
            stroke="#4078EF",  # "black"
            # strokeWidth=cross_width,
            strokeWidth=math.sqrt(icon_size) / 1.7 if cross_width is None else cross_width,
            strokeCap="round",
            size=icon_size,
        ).encode(
            shape=alt.ShapeValue(cross_shape),
            opacity=alt.Opacity(
                'reduced:N',
                legend=None,
                scale=alt.Scale(
                    domain=[False, True],
                    range=[0, 1]
                ),
            )
        )
        chart += stroke_out
    if configure_chart:  # Configured charts cannot be later concatenated.
        chart = chart.configure_title(
            align="left",
            anchor="start",
            offset=-10,
        ).configure_view(
            strokeWidth=0,
        )

    return chart


def __generate_chart_source_data(baseline_ef, exposed_ef, population_size):
    """Generate data to plug into Altair chart. shape = (`population_size`, 3).
    Columns: - `id`: base-1 counting from 1 to `population_size` + 1,
             - `hue`: 0: entire population, 1: baseline risk people, 2: additional exposed risk people.
             - `reduced`: In risk reduction, whether to cross out a baseline-risk icon
    """
    data = [{"id": i, "hue": 0, "reduced": False}
            for i in range(1, population_size + 1)]
    for row in data[:baseline_ef]:
        row['hue'] = 1  # data.iloc[:baseline_ef]['hue'] = "Baseline"
    if exposed_ef >= baseline_ef:  # Additional units under expose
        for row in data[baseline_ef:exposed_ef]:
            row['hue'] = 2  # data.iloc[baseline_ef:exposed_ef]['hue'] = "Exposed"
    else:  # Baseline units to "remove" from the outcome
        for row in data[baseline_ef - exposed_ef:baseline_ef]:
            row['reduced'] = True  # data.iloc[baseline_ef:exposed_ef]['reduced'] = True
    data = alt.Data(values=data)
    return data


class ExpectedFrequencies:
    def __init__(self, baseline_expected_frequencies,
                 exposed_expected_frequencies,
                 chart, text):
        """Data class containing the results from running `expected_frequencies()`.

        Parameters
        ----------
        baseline_expected_frequencies : float
            Expected frequencies without the risk factor
         exposed_expected_frequencies : float
            Expected frequencies with the risk factor
         chart : alt.Chart
            Icon array depicting the expected frequencies
         text : str
            Textual phrasing conveying the expected frequencies
        """
        self.baseline_expected_frequencies = baseline_expected_frequencies
        self.exposed_expected_frequencies = exposed_expected_frequencies
        self.chart = chart
        self.text = text

    def __repr__(self):
        s = (f"ExpectedFrequencies: "
             f"baseline - {self.baseline_expected_frequencies:.0f}, "
             f"exposed - {self.exposed_expected_frequencies:.0f}.")
        return s
