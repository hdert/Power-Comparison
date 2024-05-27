"""Plot usage data using matplotlib."""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import statistics_generator
import default_values


def main():
    """Plot usage data."""
    usage_data = statistics_generator.get_analysis(default_values.analysis_file_path)
    usage_data = np.average(usage_data, axis=0)
    x_axis = [i for i in range(24)]
    axes = plt.subplot()
    axes.set_xticks(x_axis)
    axes.set_title("Average Power Usage Per Hour")
    axes.set_xlabel("Hour of Day")
    axes.set_ylabel("Power Usage in KWh")
    axes.grid(True, "both", "y")
    plt.bar(x_axis, usage_data)
    plt.show()


if __name__ == "__main__":
    main()
