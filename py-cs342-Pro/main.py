# main.py
import sys
import json
import math

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem,
    QVBoxLayout, QPushButton, QHBoxLayout, QInputDialog, QFileDialog,
    QMessageBox, QWidget, QGraphicsLineItem, QComboBox, QLabel,
    QTextEdit, QDialog, QDialogButtonBox
)
from PyQt5.QtGui import QPen, QBrush, QFont, QPolygonF
from PyQt5.QtCore import QPointF, Qt

# Importing custom models and engines
from model import Automaton, EPSILON
from regex_engine import RegexToNFA
from graphics import StateItem


class AutomataWindow(QMainWindow):
    """
    Main GUI Window for the Automata Simulator.
    Handles the user interface, canvas drawing, and interactions with the underlying Automaton model.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CS342 - Automata Simulator & Regex to NFA")
        self.setGeometry(100, 100, 1100, 750)

        # Initialize the core logic model (Default is DFA)
        self.automaton = Automaton(is_dfa=True)
        self.selected_state = None  # Tracks the currently clicked state on the canvas

        # Setup the graphics scene and view for drawing
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.init_ui()

    def init_ui(self):
        """
        Initializes the User Interface layout, buttons, and dropdown menus.
        Connects GUI events to their respective handler functions.
        """
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        btn_layout = QHBoxLayout()

        # Dropdown to toggle between DFA and NFA modes
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["DFA", "NFA"])
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        top_layout.addWidget(QLabel("Mode:"))
        top_layout.addWidget(self.mode_combo)
        top_layout.addStretch()

        # Dictionary of button labels and their corresponding methods
        buttons = {
            "Add State": self.add_state,
            "Set Start": self.set_start_state,
            "Set Accept": self.set_accept_state,
            "Add Transition": self.add_transition,
            "Validate": self.validate_design,
            "Simulate": self.simulate_input,
            "Regex → NFA": self.regex_to_nfa,
            "Generate Language": self.generate_language,
            "Clear": self.clear_all,
        }

        # Dynamically create and style buttons
        for label, func in buttons.items():
            btn = QPushButton(label)
            btn.setFont(QFont("Segoe UI", 9))
            btn.setStyleSheet("""
                QPushButton { background-color: #5A9BD5; color: white; border-radius: 6px; padding: 7px 10px; }
                QPushButton:hover { background-color: #4178BE; }
                QPushButton:pressed { background-color: #2A5D9F; }
            """)
            btn.clicked.connect(func)
            btn_layout.addWidget(btn)

        layout.addLayout(top_layout)
        layout.addWidget(self.view)
        layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def change_mode(self, mode):
        """Updates the automaton ruleset based on the selected mode (DFA/NFA)."""
        self.automaton.is_dfa = (mode == "DFA")

    def clear_all(self):
        """Clears the canvas and resets the underlying automaton model."""
        self.scene.clear()
        self.automaton = Automaton(is_dfa=(self.mode_combo.currentText() == "DFA"))
        self.selected_state = None

    def add_state(self):
        """Prompts the user for a state name, creates a graphical item, and adds it to the model."""
        name, ok = QInputDialog.getText(self, "State Name", "Enter state name:")
        if ok and name:
            if name in self.automaton.states:
                QMessageBox.warning(self, "Error", f"State '{name}' already exists.")
                return

            # Calculate dynamic initial position based on the number of existing states
            x = len(self.automaton.states) * 110 + 80
            y = 170

            # Create a new graphical state item and bind the click event
            state = StateItem(name, x, y, click_callback=self.on_state_clicked)
            self.scene.addItem(state)
            self.automaton.add_state(state)

    def on_state_clicked(self, state):
        """Callback function triggered when a state item is clicked on the canvas."""
        self.selected_state = state

    def set_start_state(self):
        """Marks the currently selected state as the Start state."""
        if not self.selected_state:
            QMessageBox.warning(self, "Error", "Select a state first.")
            return
        self.automaton.set_start(self.selected_state)

    def set_accept_state(self):
        """Marks the currently selected state as an Accept (Final) state."""
        if not self.selected_state:
            QMessageBox.warning(self, "Error", "Select a state first.")
            return
        self.automaton.set_accept(self.selected_state)

    def add_transition(self):
        """
        Prompts the user for destination and transition symbol.
        Handles Epsilon (ε) conversion and draws the visual arrow.
        """
        if not self.selected_state:
            QMessageBox.warning(self, "Error", "Select the source state first.")
            return

        from_state = self.selected_state
        to_name, ok = QInputDialog.getText(self, "Destination", "Enter destination state name:")
        if not ok or not to_name: return

        symbol, ok2 = QInputDialog.getText(self, "Symbol", "Enter symbol (use 'eps' or 'epsilon' for ε):")
        if not ok2 or not symbol: return

        to_state = self.automaton.states.get(to_name)
        if not to_state:
            QMessageBox.warning(self, "Error", f"State '{to_name}' does not exist.")
            return

        try:
            # Update the core model
            self.automaton.add_transition(from_state, symbol, to_state)

            # Draw the graphical arrow. Convert 'eps'/'epsilon' to visual 'ε'
            display_symbol = EPSILON if symbol.lower() in ["epsilon", "eps"] else symbol
            self.draw_arrow(from_state, to_state, display_symbol)
        except Exception as e:
            QMessageBox.critical(self, "Transition Error", str(e))

    def validate_design(self):
        """Triggers the strict validation checks (Completeness, uniqueness, etc.) and shows the result."""
        errors = self.automaton.validate()
        if errors:
            QMessageBox.warning(self, "Validation Failed", "\n".join(errors))
        else:
            QMessageBox.information(self, "Success", "The automaton design is valid!")

    def simulate_input(self):
        """
        Validates the design, then runs the string simulation (DFA or NFA).
        Displays the acceptance status and the step-by-step trace.
        """
        errors = self.automaton.validate()
        if errors:
            QMessageBox.warning(self, "Cannot Simulate", "Fix design errors first:\n" + "\n".join(errors))
            return

        input_str, ok = QInputDialog.getText(self, "Simulate", "Enter input string:")
        if ok:
            accepted, trace = self.automaton.simulate(input_str)
            msg = "✅ ACCEPTED" if accepted else "❌ REJECTED"
            msg += "\n\n--- Trace Steps ---\n" + "\n".join(trace)
            QMessageBox.information(self, "Result", msg)

    def regex_to_nfa(self):
        """
        Takes a regular expression from the user, converts it to an NFA using
        Thompson's Construction, and redraws the layout automatically.
        """
        regex, ok = QInputDialog.getText(self, "Regex to NFA", "Enter Regex (e.g., (a|b)*abb):")
        if not ok or not regex: return

        try:
            converter = RegexToNFA()
            self.automaton = converter.build_from_regex(regex)
            self.automaton.is_dfa = False
            self.mode_combo.setCurrentText("NFA")
            self.redraw_automaton_from_model()
            QMessageBox.information(self, "Success", "Regex converted to NFA using Thompson's Construction.")
        except Exception as e:
            QMessageBox.critical(self, "Regex Error", str(e))

    def generate_language(self):
        """
        Generates all accepted strings up to a specified maximum length using BFS.
        Displays the result in a scrollable text dialog.
        """
        errors = self.automaton.validate()
        if errors:
            QMessageBox.warning(self, "Cannot Generate", "Fix design errors first.")
            return

        max_len, ok = QInputDialog.getInt(self, "Generate Language", "Max string length:", 3, 0, 10)
        if not ok: return

        strings = self.automaton.generate_language(max_len)
        result = "Accepted Strings:\n" + "\n".join(strings)

        # Show the generated language in a dedicated dialog window
        dialog = QDialog(self)
        dialog.setWindowTitle("Generated Language")
        dialog.resize(400, 300)
        layout = QVBoxLayout()
        edit = QTextEdit()
        edit.setReadOnly(True)
        edit.setText(result)
        layout.addWidget(edit)
        dialog.setLayout(layout)
        dialog.exec_()

    def redraw_automaton_from_model(self):
        """
        Clears the canvas and visually reconstructs the automaton based on the core model.
        Used primarily after automatic generation (like Regex to NFA).
        """
        self.scene.clear()

        # Add state items back to the graphical scene
        for name, state_obj in self.automaton.states.items():
            self.scene.addItem(state_obj)

        # Redraw all transitions/arrows
        for state in self.automaton.states.values():
            for symbol, targets in state.transitions.items():
                for target in targets:
                    if target in self.automaton.states:
                        self.draw_arrow(state, self.automaton.states[target], symbol)

    def draw_arrow(self, from_state, to_state, symbol):
        """
        Calculates mathematical coordinates and draws an arrow between two states.
        Handles standard transitions and self-loops.
        """
        # Handle self-loops (Arrow pointing back to the same state)
        if from_state.name == to_state.name:
            center = from_state.scenePos()
            text = QGraphicsTextItem(f"↻ {symbol}")
            text.setFont(QFont("Segoe UI", 11))
            text.setPos(center.x() - 15, center.y() - 65)
            self.scene.addItem(text)
            return

        # Calculate exact intersection points on the border of the state rectangles
        start = from_state.get_border_point_towards(to_state.scenePos())
        end = to_state.get_border_point_towards(from_state.scenePos())

        # Draw the main transition line
        line = QGraphicsLineItem(start.x(), start.y(), end.x(), end.y())
        line.setPen(QPen(Qt.black, 2))
        self.scene.addItem(line)

        # Calculate coordinates for the arrowhead polygon using trigonometry
        arrow_size = 10
        angle = math.atan2(end.y() - start.y(), end.x() - start.x())
        p1 = QPointF(end.x() - arrow_size * math.cos(angle - math.pi / 6),
                     end.y() - arrow_size * math.sin(angle - math.pi / 6))
        p2 = QPointF(end.x() - arrow_size * math.cos(angle + math.pi / 6),
                     end.y() - arrow_size * math.sin(angle + math.pi / 6))

        # Draw the arrowhead
        arrow_head = QPolygonF([end, p1, p2])
        self.scene.addPolygon(arrow_head, QPen(Qt.black), QBrush(Qt.black))

        # Add the transition symbol text near the middle of the line
        text = QGraphicsTextItem(symbol)
        text.setFont(QFont("Segoe UI", 11))
        text.setPos((start.x() + end.x()) / 2 + 5, (start.y() + end.y()) / 2 + 5)
        self.scene.addItem(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutomataWindow()
    window.show()
    sys.exit(app.exec_())