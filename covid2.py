import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.patheffects
import matplotlib
from adjustText import adjust_text

output_directory = 'out/'
output_plotname = 'trajectories.png'
filename = 'covid_data.xls'
start_at = 100  # Start value of y-axis
cases_treshold = start_at  # Minimum number of cases to include country

names = {'DateRep': 'date', 'Cases': 'cases', 'Deaths': 'deaths', 'Countries and territories': 'country', 'GeoId': 'geoid'}

df = pd.read_excel(filename)
df = df.drop(columns=list(set(df.columns.tolist()) - names.keys()))  # Drop unnecessary columns for convenience
df = df.rename(columns=names)  # Rename columns (also for convenience)

df = df.sort_values(by='date')  # Sort rows by date

# Cases and deaths per country
stats_per_country = df.groupby('country')[['cases', 'deaths']].sum()

# Filtering countries
countries_of_interest = stats_per_country[(stats_per_country.cases > cases_treshold) & (~stats_per_country.index.str.contains('Cases'))].cases.sort_values().index.tolist()

def cumsum(country):
    data = df[df.country == country].copy().set_index('date')[['cases', 'deaths']].cumsum()
    data = data[data.cases >= start_at]  # Normalize starting point
    data = data.reset_index()

    return data

per_country = {}

fits = []

max_period = 0
for country in countries_of_interest:
    data = cumsum(country)
    per_country[country] = data
    if country != 'China':
        max_period = max(len(data) + 3, max_period)  # Add a few days


matplotlib.rcParams['figure.dpi'] = 300

fig, ax = plt.subplots(figsize=(10, 5))

ax.set_yscale('log')  # Log scale

plt.grid(True)

texts = []

def get_color(country):
    if country == 'China':
        return "#cf6102"
    elif country == 'South Korea' or country == 'Japan' or country == 'Singapore':
        return "#02cfcf"
    elif country == 'Italy':
        return "#018c16"
    elif country == 'France':
        return "#437fba"
    elif country == 'United States of America':
        return "#0d30db"
    elif country == "Spain":
        return "#dbb90d"
    elif country == "Germany":
        return "#423d24"
    elif country == "United Kingdom":
        return "#9c1e74"
    elif country == "Iran":
        return "#96a61b"
    else:
        return None

for country in countries_of_interest:
    country_display = country.replace("_", " ")

    data = per_country[country]

    to_plot = data.head(max_period).cases

    highlight = len(data) > 10

    color = get_color(country_display) if highlight else 'lightgray'
    font_weight = 'bold' if color is not None else None
    color = "#919191" if color is None else color
    line_width = 1 if highlight else 0.5
    marker_kind = 'o' if highlight else None
    marker_size = 2
    marker_size_last = marker_size * 2
    marker_edge_last = 0.5

    [p] = plt.plot(to_plot, marker=marker_kind, markersize=marker_size, color=color, linewidth=line_width)
    color = p.get_color()

    last = to_plot.tail(1)

    if highlight:
        plt.plot(to_plot.tail(1), marker=marker_kind, markersize=marker_size_last, color=color, markeredgewidth=marker_edge_last, markeredgecolor='black')
        last_pos = last.reset_index().to_numpy()[0]
        display = "%s (after %s days)" % (country_display, max_period - 1) if country == 'China' else country_display
        text = ax.annotate(display, (last_pos[0] + 0.3, last_pos[1]),
                           size=8, color=color, weight=font_weight,
                           path_effects=[matplotlib.patheffects.withStroke(linewidth=1, foreground="white")])
        texts.append(text)


plt.axis([0, None, start_at, None])  # Axis bounds

maxy = stats_per_country.cases.max()

ticks_base = [1, 2, 5]
ticks = []
i = 0
loop = True
while loop:
    for t in ticks_base:
        tick = t * (10 ** i)
        if tick >= start_at:
            ticks.append(tick)
        if tick > maxy:
            loop = False
            break
    i += 1

ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:,}'.format(x)))
plt.yticks(ticks)

adjust_text(texts)

plt.xlabel("Number of days since the %sth case" % start_at)

plt.title("Cumulative number of cases per country on a daily basis since the %sth case" % start_at)

plt.savefig(output_directory + output_plotname)

# --

with open("html/index.html", 'r') as file:
    template = file.read()
    image = """<img src="%s" alt="Trajectories by country" class="col-12"/>""" % output_plotname
    result_graphs = template.replace("{0}", image)
    output_filename = "%s%s" % (output_directory, "index.html")
    with open(output_filename, "w") as output:
        output.write(result_graphs)
