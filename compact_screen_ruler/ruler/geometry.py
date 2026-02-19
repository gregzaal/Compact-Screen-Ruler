"""Geometry and hit-testing logic for the ruler widget."""

from PyQt6 import QtCore, QtGui

from ..constants import SCREEN_EDGE_SNAP_DISTANCE


class RulerGeometryMixin:
    """Provide geometry helpers used by rendering and interactions."""

    def getResolutionTextRect(self, draw_rect, alignment, text):
        metrics = QtGui.QFontMetrics(self.font())
        flags = int(alignment) | int(QtCore.Qt.TextFlag.TextSingleLine)
        return metrics.boundingRect(draw_rect, flags, text)

    def getResizeHitZones(self, local_x, local_y):
        grab_size = self.GRAB_HANDLE_SIZE
        width = self.width()
        height = self.height()

        return {
            "left": local_x < grab_size,
            "right": local_x > width - grab_size,
            "top": local_y < grab_size,
            "bottom": local_y > height - grab_size,
        }

    def getResizeCursorShape(self, hover_zones):
        on_left = hover_zones["left"]
        on_right = hover_zones["right"]
        on_top = hover_zones["top"]
        on_bottom = hover_zones["bottom"]

        if (on_left and on_top) or (on_right and on_bottom):
            return QtCore.Qt.CursorShape.SizeFDiagCursor
        if (on_right and on_top) or (on_left and on_bottom):
            return QtCore.Qt.CursorShape.SizeBDiagCursor
        if on_left or on_right:
            return QtCore.Qt.CursorShape.SizeHorCursor
        if on_top or on_bottom:
            return QtCore.Qt.CursorShape.SizeVerCursor
        return QtCore.Qt.CursorShape.OpenHandCursor

    def getScreenGeometryForRect(self, x_pos, y_pos, width, height):
        center_point = QtCore.QPoint(int(x_pos + width / 2), int(y_pos + height / 2))
        screen = QtGui.QGuiApplication.screenAt(center_point)
        if not screen:
            screen = QtGui.QGuiApplication.primaryScreen()
        return screen.availableGeometry() if screen else QtCore.QRect()

    def snapPositionToScreenEdges(self, x_pos, y_pos, width, height):
        screen_rect = self.getScreenGeometryForRect(x_pos, y_pos, width, height)
        if screen_rect.isNull():
            return x_pos, y_pos

        snap_distance = SCREEN_EDGE_SNAP_DISTANCE
        left_edge = screen_rect.x()
        top_edge = screen_rect.y()
        right_edge = left_edge + screen_rect.width()
        bottom_edge = top_edge + screen_rect.height()

        x_candidates = [(abs(x_pos - left_edge), left_edge), (abs((x_pos + width) - right_edge), right_edge - width)]
        y_candidates = [(abs(y_pos - top_edge), top_edge), (abs((y_pos + height) - bottom_edge), bottom_edge - height)]

        x_distance, snapped_x = min(x_candidates, key=lambda item: item[0])
        y_distance, snapped_y = min(y_candidates, key=lambda item: item[0])

        if x_distance <= snap_distance:
            x_pos = snapped_x
        if y_distance <= snap_distance:
            y_pos = snapped_y

        return x_pos, y_pos

    def snapResizeGeometryToScreenEdges(self, x_pos, y_pos, width, height, on_left, on_right, on_top, on_bottom):
        screen_rect = self.getScreenGeometryForRect(x_pos, y_pos, width, height)
        if screen_rect.isNull():
            return x_pos, y_pos, width, height

        snap_distance = SCREEN_EDGE_SNAP_DISTANCE
        left_edge = screen_rect.x()
        top_edge = screen_rect.y()
        right_edge = left_edge + screen_rect.width()
        bottom_edge = top_edge + screen_rect.height()

        right_side = x_pos + width
        bottom_side = y_pos + height

        if on_left and abs(x_pos - left_edge) <= snap_distance:
            x_pos = left_edge
            width = max(self.MIN_WINDOW_SIZE, right_side - x_pos)
            right_side = x_pos + width
        if on_right and abs(right_side - right_edge) <= snap_distance:
            width = max(self.MIN_WINDOW_SIZE, right_edge - x_pos)
            right_side = x_pos + width

        if on_top and abs(y_pos - top_edge) <= snap_distance:
            y_pos = top_edge
            height = max(self.MIN_WINDOW_SIZE, bottom_side - y_pos)
            bottom_side = y_pos + height
        if on_bottom and abs(bottom_side - bottom_edge) <= snap_distance:
            height = max(self.MIN_WINDOW_SIZE, bottom_edge - y_pos)

        return x_pos, y_pos, width, height

    def getScreenEdgeAlignment(self):
        x_pos = self.pos().x()
        y_pos = self.pos().y()
        width = self.width()
        height = self.height()
        screen_rect = self.getScreenGeometryForRect(x_pos, y_pos, width, height)
        if screen_rect.isNull():
            return {"left": False, "right": False, "top": False, "bottom": False}

        left_edge = screen_rect.x()
        top_edge = screen_rect.y()
        right_edge = left_edge + screen_rect.width()
        bottom_edge = top_edge + screen_rect.height()

        return {
            "left": x_pos == left_edge,
            "right": x_pos + width == right_edge,
            "top": y_pos == top_edge,
            "bottom": y_pos + height == bottom_edge,
        }
