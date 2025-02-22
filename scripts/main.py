import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from models import MortalityRate2014, ACS2017CountyData
from scripts.database import get_session
from scripts.utils import load_config, setup_logging
from sklearn.feature_selection import mutual_info_regression
from statsmodels.stats.outliers_influence import variance_inflation_factor


def calculate_vif(data):
    vif_data = pd.DataFrame()
    vif_data["feature"] = data.columns
    vif_data["VIF"] = [
        variance_inflation_factor(data.values, i) for i in range(len(data.columns))
    ]
    return vif_data


def plot_features_vs_target(df, features, target):
    """
    Plots each feature against the target variable using Seaborn.
    """
    for feature in features:
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x=df[feature], y=df[target], alpha=0.6)
        plt.title(f"{feature} vs {target}")
        plt.xlabel(feature)
        plt.ylabel(target)
        plt.grid(True)
        plt.show()


def calculate_mutual_info(X, y):
    mi = mutual_info_regression(X, y)
    mi_series = pd.Series(mi, index=X.columns)
    return mi_series.sort_values(ascending=False)


def main():
    # 1. Load configuration
    config = load_config()

    # 2. Set up logging
    setup_logging(config["paths"]["log_path"])
    logging.info("Starting the data analysis project.")

    # 3. Get database session
    session = get_session(config["db_config"])

    results = (
        session.query(
            MortalityRate2014.mortality_rate_2014_max,
            ACS2017CountyData.poverty,
            ACS2017CountyData.incomepercap,
            ACS2017CountyData.hispanic,
            ACS2017CountyData.white,
            ACS2017CountyData.childpoverty,
            ACS2017CountyData.unemployment,
            ACS2017CountyData.meancommute,
            ACS2017CountyData.professional,
            ACS2017CountyData.service,
            ACS2017CountyData.privatework,
            ACS2017CountyData.publicwork,
            ACS2017CountyData.selfemployed,
            ACS2017CountyData.familywork,
            ACS2017CountyData.employed,
        )
        .filter(MortalityRate2014.fips_code == ACS2017CountyData.fips_code)
        .all()
    )

    columns = pd.Index(
        [
            "mortality_rate_2014_max",
            "poverty",
            "incomepercap",
            "hispanic",
            "white",
            "childpoverty",
            "unemployment",
            "meancommute",
            "professional",
            "service",
            "privatework",
            "publicwork",
            "selfemployed",
            "familywork",
            "employed",
        ]
    )

    df = pd.DataFrame(results, columns=columns)

    selected_features = ["poverty", "unemployment", "familywork"]
    target = "mortality_rate_2014_max"

    plot_features_vs_target(df, selected_features, target)

    logging.info("Data analysis (including logistic regression) complete.")


if __name__ == "__main__":
    main()
