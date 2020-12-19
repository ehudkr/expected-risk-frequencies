# Convert different statistical risk measures to absolute risk (through relative risk)

def __odds_ratio_to_risk_ratio(baseline_risk, odds_ratio):
    # https://en.wikipedia.org/wiki/Odds_ratio#Relation_to_relative_risk
    rr = odds_ratio / (1 - baseline_risk + (odds_ratio * baseline_risk))
    return rr


def __hazard_ratio_to_risk_ratio(baseline_risk, hazard_ratio):
    # https://stats.stackexchange.com/a/309095/153005
    rr = (1 - (1 - baseline_risk) ** hazard_ratio) / baseline_risk
    rr = hazard_ratio  # RealRisk treats HR as RR
    return rr


def __risk_ratio_to_risk_ratio(baseline_risk, risk_ratio):
    return risk_ratio


def __percentage_change_to_risk_ratio(baseline_risk, percentage_change):
    # Calculate the quantity `rr` for which `exposed_absolute_risk == baseline_risk * rr`
    rr = 1 + percentage_change / 100
    return rr


risk_ratio_conversion_funcs = {
    "odds_ratio": __odds_ratio_to_risk_ratio,
    "hazard_ratio": __hazard_ratio_to_risk_ratio,
    "percentage_change": __percentage_change_to_risk_ratio,
    "risk_ratio": __risk_ratio_to_risk_ratio,
    "relative_risk": __risk_ratio_to_risk_ratio,
}


def calculate_exposed_absolute_risk(baseline_risk, added_risk, added_risk_type):
    added_risk_type = added_risk_type.lower()
    conversion_func = risk_ratio_conversion_funcs.get(added_risk_type)
    if conversion_func is None:
        raise ValueError(f"Only supported conversion functions are "
                         f"{list(risk_ratio_conversion_funcs.keys())}")
    risk_ratio = conversion_func(baseline_risk, added_risk)
    exposed_risk = baseline_risk * risk_ratio
    return exposed_risk
