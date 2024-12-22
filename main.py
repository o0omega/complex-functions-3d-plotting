import sys
import numpy as np
import plotly.graph_objects as go
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QLineEdit, QPushButton, QHBoxLayout, QGridLayout, QLabel, QSpacerItem, QSizePolicy, QSplitter, QScrollArea, QCheckBox, QButtonGroup, QComboBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl
import tempfile
from scipy.special import gamma  # Import Gamma function

class PlotlyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Complex Function 3D-Plot With Colormap Visualization")

        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)
        splitter.setStyleSheet("QSplitter::handle { background: #5b5b5b; border: 1px solid #555; }")

        # Left side for update button, function inputs and options 
        left_layout = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        self.create_widgets(left_layout)

        # Right side for the graphs (using QWebEngineView for each graph)
        right_layout = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        grid_layout_graphs = QGridLayout()
        grid_layout_graphs.setSpacing(0)
        grid_layout_graphs.setContentsMargins(0, 0, 0, 0)

        self.view = QWebEngineView()
        grid_layout_graphs.addWidget(self.view, 0, 0)

        self.imaginary_part_view = QWebEngineView()
        grid_layout_graphs.addWidget(self.imaginary_part_view, 0, 1)

        self.real_part_view = QWebEngineView()
        grid_layout_graphs.addWidget(self.real_part_view, 1, 0)

        self.real_function_view = QWebEngineView()
        grid_layout_graphs.addWidget(self.real_function_view, 1, 1)

        right_layout.addLayout(grid_layout_graphs)

        # Add widgets to the splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        layout.addWidget(splitter)

        self.setCentralWidget(central_widget)
        self.create_plot()  # Call create_plot without the function initially

        splitter.setSizes([138, 1800])
        splitter.setStretchFactor(1, 15)

        left_widget.setMinimumWidth(138)
        left_widget.setMaximumWidth(300)

        right_widget.setMinimumWidth(240)
        right_widget.setMaximumWidth(1800)

        splitter.setHandleWidth(3)

        # Initialize input fields list
        self.input_fields = [self.function_input]

    def create_widgets(self, left_layout):
        # Update button widget
        update_button_widget = QWidget()
        update_button_layout = QVBoxLayout()
        update_button_widget.setLayout(update_button_layout)

        # New input field for the Z function
        z_layout = QGridLayout()
        self.z_function_input = QLineEdit(self)
        self.z_function_input.setPlaceholderText("x+i*y")
        self.z_function_label = QLabel("z =", self)

        z_layout.addWidget(self.z_function_label, 0, 0)
        z_layout.addWidget(self.z_function_input, 0, 1)

        # Add the z_layout to the parent layout (update_button_layout)
        update_button_layout.addLayout(z_layout)


        update_button = QPushButton("Update Function", self)
        update_button.clicked.connect(self.update_plot)
        update_button.setFixedWidth(120)
        update_button_layout.addWidget(update_button)

        # Function input field with the + and - buttons widget
        input_widget = QWidget()
        input_layout = QVBoxLayout()
        input_widget.setLayout(input_layout)

        # Create a horizontal layout for + and - buttons
        button_layout = QGridLayout()
        self.add_button = QPushButton("+", self)
        self.add_button.clicked.connect(self.add_input_field)
        button_layout.addWidget(self.add_button, 0, 0)

        self.remove_button = QPushButton("-", self)
        self.remove_button.clicked.connect(self.remove_input_field)
        button_layout.addWidget(self.remove_button, 0, 1)

        # Initially hide the - button
        self.remove_button.setVisible(False)

        input_layout.addLayout(button_layout)

        self.function_input = QLineEdit(self)
        self.function_input.setPlaceholderText("Input...")
        input_layout.addWidget(self.function_input)

        # Create a QScrollArea to make input field section scrollable
        scroll_area = QScrollArea(self)
        scroll_area.setWidget(input_widget)
        scroll_area.setWidgetResizable(True)  # Allow the widget inside to resize as needed

        # Set the vertical scrollbar to appear only when needed
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Styling for the scroll area and scrollbar (already implemented correctly)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: #1e1e1e;  /* Ensure scroll area has the same background as the app */
                border: none;  /* Remove any border around the scroll area */
            }

            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;  /* Dark gray background to match app */
                width: 12px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical {
                background: #666666;  /* Lighter gray for the handle */
                border-radius: 6px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background: #4d4d4d;  /* Slightly darker on hover */
            }

            QScrollBar::add-line:vertical {
                background: none;
                height: 0px;
            }

            QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }

            QScrollBar:horizontal {
                border: none;
                background: #1e1e1e;  /* Dark gray background to match app */
                height: 12px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:horizontal {
                background: #666666;  /* Lighter gray for the handle */
                border-radius: 6px;
                min-width: 20px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #4d4d4d;  /* Slightly darker on hover */
            }

            QScrollBar::add-line:horizontal {
                background: none;
                width: 0px;
            }

            QScrollBar::sub-line:horizontal {
                background: none;
                width: 0px;
            }

            QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                background: none;
            }

            /* Additional styling for the scroll track background */
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: #1e1e1e;  /* This changes the area where the scrollbar moves */
            }
        """)

        # Options widget
        options_widget = QWidget()
        options_layout = QVBoxLayout()
        options_widget.setLayout(options_layout)

        # Create grid layout for options
        grid_layout = QGridLayout()
        grid_options = QGridLayout()

        # Options label spanning the entire first row
        options_label = QLabel("Options")
        options_label.setAlignment(Qt.AlignCenter)
        options_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        grid_options.addWidget(options_label, 0, 0, 1, 3)

        # Create a QComboBox for colorscale selection
        self.colormap = QComboBox(self)
        
        # Add colorscale options to the combo box
        colormaps = [
            "Viridis", "Cividis", "Plasma", "Inferno", "Magma", "Rainbow", "Jet", 
            "Blues", "Greens", "Greys", "Oranges", "Purples", "Reds", "YlGn", 
            "YlGnBu", "GnBu", "BuGn", "BuPu", "RdPu", "PurRd", "Blues", 
            "YlOrBr", "YlOrRd", "OrRd", "PuBuGn", "PuBu", "GnBu", "RdYlBu", 
            "RdGy", "RdYlGn", "Spectral", "RdYlBu", "RdGy", "PiYG", "PRGn", 
            "PuOr", "RdBu", "RdGy", "RdYlGn", "Spectral", "Twilight"]

        for cmap in colormaps:
            self.colormap.addItem(cmap)

        # X, Y, Z labels and inputs
        x_label = QLabel("X:", self)
        y_label = QLabel("Y:", self)
        z_label = QLabel("Z:", self)

        self.x_min_input = QLineEdit(self)
        self.x_min_input.setPlaceholderText("Min")
        self.x_max_input = QLineEdit(self)
        self.x_max_input.setPlaceholderText("Max")

        self.y_min_input = QLineEdit(self)
        self.y_min_input.setPlaceholderText("Min")
        self.y_max_input = QLineEdit(self)
        self.y_max_input.setPlaceholderText("Max")

        self.z_min_input = QLineEdit(self)
        self.z_min_input.setPlaceholderText("Min")
        self.z_max_input = QLineEdit(self)
        self.z_max_input.setPlaceholderText("Max")

        grid_layout.addWidget(x_label, 1, 0)
        grid_layout.addWidget(self.x_min_input, 1, 1)
        grid_layout.addWidget(self.x_max_input, 1, 2)

        grid_layout.addWidget(y_label, 2, 0)
        grid_layout.addWidget(self.y_min_input, 2, 1)
        grid_layout.addWidget(self.y_max_input, 2, 2)

        grid_layout.addWidget(z_label, 3, 0)
        grid_layout.addWidget(self.z_min_input, 3, 1)
        grid_layout.addWidget(self.z_max_input, 3, 2)

        # Add the grid layout for options to options_layout
        options_layout.addLayout(grid_options)
        options_layout.addWidget(self.colormap)
        options_layout.addLayout(grid_layout)

        # Add the widgets in the correct order
        left_layout.addWidget(update_button_widget)
        left_layout.addWidget(scroll_area)  # Add the scrollable area for inputs
        left_layout.addWidget(options_widget)

        # Keep track of input fields (so we can add them dynamically)
        self.input_layout = input_layout  # Store the layout here
        self.input_fields = [self.function_input]  # Store the initial input field

        # Add spacer to align inputs to the top of the scroll area
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        input_layout.addItem(self.spacer)

    def add_input_field(self):
        # Create a new input field
        new_input_field = QLineEdit(self)
        new_input_field.setPlaceholderText("Input...")

        # Insert the new input field into the layout (directly below the first one)
        self.input_layout.insertWidget(len(self.input_fields)+1, new_input_field)

        # Append the new input field to the list
        self.input_fields.append(new_input_field)

        # Show the remove button if there's more than one input field
        if len(self.input_fields) > 1:
            self.remove_button.setVisible(True)

    def remove_input_field(self):
        # Only remove input field if there are more than 1 input field
        if len(self.input_fields) > 1:
            last_input_field = self.input_fields.pop()
            last_input_field.deleteLater()

            # Hide the remove button if there is only 1 input field left
            if len(self.input_fields) == 1:
                self.remove_button.setVisible(False)

    def create_plot(self):
        # Prepare the layout settings
        layout_settings = dict(
            plot_bgcolor='#121212',
            paper_bgcolor='#121212',
            font=dict(color='#e0e0e0')
        )

        # Get the user input for the Z function (defaulting to "X + 1j * Y" if empty)
        z_function = self.z_function_input.text().strip()
        if not z_function:
            z_function = "X + 1j * Y"  # Default value if the input is empty

        # Replace 'i' with '1j' and lowercase x/y to uppercase X/Y in the input expression
        z_function = z_function.replace('i', '1j')
        z_function = z_function.replace('x', 'X').replace('y', 'Y')  # Convert lowercase to uppercase

        # Initialize the figures for the different parts (real, imaginary, magnitude)
        fig_real_part = go.Figure()
        fig_imaginary_part = go.Figure()
        fig_3d = go.Figure()
        fig_real = go.Figure()

        # Loop through the input fields and generate traces for each function
        for idx, field in enumerate(self.input_fields):
            func_expr = field.text()
            func_expr = func_expr.replace('i', '1j')
            func_expr = func_expr.replace('x', 'X').replace('y', 'Y')  # Convert lowercase to uppercase

            if not any(var in func_expr for var in ['z', '1j']):
                func_expr = f"({func_expr}) + 0*z"

            safe_locals = {
                'np': np,
                'sin': np.sin,
                'cos': np.cos,
                'tan': np.tan,
                'cot': lambda x: 1 / np.tan(x),
                'sqrt': np.sqrt,
                'log': np.log,
                'exp': np.exp,
                'abs': np.abs,
                'arctan': np.arctan,
                'arccot': lambda x: np.pi / 2 - np.arctan(x),
                'arccos': np.arccos,
                'arcsin': np.arcsin,
                'angle': np.angle,
                'vstack': np.vstack,
                'hstack': np.hstack,
                'dstack': np.dstack,
                'column_stack': np.column_stack,
                'transpose': np.transpose,
                'gamma': gamma
            }

            def f(z):
                # Dynamically evaluate Z function based on the input expression
                z_expr = z_function.replace('X', 'z.real').replace('Y', 'z.imag')
                # Print for debugging to see the evaluated Z expression
                print(f"Evaluating Z function: {z_expr}")
                z_value = eval(z_expr, {"__builtins__": None}, {'z': z, 'X': z.real, 'Y': z.imag})
                return eval(func_expr, {"__builtins__": None}, {**safe_locals, 'z': z_value, 'X': z_value.real, 'Y': z_value.imag})

            try:
                x_min = float(self.x_min_input.text()) if self.x_min_input.text() else -2
                x_max = float(self.x_max_input.text()) if self.x_max_input.text() else 2
                y_min = float(self.y_min_input.text()) if self.y_min_input.text() else -2
                y_max = float(self.y_max_input.text()) if self.y_max_input.text() else 2
                z_min = float(self.z_min_input.text()) if self.z_min_input.text() else -5
                z_max = float(self.z_max_input.text()) if self.z_max_input.text() else 5

                x = np.linspace(x_min, x_max, 200)
                y = np.linspace(y_min, y_max, 200)
                X, Y = np.meshgrid(x, y)
                
                # Dynamically generate Z based on user input
                Z = eval(z_function.replace('X', 'X').replace('Y', 'Y'))
                
                print(f"Calculated Z: {Z}")  # Debug print to check Z

                F = f(Z)
            except Exception as e:
                return e

            magnitude = np.abs(F)
            phase = np.angle(F) / np.pi

            self.colorscale = self.colormap.currentText()

            colorscale_settings = dict(
                colorscale=self.colorscale,
                colorbar=dict(
                    title="Phase (π units)",
                    tickvals=[-1, -0.5, 0, 0.5, 1],
                    ticktext=["-π", "-π/2", "0", "π/2", "π"],
                    tickmode="array"
                )
            )

            # Real part trace
            fig_real_part.add_trace(go.Surface(
                z=np.real(F), x=X, y=Y, surfacecolor=phase, **colorscale_settings
            ))

            # Imaginary part trace
            fig_imaginary_part.add_trace(go.Surface(
                z=np.imag(F), x=X, y=Y, surfacecolor=phase, **colorscale_settings
            ))

            # Magnitude part trace
            fig_3d.add_trace(go.Surface(
                z=magnitude, x=X, y=Y, surfacecolor=phase, **colorscale_settings
            ))

            # Real part of the function trace
            real_z = np.linspace(x_min, x_max, 200)
            F_real = f(real_z)
            fig_real.add_trace(go.Scatter(x=real_z, y=np.real(F_real), mode='lines', line=dict(color='blue')))

        # Apply Z-axis limits to each plot
        z_axis_limits = dict(range=[z_min, z_max])

        fig_real_part.update_layout(
            title="Real Part of f(z)",
            scene=dict(
                xaxis_title="Re(z)",
                yaxis_title="Im(z)",
                zaxis_title="Re(f(z))",
                zaxis=z_axis_limits
            ),
            **layout_settings
        )

        fig_imaginary_part.update_layout(
            title="Imaginary Part of f(z)",
            scene=dict(
                xaxis_title="Re(z)",
                yaxis_title="Im(z)",
                zaxis_title="Im(f(z))",
                zaxis=z_axis_limits
            ),
            **layout_settings
        )

        fig_3d.update_layout(
            title="Magnitude of f(z)",
            scene=dict(
                xaxis_title="Re(z)",
                yaxis_title="Im(z)",
                zaxis_title="|f(z)|",
                zaxis=dict(range=[0, z_max])  # Ensures the Z-axis starts at 0
            ),
            **layout_settings
        )

        fig_real.update_layout(
            title="Real Function f(z)",
            scene=dict(
                xaxis_title="z",
                yaxis_title="f(z)",
            ),
            **layout_settings
        )

        # Save and display plots
        temp_file_real_part = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        fig_real_part.write_html(temp_file_real_part.name)
        self.real_part_view.load(QUrl.fromLocalFile(temp_file_real_part.name))

        temp_file_imaginary_part = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        fig_imaginary_part.write_html(temp_file_imaginary_part.name)
        self.imaginary_part_view.load(QUrl.fromLocalFile(temp_file_imaginary_part.name))

        temp_file_3d = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        fig_3d.write_html(temp_file_3d.name)
        self.view.load(QUrl.fromLocalFile(temp_file_3d.name))

        temp_file_real_func_2d = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        fig_real.write_html(temp_file_real_func_2d.name)
        self.real_function_view.load(QUrl.fromLocalFile(temp_file_real_func_2d.name))

    def update_plot(self):
        self.create_plot()  # Call create_plot to update the graphs


def set_dark_mode(app):
    dark_stylesheet = """
    QWidget {
        background-color: #121212;
        color: #e0e0e0;
        font-family: Arial;
        font-size: 10pt;
    }
    QLineEdit {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #555;
        border-radius: 5px;
        padding: 4px;
    }
    QPushButton {
        background-color: #2a2a2a;
        color: #e0e0e0;
        border: 1px solid #555;
        border-radius: 5px;
        padding: 4px;
    }
    QPushButton:hover {
        background-color: #3e3e3e;
    }
    QPushButton:pressed {
        background-color: #555555;
    }
    QLabel {
        color: #e0e0e0;
    }
    QWebEngineView {
        border: 1px solid #555;
    }
    """
    app.setStyleSheet(dark_stylesheet)

app = QApplication(sys.argv)
set_dark_mode(app)
main_window = PlotlyApp()
main_window.showMaximized()
sys.exit(app.exec_())
