from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.patheffects
import matplotlib
from adjustText import adjust_text

output_directory = 'out/'
output_cases = 'trajectories_cases.png'
output_deaths = 'trajectories_deaths.png'
source_filename = 'covid_data.xls'
start_at_cases = 100  # Start value of y-axis
start_at_deaths = 10
cases_treshold = start_at_cases  # Minimum number of cases to include country
deaths_treshold = start_at_deaths

names = {'DateRep': 'date', 'Cases': 'cases', 'Deaths': 'deaths', 'Countries and territories': 'country', 'GeoId': 'geoid'}

df = pd.read_excel(source_filename)
df = df.drop(columns=list(set(df.columns.tolist()) - names.keys()))  # Drop unnecessary columns for convenience
df = df.rename(columns=names)  # Rename columns (also for convenience)

df = df.sort_values(by='date')  # Sort rows by date

# Cases and deaths per country
stats_per_country = df.groupby('country')[['cases', 'deaths']].sum()

countries = stats_per_country.index.tolist()

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
    elif country == "Switzerland":
        return "#d65e84"
    elif country == "Netherlands":
        return "#fc9803"
    else:
        return None


def draw_trajectories(filename, variable, start_at, highlight_threshold, variable_display, countries_of_interest):

    def cumsum(country):
        data = df[df.country == country].copy().set_index('date')[[variable]].cumsum()
        data = data[data[variable] >= start_at]  # Normalize starting point
        first = data.iloc[0][variable]
        data[variable] = data[variable] - first + start_at
        data = data.reset_index()

        return data


    base_date = date(2020, 2, 20)
    max_period = (date.today() - base_date).days

    matplotlib.rcParams['figure.dpi'] = 300

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.set_yscale('log')  # Log scale

    plt.grid(True)

    texts = []

    maxy = 0

    for country in countries_of_interest:
        country_display = country.replace("_", " ")

        data = cumsum(country)

        maxy = max(data[variable].max(), maxy)

        to_plot = data.head(max_period)[variable]

        highlight = len(data) >= highlight_threshold

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

    plt.xlabel("Number of days since the %sth %s" % (start_at, variable_display))

    plt.title("Cumulative number of %s per country on a daily basis since the %sth %s" % (variable, start_at, variable_display))

    plt.savefig(output_directory + filename)


# Filtering countries
stats_countries_only = stats_per_country[~stats_per_country.index.str.contains('Cases')]
countries_of_interest_cases = stats_countries_only[stats_countries_only.cases > cases_treshold].cases.sort_values().index.tolist()
countries_of_interest_deaths = stats_countries_only[stats_countries_only.deaths > deaths_treshold].deaths.sort_values().index.tolist()


draw_trajectories(output_cases, 'cases', start_at_cases, 14, 'case', countries_of_interest_cases)
draw_trajectories(output_deaths, 'deaths', start_at_deaths, 7, 'death', countries_of_interest_deaths)

# --

with open("html/index.html", 'r') as file:
    def html_image(path, alt):
        return """<img src="%s" alt="%s" class="col-12"/>""" % (path, alt)

    template = file.read()
    images = [html_image(output_cases, "Trajectories by country"), html_image(output_deaths, "Trajectories by country")]
    result_graphs = template.replace("{0}", "\n".join(images))
    output_filename = "%s%s" % (output_directory, "index.html")
    with open(output_filename, "w") as output:
        output.write(result_graphs)
