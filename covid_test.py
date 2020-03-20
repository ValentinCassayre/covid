"""
Created: 09/03/2020
Git: https://github.com/V-def/covid
Display graphs: https://covid19.cassayre.me/
"""

import xlrd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import os
import math

# constants (also used in the functions)
# exact name of the data file
name_file = "covid_data.xls"
# date of the first case (it will not change)
date_first_case = "31/12/2019"
# smallest number of cases or report to deal with the country
cases_min = 100
daily_report_min = 20
# output directory
output_directory = 'out/'
# format of the graph (png/pdf)
graph_format = "png"
graph_size = [12, 10]
graph_info = [graph_size, True, True, False]
log_base = 10
xlabel = "Date"
ylabel = "Cases"
# format of the data from different sources
data_exact_dict = \
    {"Date": "DateRep", "Cases": "Cases", "Deaths": "Deaths", "Country": "Countries and territories", "GeoId": "GeoId"}
data_dict_ecdc = \
    {data_exact_dict["Date"]: 0, data_exact_dict["Cases"]: 4, "Deaths": 5, "Countries and territories": 6, "GeoId": 7}
# https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
country_name = ""
df = pd.read_excel(name_file)

for i in df.index:
    if i + 1 == len(df.index):
        break
    elif df['Countries and territories'][i] == df['Countries and territories'][i+1]:
        if df[data_exact_dict["Country"]][i] != country_name:
            country_name = df[data_exact_dict["Country"]][i]
        date = df["Date"][i]
        cases = df[data_exact_dict["Cases"]][i]
        deaths = df[data_exact_dict["Deaths"]][i]
