"""Plot plan comparison data using matplotlib."""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import statistics_generator
import default_values


def main():
    """Plot plan comparison data."""
    usage_data = statistics_generator.get_analysis(default_values.analysis_file_path)
    profiles = statistics_generator.get_profiles(default_values.profiles_directory)
    comparison_data = statistics_generator.compare_plans(profiles, usage_data)
    x_axis = [p[0] for p in comparison_data]
    y_axis = [p[1] for p in comparison_data]
    axis = plt.subplot()
    axis.set_xticklabels(x_axis, rotation=25, ha="right")
    axis.plot(x_axis, y_axis)
    plt.show()


if __name__ == "__main__":
    main()
