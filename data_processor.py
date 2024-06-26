"""Process raw-usage-data into averages."""

import csv
import datetime
from os import path
import numpy as np
import calendar
from io import TextIOWrapper
import argparse
import default_values


# TODO: Refactor to use np nxn arrays and reader
def get_data(
    file_path: str, from_date: None | datetime.datetime = None
) -> {int: [np.array]}:
    days_of_week = [i for i in range(7)]
    data = {i: [[] for i in range(24)] for i in days_of_week}
    with open(file_path, "r") as data_file:
        reader = csv.reader(data_file, delimiter=",")
        file_header = True
        for row in reader:
            if file_header:
                file_header = False
                continue
            header = False
            date = datetime.date.fromisoformat(row[0].strip())
            if from_date is not None and date < from_date:
                continue
            day = date.weekday()
            for i, value in enumerate(row):
                if header == False:
                    header = True
                    continue
                data[day][i - 1].append(value)
    for day, day_data in data.items():
        for i, hour_array in enumerate(day_data):
            data[day][i] = np.array([float(i) for i in hour_array])
    return data


def construct_averages(data: {int: [np.array]}) -> {int: [int]}:
    result = {i: [] for i in data.keys()}
    for day, day_data in data.items():
        for _, hour_array in enumerate(day_data):
            result[day].append(hour_array.mean())
    return result


def write_header(data_file: TextIOWrapper) -> None:
    data_file.write(
        "Day, 00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23\n"
    )


def save_averages(file_path: str, data: {int: [int]}) -> None:
    with open(file_path, "w") as analysis_file:
        write_header(analysis_file)
        writer = csv.writer(analysis_file, delimiter=",")
        for day, day_data in data.items():
            writer.writerow([calendar.day_abbr[day]] + day_data)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="DataProcessor",
        description="Generate averages for each hour of usage in a week.",
    )
    parser.add_argument(
        "usage_file",
        default=default_values.usage_data_file_path,
        help="The path to the file that contains your usage data.",
        nargs="?",
    )
    parser.add_argument(
        "analysis_file",
        default=default_values.analysis_file_path,
        help="The path to where you want to output the analysis data.",
        nargs="?",
    )
    parser.add_argument(
        "-d",
        "--from-date",
        help="A date from which to calculate the averages in ISO format: 1970-01-01.",
    )
    args = parser.parse_args()
    if args.from_date is not None:
        args.from_date = datetime.date.fromisoformat(args.from_date)
    data = get_data(args.usage_file, args.from_date)
    # for day, day_data in get_data(data_file_path).items():
    #     for hour_array in day_data:
    #         print(hour_array)
    # print(construct_averages(data))
    averages = construct_averages(data)
    save_averages(args.analysis_file, averages)


if __name__ == "__main__":
    main()
