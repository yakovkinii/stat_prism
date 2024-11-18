#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

import PySide6.QtWidgets
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget
from PySide6.QtCore import QTimer
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a button to generate, save, and display the plot
        self.button = QPushButton("Generate and Save Plot")
        self.button.clicked.connect(self.generate_and_display_plot)
        self.canvas = None  # Placeholder for displaying the plot as a widget

        # Set up the main layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.button)
        self.setCentralWidget(central_widget)

        # Set window title and dimensions
        self.setWindowTitle("Plot to SVG and Display After Delay")
        self.resize(600, 600)

    def create_figure(self):
        """Creates the Matplotlib figure and returns it."""
        fig, ax = plt.subplots()

        # Generate sample data for demonstration
        np.random.seed(0)
        data_scatter_x = np.random.rand(50) * 100  # x values for scatter
        data_scatter_y = np.random.rand(50) * 1  # y values for scatter
        data_box = [np.random.normal(size=100) for _ in range(5)]  # data for box plot

        # Create the scatter plot
        ax.scatter(data_scatter_x, data_scatter_y, color='blue', label="Scatter Data")

        # Create the box plot
        ax.boxplot(data_box, positions=[20, 40, 60, 80, 100], widths=5)

        # Configure the plot appearance
        ax.set_title("Scatter and Box Plot")
        ax.set_xlabel("X Axis Label")
        ax.set_ylabel("Y Axis Label")
        ax.legend()  # Add legend
        ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels

        # Adjust layout to prevent cropping
        fig.tight_layout()  # Auto-adjust layout
        fig.subplots_adjust(bottom=0.2)  # Additional padding if necessary

        return fig

    def save_figure_to_file(self, fig, filename="plot_output.svg"):
        """Saves the given figure to an SVG file."""
        fig.savefig(filename, format="svg", bbox_inches='tight')
        plt.close(fig)  # Close the figure to release memory
        print(f"Plot saved as {filename}")

    def add_figure_to_layout(self, fig):
        """Adds the given figure to the layout in a FigureCanvas widget."""
        # Remove existing canvas if it exists
        if self.canvas:
            self.canvas.setParent(None)

        # Display the plot in a FigureCanvas widget
        self.canvas = FigureCanvas(fig)
        self.centralWidget().layout().addWidget(self.canvas)
        print("Plot displayed in widget for verification.")

    def generate_and_display_plot(self):
        """Generates the plot, saves it to file, and then displays it after a delay."""
        # Create the figure
        fig = self.create_figure()

        # Save to file
        self.save_figure_to_file(fig)

        # Display the plot after a delay
        QTimer.singleShot(2000, lambda: self.add_figure_to_layout(self.create_figure()))


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
