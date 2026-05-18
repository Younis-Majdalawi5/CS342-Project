# graphics.py
import math
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QPen, QBrush, QFont, QPainterPath
from PyQt5.QtCore import QRectF, QPointF, Qt


class StateItem(QGraphicsItem):
    """
    Custom QGraphicsItem representing a visual node (State) in the automaton.
    Handles its own rendering, positioning, and mouse interactions on the canvas.
    """

    def __init__(self, name, x, y, click_callback=None, width=70, height=50):
        super().__init__()
        self.setPos(x, y)
        self.name = name
        self.width = width
        self.height = height
        self.click_callback = click_callback

        # Enable dragging, dropping, and selecting the state on the canvas
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        # State properties
        self.is_accept = False
        self.is_start = False
        self.transitions = {}

    def mousePressEvent(self, event):
        """
        Intercepts mouse click events on the state.
        Triggers the callback function to update the selected state in the main UI.
        """
        if self.click_callback:
            self.click_callback(self)
        super().mousePressEvent(event)

    def boundingRect(self):
        """
        Defines the outer bounding box of the item.
        Required by PyQt5 to know the area that needs to be redrawn or updated.
        """
        margin = 5
        return QRectF(
            -self.width / 2 - margin,
            -self.height / 2 - margin,
            self.width + 2 * margin,
            self.height + 2 * margin
        )

    def paint(self, painter, option, widget=None):
        """
        Handles the actual drawing of the state (colors, borders, and text).
        Visual cues: Green = Start, Cyan = Accept, Dark Cyan = Both.
        """
        rect = QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

        # Determine fill color based on state type
        if self.is_start and self.is_accept:
            brush = QBrush(Qt.darkCyan)
        elif self.is_start:
            brush = QBrush(Qt.green)
        elif self.is_accept:
            brush = QBrush(Qt.cyan)
        else:
            brush = QBrush(Qt.white)

        # Draw the main rounded rectangle
        painter.setBrush(brush)
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRoundedRect(rect, 15, 15)

        # Draw an inner dotted line if it is an Accept state (Standard Automata notation)
        if self.is_accept:
            painter.setPen(QPen(Qt.black, 2, Qt.DotLine))
            inner_rect = rect.adjusted(6, 6, -6, -6)
            painter.drawRoundedRect(inner_rect, 15, 15)

        # Render the state's name in the center
        painter.setFont(QFont("Segoe UI", 12))
        painter.setPen(Qt.black)
        painter.drawText(rect, Qt.AlignCenter, self.name)

    def set_start(self, value=True):
        """Toggles the start state property and forces a visual update."""
        self.is_start = value
        self.update()

    def set_accept(self, value=True):
        """Toggles the accept state property and forces a visual update."""
        self.is_accept = value
        self.update()

    def shape(self):
        """
        Defines the exact collision shape for the item.
        Ensures mouse clicks are only registered inside the rounded rectangle.
        """
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(-self.width / 2, -self.height / 2, self.width, self.height),
            15,
            15
        )
        return path

    def get_border_point_towards(self, target_point):
        """
        Calculates the exact point on the state's perimeter that points towards a target coordinate.
        Uses trigonometry to ensure arrows connect nicely to the border, not the center of the shape.
        """
        center = self.scenePos()
        dx = target_point.x() - center.x()
        dy = target_point.y() - center.y()

        # If points are identical, return the center to avoid division by zero
        if dx == 0 and dy == 0:
            return center

        # Calculate the angle to the target point
        angle = math.atan2(dy, dx)
        w = self.width / 2
        h = self.height / 2

        # Calculate intersection with the ellipse/rectangle boundary
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        denom = math.sqrt((cos_a ** 2) / (w ** 2) + (sin_a ** 2) / (h ** 2))

        return QPointF(center.x() + cos_a / denom, center.y() + sin_a / denom)