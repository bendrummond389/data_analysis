import logging
from models import MortalityRate2014, ACS2017CountyData
from scripts.database import get_session
from scripts.utils import load_config, setup_logging

from statsmodels.stats.outliers_influence import variance_inflation_factor
import pandas as pd


def calculate_vif(data):
    vif_data = pd.DataFrame()
    vif_data["feature"] = data.columns
    vif_data["VIF"] = [variance_inflation_factor(data.values, i) for i in range(len(data.columns))]
    return vif_data



def main():
    # 1. Load configuration
    config = load_config()

    # 2. Set up logging
    setup_logging(config['paths']['log_path'])
    logging.info("Starting the data analysis project.")

    # 3. Get database session
    session = get_session(config['db_config'])

    results = session.query(
        MortalityRate2014.mortality_rate_2014_max,
        ACS2017CountyData.poverty,
        ACS2017CountyData.incomepercap,
        ACS2017CountyData.hispanic,
        ACS2017CountyData.black)\
        .filter(MortalityRate2014.fips_code == ACS2017CountyData.fips_code)\
        .all()

    df = pd.DataFrame(results)

    predictors = df.drop(columns=['mortality_rate_2014_max'])
    vif_results = calculate_vif(predictors)
    print(vif_results)



if __name__ == "__main__":
    main()
