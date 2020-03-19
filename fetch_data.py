from datetime import datetime, timedelta
import urllib.request
from urllib.error import HTTPError


def url_for_date(date):
    date_format = date.strftime("%Y-%m-%d")
    return "https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-%s.xls"\
           % date_format


output_file = "covid_data.xls"

# start from today
day = datetime.now()

data = None
trials = 0

while data is None and trials < 3:
    url = url_for_date(day)
    day_str = day.strftime("%d/%m/%Y")
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
        print("File retrieved for %s" % day_str)
    except HTTPError:
        print("Could not find a file for %s" % day_str)

    trials += 1
    day -= timedelta(days=1)

if data is not None:
    with open(output_file, "wb") as file:
        file.write(data)
    print("Successfuly wrote file to disk as '%s'" % output_file)
else:
    print("Error: could not find a suitable file after %s attempts" % trials)
