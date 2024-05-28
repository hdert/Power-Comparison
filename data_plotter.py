"""Plot plan comparison data using matplotlib."""

import matplotlib.pyplot as plt
import numpy as np

import statistics_generator
import default_values


def main():
    """Plot plan comparison data."""
    usage_data = statistics_generator.get_analysis(
        default_values.analysis_file_path
    )
    profiles = statistics_generator.get_profiles(
        default_values.profiles_directory
    )
    comparison_data = statistics_generator.compare_plans(profiles, usage_data)
    x_axis = [p[0] for p in comparison_data]
    y_axis = [p[1] for p in comparison_data]
    axis = plt.subplot()
    minor_y_ticks = np.arange(0, 4000, 100)
    major_y_ticks = np.arange(0, 4000, 200)
    axis.set_yticks(major_y_ticks)
    axis.set_yticks(minor_y_ticks, minor=True)
    axis.set_ylabel("Estimated cost of plan in a year")
    axis.set_xticks(range(len(x_axis)), labels=x_axis)
    axis.set_xticklabels(x_axis, rotation=25, ha="right")
    axis.set_xlabel("Power Plans")
    axis.grid(True, "both", "y")
    axis.grid(which="minor", alpha=0.3)
    axis.bar(x_axis, y_axis)
    plt.subplots_adjust(bottom=0.2)
    plt.show()


if __name__ == "__main__":
    main()
