""" holds the main functions to create analysis data from processed data using functions from 
garch modelling.py and statistical analysis.py"""

import src.analysis.statistical_analysis as s
import src.analysis.garch_modelling as g

from src.data_helper import load_csv,save_csv
from src.config import ANALYSIS_DATA_DIR

#====================
#FUNCTIONS
#====================

def generate_statistical_data():
    "runs full suite of statistical functions on available data"
    master = load_csv("master", ANALYSIS_DATA_DIR)
    returns = load_csv("returns", ANALYSIS_DATA_DIR)

    datasets = {
        "returns": s.calculate_returns(master),
        "sq_returns" : s.calculate_returns_squared(returns)

    }

    datasets["vol_7"] = s.calculate_rolling_volatility(datasets["returns"],7)
    datasets["vol_30"] = s.calculate_rolling_volatility(datasets["returns"],30)

    for name, dataframe in datasets.items():
        save_csv(name,dataframe,ANALYSIS_DATA_DIR,True)
        stats = s.calculate_statistics(dataframe)
        save_csv(f"{name}_stats",stats,ANALYSIS_DATA_DIR,True)

    return

def garch_suitability_test():
    """ performs preliminary checks (arch lm and adf) for garch suitability on datasets"""

    arch_lm_result = g.arch_lm_test()
    adf_results = g.adf_test()

    arch_lm_result = arch_lm_result.set_index("index")
    print(arch_lm_result)

    adf_results = adf_results.set_index("index")
    print(adf_results)

    results = arch_lm_result.merge(adf_results, on="index")
    save_csv("arch suitability",results,ANALYSIS_DATA_DIR,True)

    return

