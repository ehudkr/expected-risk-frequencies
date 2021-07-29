from expected_frequencies.forest_plot import forest_plot

import pandas as pd
from altair_saver import save as alt_save
from selenium import webdriver as WebDriver


CHROMEDRIVER_PATH = "../webdriver/chromedriver.exe"
webdriver = WebDriver.Chrome(CHROMEDRIVER_PATH)


data = pd.DataFrame([
    ["Alternative", "Hepatic", "Unadjusted", 1.26, 0.79, 2.24],
    ["Alternative", "Hepatic", "IPW", 1.1, 0.67, 2.0],
    ["Alternative", "Hepatic", "Standardization", 1.13, 0.7, 2.03],
    ["Alternative", "Renal", "Unadjusted", 2.01, 1.46, 2.86],
    ["Alternative", "Renal", "IPW", 1.67, 1.17, 2.36],
    ["Alternative", "Renal", "Standardization", 1.65, 1.18, 2.33],
    ["Alternative", "Cardiovascular", "Unadjusted", 1.86, 1.33, 2.69],
    ["Alternative", "Cardiovascular", "IPW", 1.69, 1.19, 2.45],
    ["Alternative", "Cardiovascular", "Standardization", 1.68, 1.19, 2.44],
    ["Alternative", "Sepsis", "Unadjusted", 1.46, 1.08, 2.02],
    ["Alternative", "Sepsis", "IPW", 1.41, 1.04, 1.98],
    ["Alternative", "Sepsis", "Standardization", 1.43, 1.06, 1.99],
    ["Alternative", "Neurological", "Unadjusted", 1.12, 0.84, 1.54],
    ["Alternative", "Neurological", "IPW", 1.08, 0.8, 1.52],
    ["Alternative", "Neurological", "Standardization", 1.09, 0.8, 1.51],
    ["Alternative", "Pulmonary", "Unadjusted", 1.76, 1.22, 2.77],
    ["Alternative", "Pulmonary", "IPW", 1.39, 0.95, 2.19],
    ["Alternative", "Pulmonary", "Standardization", 1.41, 0.96, 2.22],
    ["Alternative", "Hematologic", "Unadjusted", 1.62, 1.29, 2.11],
    ["Alternative", "Hematologic", "IPW", 1.54, 1.19, 2.0],
    ["Alternative", "Hematologic", "Standardization", 1.54, 1.21, 2.0],

    ["Null", "Hepatic", "Unadjusted", None, None, None],
    ["Null", "Hepatic", "IPW", 1.0, 0.62, 1.67],
    ["Null", "Hepatic", "Standardization", 1.0, 0.63, 1.73],
    ["Null", "Renal", "Unadjusted", None, None, None],
    ["Null", "Renal", "IPW", 1.01, 0.71, 1.39],
    ["Null", "Renal", "Standardization", 1.0, 0.71, 1.36],
    ["Null", "Cardiovascular", "Unadjusted", None, None, None],
    ["Null", "Cardiovascular", "IPW", 1.0, 0.71, 1.4],
    ["Null", "Cardiovascular", "Standardization", 1.0, 0.71, 1.4],
    ["Null", "Sepsis", "Unadjusted", None, None, None],
    ["Null", "Sepsis", "IPW", 1.0, 0.76, 1.38],
    ["Null", "Sepsis", "Standardization", 1.0, 0.74, 1.35],
    ["Null", "Neurological", "Unadjusted", None, None, None],
    ["Null", "Neurological", "IPW", 1.01, 0.76, 1.35],
    ["Null", "Neurological", "Standardization", 1.0, 0.76, 1.37],
    ["Null", "Pulmonary", "Unadjusted", None, None, None],
    ["Null", "Pulmonary", "IPW", 1.01, 0.74, 1.47],
    ["Null", "Pulmonary", "Standardization", 1.0, 0.74, 1.43],
    ["Null", "Hematologic", "Unadjusted", None, None, None],
    ["Null", "Hematologic", "IPW", 1.0, 0.82, 1.24],
    ["Null", "Hematologic", "Standardization", 1.0, 0.82, 1.21],
],
    columns=["hypothesis", "outcome", "model", "risk_ratio", "ci_lower", "ci_upper"]
)


chart = forest_plot(
    x="risk_ratio", y="outcome",
    data=data.query("(hypothesis=='Alternative') and (model=='IPW')"),
    lower="ci_lower", upper="ci_upper",
    neutral=1.0,
    logscale=True,
    with_text=True, text_decimals=2,
    configure=True,
).properties(
    title="Risk associated with treatment"
)
alt_save(chart, "forest_plot-text.png",
         method='selenium', webdriver=webdriver)
# chart.save("forest_plot-text.html")


# # No confidence intervals:
# chart = forest_plot(
#     x="risk_ratio", y="outcome",
#     data=data.query("(hypothesis=='Alternative') and (model=='IPW')"),
#     lower=None, upper=None,
#     neutral=1.0,
#     logscale=True,
#     tooltip=True,
#     with_text=True, text_decimals=2,
#     configure=True,
# )
# chart.save("forest_plot-text-2.html")

# # No text:
# chart = forest_plot(
#     x="risk_ratio", y="outcome",
#     data=data.query("(hypothesis=='Alternative') and (model=='IPW')"),
#     lower="ci_lower", upper="ci_upper",
#     neutral=1.0,
#     logscale=True,
#     tooltip=False,
#     with_text=False, text_decimals=2,
#     configure=True,
# )
# chart.save("forest_plot-text-3.html")


chart = forest_plot(
    x="risk_ratio", y="outcome",
    data=data.query("hypothesis=='Alternative'"),
    hue="model",
    panel=None,
    lower="ci_lower", upper="ci_upper",
    neutral=1.0,
    logscale=False,
).properties(
    title="Risk associated with treatment"
)
alt_save(chart, "forest_plot-colored.png",
         method='selenium', webdriver=webdriver)
# chart.save("forest_plot-colored.html")

chart = forest_plot(
    x="risk_ratio", y="outcome",
    data=data.query("hypothesis=='Alternative'"),
    hue=None,
    panel="model",
    lower="ci_lower", upper="ci_upper",
    neutral=1.0,
    logscale=True,
).properties(
    title="Risk associated with treatment"
)
alt_save(chart, "forest_plot-column_panels.png",
         method='selenium', webdriver=webdriver)
# chart.save("forest_plot-column_panels.html")

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
alt_save(chart, "forest_plot-colored_panels.png",
         method='selenium', webdriver=webdriver)
# chart.save("forest_plot-colored_panels.html")
