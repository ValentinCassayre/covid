import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.patheffects
import matplotlib
from adjustText import adjust_text

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

matplotlib.rcParams['figure.dpi'] = 300

fig, ax = plt.subplots(figsize=(10, 5))

ax.set_yscale('log')  # Log scale

plt.grid(True)

texts = []

for country in countries_of_interest:
    country_display = country.replace("_", " ")

    data = df[df.country == country].copy().set_index('date')[['cases', 'deaths']].cumsum()
    data = data[data.cases >= start_at]  # Normalize starting point
    data = data.reset_index()

    to_plot = data.cases

    highlight = len(data) > 10

    color = None if highlight else 'lightgray'
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
        text = ax.annotate(country_display, (last_pos[0] + 0.3, last_pos[1]),
                           size=8, color=color,
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

ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:,}'.format(x).replace(",", " ")))
plt.yticks(ticks)

adjust_text(texts)

plt.xlabel("Nombre de jours depuis le %sème cas" % start_at)

plt.title("Nombre de cas cumulés jour par jour depuis le %sème cas" % start_at)

plt.show()
