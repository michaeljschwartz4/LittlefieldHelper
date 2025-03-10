#!/usr/bin/env python3
"""
Littlefield Experiment Data Scraper
Author: Michael Schwartz @mjschwa; UWB C/O 2025

This script logs in to the Littlefield experiment website,
scrapes multiple data series using regex extraction from embedded JavaScript
(which provides day/value pairs in a "points:" field), merges them into one
data structure, and writes the complete dataset to an Excel file ("data.xlsx").

Data series extracted:
  - Inventory (INV)       [two-column, one points string]
  - Other Two-column series:
      CASH, JOBIN, JOBQ, S1Q, S2Q, S3Q, S1UTIL, S2UTIL, S3UTIL
  - Four-column series (each is expected to produce three sets based on user decisions):
      JOBT, JOBREV, JOBOUT

The final DataFrame has 19 columns in this order:
  ["INV", "CASH", "JOBIN", "JOBQ", "S1Q", "S2Q", "S3Q",
   "S1UTIL", "S2UTIL", "S3UTIL",
   "JOBT0", "JOBT1", "JOBT2",
   "JOBREV0", "JOBREV1", "JOBREV2",
   "JOBOUT0", "JOBOUT1", "JOBOUT2"]

A "Backlog" column is computed as:
   cumulative JOBIN minus cumulative JOBOUT0, JOBOUT1, and JOBOUT2.
"""
import mechanize
from bs4 import BeautifulSoup
import http.cookiejar as cookielib
import re
import pandas as pd
import datetime
import sys

"""
    Opens the given URL using the provided mechanize browser instance,
    finds a <script> tag containing "points:", and extracts the
    content of the points string via regex.

    The expected format is:
       points: '1 9480 2 9360 3 9300 ...'
    where each pair represents [day, value].

    Parameters:
      br              : a mechanize.Browser() instance (already logged in)
      url             : URL to fetch
      expected_matches: number of separate points strings expected
                        (1 for two-column pages, >1 for four-column pages)

    Returns:
      A list of dictionaries. Each dictionary maps day (float) to value (float).
    """
def extract_points(br, url, expected_matches=1):
    response = br.open(url)
    soup = BeautifulSoup(response, "html.parser")

    # Search all <script> tags for one containing "points:"
    script_content = None
    for script in soup.find_all("script"):
        if script.string and "points:" in script.string:
            script_content = script.string
            break
    if script_content is None:
        raise Exception("Could not find a script containing 'points:' in URL: " + url)

    matches = re.findall(r"points:\s*'([^']+)'", script_content)
    if expected_matches > 1 and len(matches) < expected_matches:
        print("Warning: Expected {} matches but found {} in URL: {}. Will pad missing series.".format(expected_matches, len(matches), url))

    series_list = []
    for m in matches:
        tokens = m.split()
        series = {}
        # Expect tokens to alternate: day value day value ...
        for i in range(0, len(tokens), 2):
            try:
                day = float(tokens[i])
                value = float(tokens[i+1])
            except Exception as e:
                continue
            series[day] = value
        series_list.append(series)
    return series_list

def main(team_name, password):
    now = datetime.datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Execution started at {formatted}")

    # Setup mechanize browser with cookie jar and login [credentials provided by user]
    cj = cookielib.CookieJar()
    br = mechanize.Browser()
    br.set_cookiejar(cj)

    login_url = "https://op.responsive.net/lt/oneill/entry.html"
    br.open(login_url)
    br.select_form(nr=0)
    br.form['id'] = team_name
    br.form['password'] = password
    br.submit()

    # Global dictionary to hold all data.
    # Keys are simulation days (float); values are lists of measurements.
    LF_DATA = {}

    # Scrape Inventory Data (two-column series)
    inv_url = "http://op.responsive.net/Littlefield/Plot?data=INV&x=all"
    inv_series_list = extract_points(br, inv_url, expected_matches=1)
    inv_series = inv_series_list[0]
    for day, inv_value in inv_series.items():
        LF_DATA[day] = [inv_value]

    # Scrape Other Two-Column Series
    two_col_labels = ["CASH", "JOBIN", "JOBQ", "S1Q", "S2Q", "S3Q", "S1UTIL", "S2UTIL", "S3UTIL"]
    for label in two_col_labels:
        url = "http://op.responsive.net/Littlefield/Plot?data={}&x=all".format(label)
        series_list = extract_points(br, url, expected_matches=1)
        series = series_list[0]
        for day, value in series.items():
            if day not in LF_DATA:
                LF_DATA[day] = []
            LF_DATA[day].append(value)

    # Scrape Four-Column Series
    four_col_labels = ["JOBT", "JOBREV", "JOBOUT"]
    for label in four_col_labels:
        url = "http://op.responsive.net/Littlefield/Plot?data={}&x=all".format(label)
        series_list = extract_points(br, url, expected_matches=3)
        # If fewer than 3 series, pad with dummy series.
        if len(series_list) < 3:
            # Collect all days present in the found series.
            all_days = set()
            for s in series_list:
                all_days.update(s.keys())
            # For each missing series, create a dummy dictionary with 0.0 for each day.
            for _ in range(3 - len(series_list)):
                dummy_series = {day: 0.0 for day in all_days}
                series_list.append(dummy_series)
        # Merge series into LF_DATA.
        for series in series_list:
            for day, value in series.items():
                if day not in LF_DATA:
                    LF_DATA[day] = []
                LF_DATA[day].append(value)

    # Fill in Missing Data
    expected_columns = 19
    for day, values in LF_DATA.items():
        if len(values) < expected_columns:
            values.extend([0] * (expected_columns - len(values)))

    # Removes all non-integer entries from the dataset
    # These occur when the company receives inventory from an order
    LF_DATA = {day: values for day, values in LF_DATA.items() if float(day).is_integer()}

    # Create DataFrame, Compute Backlog, and Write to Excel
    headers = [
        "INV",
        "CASH", "JOBIN", "JOBQ", "S1Q", "S2Q", "S3Q",
        "S1UTIL", "S2UTIL", "S3UTIL",
        "JOBT0", "JOBT1", "JOBT2",
        "JOBREV0", "JOBREV1", "JOBREV2",
        "JOBOUT0", "JOBOUT1", "JOBOUT2"
    ]
    df = pd.DataFrame.from_dict(LF_DATA, orient="index")
    df.columns = headers
    df.sort_index(inplace=True)

    df["Backlog"] = (df["JOBIN"].cumsum() -
                     df["JOBOUT0"].cumsum() -
                     df["JOBOUT1"].cumsum() -
                     df["JOBOUT2"].cumsum())

    excel_file = "data.xlsx"
    writer = pd.ExcelWriter(excel_file, engine="openpyxl")
    df.to_excel(writer, sheet_name="data")
    writer.close()

    print("Data successfully written to '{}'.".format(excel_file))
    now = datetime.datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Execution finished at {formatted}")
if __name__ == "__main__":
    team_name = sys.argv[1]
    password = sys.argv[2]
    main(team_name, password)
