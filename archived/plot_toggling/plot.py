from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk



class WeatherPlotViewer:
    def __init__(self, root, weather_df):
        """
        Initialize the WeatherPlotViewer with the root Tk window and the weather DataFrame.
        """
        self.root = root
        self.weather_df = weather_df
        self.current_plot_index = 0

        # List of plot functions
        self.plots = [
            self.plot_temperature_trends,
            self.plot_daily_range
        ]

        # Create the figure for matplotlib plots
        self.figure, self.ax = plt.subplots(figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Create navigation buttons
        self.button_frame = ttk.Frame(root)
        self.button_frame.pack(fill=tk.X, pady=5)
        self.prev_button = ttk.Button(self.button_frame, text="Previous", command=self.show_previous_plot)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button = ttk.Button(self.button_frame, text="Next", command=self.show_next_plot)
        self.next_button.pack(side=tk.RIGHT, padx=5)

        # Show the first plot
        self.show_plot(self.current_plot_index)

    def show_plot(self, plot_index):
        """
        Display the plot at the specified index.
        """
        # Clear the current axes
        self.ax.clear()

        # Call the plot function
        self.plots[plot_index]()

        # Refresh the canvas
        self.canvas.draw()

    def show_next_plot(self):
        """
        Display the next plot in the list.
        """
        self.current_plot_index = (self.current_plot_index + 1) % len(self.plots)
        self.show_plot(self.current_plot_index)

    def show_previous_plot(self):
        """
        Display the previous plot in the list.
        """
        self.current_plot_index = (self.current_plot_index - 1) % len(self.plots)
        self.show_plot(self.current_plot_index)

    def plot_temperature_trends(self):
        """
        Plot max and min temperature trends over time.
        """
        self.ax.plot(self.weather_df['Date'], self.weather_df['TemperatureMax'], label="Max Temperature", color="red")
        self.ax.plot(self.weather_df['Date'], self.weather_df['TemperatureMin'], label="Min Temperature", color="blue")
        self.ax.set_title("Temperature Trends Over Time")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Temperature (\u00B0C)")
        self.ax.legend()
        self.ax.grid(True, linestyle='--', alpha=0.7)

    def plot_daily_range(self):
        """
        Plot the daily temperature range.
        """
        if 'DailyRange' not in self.weather_df:
            self.weather_df['DailyRange'] = self.weather_df['TemperatureMax'] - self.weather_df['TemperatureMin']

        self.ax.plot(self.weather_df['Date'], self.weather_df['DailyRange'], label="Daily Temperature Range", linestyle='-', marker='o')
        self.ax.set_title("Daily Temperature Range Over Time")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Temperature Range (\u00B0C)")
        self.ax.legend()
        self.ax.grid(True, linestyle='--', alpha=0.7)


def run_weather_plot_viewer(weather_df):
    """
    Launch the WeatherPlotViewer with the given DataFrame.
    """
    root = tk.Tk()
    root.title("Weather Plot Viewer")
    viewer = WeatherPlotViewer(root, weather_df)
    root.mainloop()
