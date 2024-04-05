"""Process averaged data and profiles into statistics."""

import numpy as np
from numpy import typing as npt
import os
import csv
import argparse


def get_analysis(file_path: str) -> npt.NDArray:
    """Get electricity usage analysis data from a file."""
    return np.loadtxt(
        file_path, dtype=float, delimiter=",", skiprows=1, usecols=range(1, 25)
    )


def get_profiles(directory_path: str) -> {str: (float, npt.NDArray)}:
    """Get electricity profiles from a directory."""
    if not os.path.isdir(directory_path):
        raise NotADirectoryError
    profiles = {}
    for data_file in os.listdir(directory_path):
        profile = get_profile(os.path.join(directory_path, data_file))
        profiles[profile[0]] = profile[1]
    return profiles


def get_profile(file_path: str) -> (str, (float, npt.NDArray)):
    """Get electricity provider's cost profile from a csv file."""
    name = os.path.splitext(os.path.basename(file_path))[0]
    data = np.loadtxt(
        file_path,
        dtype=float,
        delimiter=",",
        skiprows=1,
        usecols=range(1, 25),
        max_rows=7,
    )
    with open(file_path, "r") as data_file:
        reader = csv.reader(data_file, delimiter=",")
        for row in reader:
            if len(row) == 2:
                return (name, (float(row[1].strip()), data))


def compare_plans(
    profiles: {str: (float, npt.NDArray)}, usage_data: npt.NDArray
) -> [(str, float)]:
    """Return the calculated and sorted price of running every plan for a year."""
    costs = []
    for name, profile in profiles.items():
        costs.append((name, calculate_yearly_cost(profile, usage_data)))
    return sorted(costs, key=lambda x: x[1])


def print_comparison(data: [(str, float)]) -> None:
    """Pretty-print the comparison data."""
    for i, (name, cost) in enumerate(data):
        print(f"#{i+1:3}: ${cost:6.2f} ({name})")


def calculate_yearly_cost(
    profile: (float, npt.NDArray), usage_data: npt.NDArray
) -> float:
    """Calculate the cost of running a plan for one year."""
    return (
        np.sum(np.multiply(profile[1], usage_data) * (365 / 7)) + 365 * profile[0]
    ) / 100


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="StatisticsGenerator",
        description="Generate statistics on the cost of electricity at a electricity provider for a year.",
    )
    parser.add_argument(
        "analysis_file",
        default="data/analysis.csv",
        help="The path to the file that contains the analysis of your power usage.",
        nargs="?",
    )
    parser.add_argument(
        "profiles_dir",
        default="profiles/Christchurch-Apr-2024/",
        help="The path to the directory that contains the profiles of the electricity providers that you want to compare.",
        nargs="?",
    )
    args = parser.parse_args()
    usage_data = get_analysis(args.analysis_file)
    profiles = get_profiles(args.profiles_dir)
    comparison_data = compare_plans(profiles, usage_data)
    print_comparison(comparison_data)


if __name__ == "__main__":
    main()
