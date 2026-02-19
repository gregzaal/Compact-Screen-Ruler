"""Resolution text and measurement overlay helpers for ruler rendering."""

from PyQt6 import QtCore


class RulerRenderingTextMixin:
    """Provide readout text and pick-mode overlay drawing."""

    def resetResolutionTextState(self):
        self.resolution_text_rect = QtCore.QRect()
        self.resolution_text_click_enabled = False

    def getMeasurementSize(self, painter):
        size_x = self.width()
        size_y = self.height()

        if self.drawPickPos:
            mouse_xpos = self.mouse_x - self.pos().x()
            mouse_ypos = self.mouse_y - self.pos().y()
            size_x = mouse_xpos
            size_y = mouse_ypos
            if self.height() > 80 and self.width() >= 88:
                painter.drawLine(mouse_xpos, 0, mouse_xpos, self.height())
                painter.drawLine(0, mouse_ypos, self.width(), mouse_ypos)
            elif self.width() >= 88:
                painter.drawLine(mouse_xpos, 0, mouse_xpos, self.height())
            else:
                painter.drawLine(0, mouse_ypos, self.width(), mouse_ypos)

        return size_x, size_y

    def drawResolutionReadout(self, painter, size_x, size_y, color_value):
        if self.height() > 80 and self.width() >= 88:
            resolution_text = self.buildResolutionText(size_x, size_y, include_y=True)
            resolution_draw_rect = QtCore.QRect(0, 0, self.width(), self.height())
            resolution_alignment = QtCore.Qt.AlignmentFlag.AlignCenter
            self.resolution_text_rect = self.getResolutionTextRect(
                resolution_draw_rect, resolution_alignment, resolution_text
            )
            self.resolution_text_click_enabled = True
            self.drawResolutionText(painter, resolution_draw_rect, resolution_alignment, resolution_text)
            self.drawStatusMessages(painter, color_value)
        elif self.height() > 80 and self.width() < 88:
            resolution_text = f"{self.formatMeasurementValue(size_y, 'y')} {self.measurement_unit}"
            resolution_draw_rect = QtCore.QRect(0, self.height() - 37, self.width(), 20)
            resolution_alignment = QtCore.Qt.AlignmentFlag.AlignCenter
            self.resolution_text_rect = self.getResolutionTextRect(
                resolution_draw_rect, resolution_alignment, resolution_text
            )
            self.drawResolutionText(painter, resolution_draw_rect, resolution_alignment, resolution_text)
        else:
            resolution_text = self.buildResolutionText(size_x, size_y, include_y=False)
            if self.height() < 54:
                resolution_draw_rect = QtCore.QRect(0, 19, self.width() - 3, 15)
            else:
                resolution_draw_rect = QtCore.QRect(0, 0, self.width() - 3, self.height())
            resolution_alignment = QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
            self.resolution_text_rect = self.getResolutionTextRect(
                resolution_draw_rect, resolution_alignment, resolution_text
            )
            self.drawResolutionText(painter, resolution_draw_rect, resolution_alignment, resolution_text)
