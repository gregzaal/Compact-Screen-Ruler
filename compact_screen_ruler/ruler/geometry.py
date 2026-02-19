"""Geometry and hit-testing logic for the ruler widget."""

from PyQt6 import QtCore, QtGui

from ..constants import SCREEN_EDGE_SNAP_DISTANCE


class RulerGeometryMixin:
    """Provide geometry helpers used by rendering and interactions."""

    def getPixelsPerInch(self, axis):
        screen = self.getCenterScreen()
        if not screen:
            return 0.0

        axis_name = str(axis).lower()
        if axis_name == "y":
            pixels_per_inch = float(screen.physicalDotsPerInchY())
        else:
            pixels_per_inch = float(screen.physicalDotsPerInchX())

        if pixels_per_inch <= 0:
            if axis_name == "y":
                pixels_per_inch = float(screen.logicalDotsPerInchY())
            else:
                pixels_per_inch = float(screen.logicalDotsPerInchX())

        if pixels_per_inch <= 0:
            return 0.0

        scale_factor = float(screen.devicePixelRatio())
        if scale_factor <= 0:
            scale_factor = 1.0

        return pixels_per_inch / scale_factor

    def getCenterScreen(self, x_pos=None, y_pos=None, width=None, height=None):
        if x_pos is None or y_pos is None or width is None or height is None:
            frame = self.frameGeometry()
            center_point = frame.center()
        else:
            center_point = QtCore.QPoint(int(x_pos + width / 2), int(y_pos + height / 2))

        screen = QtGui.QGuiApplication.screenAt(center_point)
        if not screen:
            screen = QtGui.QGuiApplication.primaryScreen()
        return screen

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
        screen = self.getCenterScreen(x_pos, y_pos, width, height)
        return screen.availableGeometry() if screen else QtCore.QRect()

    def convertPixelsToUnit(self, value_px, axis, unit):
        if unit == "px":
            return float(value_px)

        pixels_per_inch = self.getPixelsPerInch(axis)
        if pixels_per_inch <= 0:
            return float(value_px)

        inches = float(value_px) / pixels_per_inch
        if unit == "cm":
            return inches * 2.54
        if unit == "in":
            return inches
        return float(value_px)

    def convertUnitToPixels(self, value, axis, unit):
        if unit == "px":
            return float(value)

        pixels_per_inch = self.getPixelsPerInch(axis)
        if pixels_per_inch <= 0:
            return float(value)

        unit_name = str(unit).lower()
        if unit_name == "cm":
            inches = float(value) / 2.54
        elif unit_name == "in":
            inches = float(value)
        else:
            return float(value)

        return inches * pixels_per_inch

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
