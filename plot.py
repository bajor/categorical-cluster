import matplotlib.pyplot as plt


def _read_file_and_plot_histogram(filename):
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
        values = [round(float(line.strip()), 2) for line in lines]
        plt.hist(values, bins=100, edgecolor="k", alpha=0.7)
        plt.title("Histogram of Values Rounded to 0.01")
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.show()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def plot_daily_extended():
    filname = "logs.csv"
    _read_file_and_plot_histogram(filname)