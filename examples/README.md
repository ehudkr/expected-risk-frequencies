# Usage examples

## Main functionality
### Generate an icon array plot with overlaid text
```python
from expected_frequencies import expected_frequencies
baseline_risk = 10.2 / 100
odds_ratio = 5.21
result = expected_frequencies(
    baseline_risk, odds_ratio, "odds_ratio",
    population_name="hospitalized patients",
    event_name="ARDS",
    risk_factor_name="test positive for SARS-CoV-2",
    plot_kwargs={"chart_width": 450, "chart_height": 380},
    plot_text=True
)
print(result.text)
# Out of 100 hospitalized patients who did not test positive for SARS-CoV-2, we should expect 10 of them to also have ARDS.
# Out of 100 hospitalized patients who did test positive for SARS-CoV-2, we should expect 37 of them to also have ARDS.
result.chart.show()
```
![Isotype-grid plot](isotype_grid.png)

Risk reduction looks slightly different:
```python
from expected_frequencies import  plot_expected_frequencies
baseline_risk = 43.7 / 100
odds_ratio = 0.36
chart = plot_expected_frequencies(
    baseline_risk, odds_ratio, "odds_ratio",
)
```
![isotype grid for risk reduction](isotype_grid_reduction.png)

## Additional Functionality
### Multiple panels:
Make each panel slightly smaller than default,
adjusting icon size, width and height.
```python
import pandas as pd
import altair as alt
from expected_frequencies import plot_expected_frequencies
data = pd.DataFrame({
    "baseline_risk": [10.2 / 100, 5.4 / 100],
    "odds_ratio": [5.21, 2.0]
}, index=["Outcome 1", "Outcome 2"])
charts = []
for _, row in data.iterrows():
    chart = plot_expected_frequencies(
        row['baseline_risk'], row['odds_ratio'], "odds_ratio",
        stroke_width=2, icon_size=50, chart_width=250, chart_height=300,
        title=row.name,
        configure_chart=False  # Important for later concatenation
    )
    charts.append(chart)
charts = alt.hconcat(
    *charts
).configure_view(
    strokeWidth=0,
)
```
![two-panel isotype-grid](multi_panel_chart.png)


### Changing the icon
Say you're working on a zoological paper,
you can replace the person icons with any 
[SVG path string](https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths) 
you wish.
```python
from expected_frequencies import plot_expected_frequencies
from urllib import request
# Get cat icon:  (cat SVG by Raúl Inc)
cat_svg = request.urlopen("https://upload.wikimedia.org/wikipedia/commons/5/5b/Cat_%2849952%29_-_The_Noun_Project.svg")
cat_svg = str(cat_svg.read())
cat_shape = cat_svg[cat_svg.index(" d=") + 4: cat_svg.index("></path>") - 1]
# Plot:
chart = plot_expected_frequencies(
    21.2 / 100, 6.8, "odds_ratio",
    population_size=49,
    icon_shape=cat_shape, icon_size=2.5,
    stroke_width=2.5, chart_width=500, chart_height=450,
)
```
![Isotype-grid of cats](cat_chart.png)


## Forest plots
Generate forest plot with text:
```python
from expected_frequencies import forest_plot
chart = forest_plot(
    x="risk_ratio", y="outcome",
    data=data,
    lower="ci_lower", upper="ci_upper",
    neutral=1.0,
    logscale=True,
    with_text=True,  # <- Set to `True` 
    text_decimals=2,
    configure=True,
).properties(
    title="Risk associated with treatment"
)
```
![Forest-plot with text](forest_plot-text.png)

Generate forest plot with groupings:
```python
from expected_frequencies import forest_plot
chart = forest_plot(
    x="risk_ratio", y="outcome",
    data=data,
    hue="model",  # <- Map a data variable to `hue`
    panel=None,
    lower="ci_lower", upper="ci_upper",
    neutral=1.0,
    logscale=False,
).properties(
    title="Risk associated with treatment"
)
```
![Forest-plot with colored grouping](forest_plot-colored.png)

Generate multi-panel forest plot
```python
from expected_frequencies import forest_plot
chart = forest_plot(
    x="risk_ratio", y="outcome",
    data=data,
    hue=None,
    panel="model",  # <- Map a data variable to `panel`
    lower="ci_lower", upper="ci_upper",
    neutral=1.0,
    logscale=True,
).properties(
    title="Risk associated with treatment"
)
```
![Multi-panel forest-plot](forest_plot-column_panels.png)

Both colored and multi-panel plots are also possible:
```python
from expected_frequencies import forest_plot

chart = forest_plot(
    x="risk_ratio", y="outcome",
    data=data,
    hue="hypothesis",
    panel="model",
    lower="ci_lower", upper="ci_upper",
    neutral=1.0,
    logscale=True,
    tooltip=False,
    configure=True,
).properties(
    title="Risk associated with treatment"
)
```
![Multi-panel colored forest-plot](forest_plot-colored_panels.png)
