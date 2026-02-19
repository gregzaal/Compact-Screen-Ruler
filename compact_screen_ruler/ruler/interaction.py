"""Mouse and hover interaction logic for the ruler widget."""

from PyQt6 import QtCore, QtGui, QtWidgets

from ..utils import snap


class RulerInteractionMixin:
    """Provide mouse interaction behaviors (move, resize, click actions)."""

    def getSnapIncrement(self, axis):
        # Use the same logic as tick config for medium tick spacing
        if hasattr(self, "getTickConfig"):
            return self.getTickConfig(axis)["medium_step_px"]
        # Fallback to default
        return 10

    def snapFromOrigin(self, value, origin, axis):
        return origin + snap(value - origin, self.getSnapIncrement(axis))

    def updateHoverState(self, local_x, local_y):
        hover_zones = self.getResizeHitZones(local_x, local_y)
        if hover_zones != self.hover_zones:
            self.hover_zones = hover_zones
            self.update()

        if self.middleclick:
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            return

        if self.leftclick:
            return

        is_over_resolution_text = (
            self.resolution_text_click_enabled
            and not self.is_transparent
            and self.resolution_text_rect.contains(QtCore.QPoint(local_x, local_y))
        )
        if self.resolution_text_hovered != is_over_resolution_text:
            self.resolution_text_hovered = is_over_resolution_text
            self.update()

        if is_over_resolution_text:
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            return

        self.setCursor(self.getResizeCursorShape(hover_zones))

    def mousePressEvent(self, event):
        local_pos = event.position().toPoint()
        self.left_press_started_on_resolution_text = (
            event.button() == QtCore.Qt.MouseButton.LeftButton
            and self.resolution_text_click_enabled
            and self.resolution_text_rect.contains(local_pos)
            and not self.is_transparent
        )
        self.left_dragged_since_press = False
        self.press_global_pos = event.globalPosition().toPoint()

        self.leftclick = event.button() == QtCore.Qt.MouseButton.LeftButton
        self.middleclick = event.button() == QtCore.Qt.MouseButton.MiddleButton
        self.drawPickPos = event.button() == QtCore.Qt.MouseButton.RightButton
        self.offset = event.pos()
        self.opos = self.pos()

        if self.middleclick:
            self.active_interaction_zones = {"left": False, "right": False, "top": False, "bottom": False}
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
        elif self.leftclick:
            press_zones = self.getResizeHitZones(local_pos.x(), local_pos.y())
            self.active_interaction_zones = dict(press_zones)
            if any(press_zones.values()):
                self.setCursor(self.getResizeCursorShape(press_zones))
            else:
                self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
        else:
            self.active_interaction_zones = {"left": False, "right": False, "top": False, "bottom": False}

    def mouseMoveEvent(self, event):
        ctrl_is_held = bool(QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ControlModifier)
        shift_is_held = bool(QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier)
        screen_edge_snap_enabled = not shift_is_held
        window_x = self.pos().x()
        window_y = self.pos().y()
        global_pos = event.globalPosition()
        global_x = int(global_pos.x())
        global_y = int(global_pos.y())
        local_pos = event.position().toPoint()
        self.updateHoverState(local_pos.x(), local_pos.y())

        self.mouse_x = global_x
        self.mouse_y = global_y

        if self.middleclick:
            move_x = global_x - self.offset.x()
            move_y = global_y - self.offset.y()
            if screen_edge_snap_enabled:
                move_x, move_y = self.snapPositionToScreenEdges(move_x, move_y, self.window_size_x, self.window_size_y)
            if ctrl_is_held:
                self.move(
                    self.snapFromOrigin(move_x, self.opos.x(), "x"), self.snapFromOrigin(move_y, self.opos.y(), "y")
                )
            else:
                self.move(move_x, move_y)
            self.update()
        elif self.leftclick:
            drag_distance = (global_pos.toPoint() - self.press_global_pos).manhattanLength()
            if drag_distance >= QtWidgets.QApplication.startDragDistance():
                self.left_dragged_since_press = True

            local_x = self.offset.x()
            local_y = self.offset.y()
            gsize_x = min(self.GRAB_HANDLE_SIZE, max(1, self.window_size_x // 2))
            gsize_y = min(self.GRAB_HANDLE_SIZE, max(1, self.window_size_y // 2))

            resize_x = None
            resize_y = None

            move_x = None
            move_y = None

            if local_x > self.window_size_x - gsize_x and local_y > self.window_size_y - gsize_y:
                resize_x = max(self.MIN_WINDOW_SIZE, global_x - window_x + (self.window_size_x - local_x))
                resize_y = max(self.MIN_WINDOW_SIZE, global_y - window_y + (self.window_size_y - local_y))
            elif local_x < gsize_x and local_y > self.window_size_y - gsize_y:
                resize_x = max(self.MIN_WINDOW_SIZE, self.window_size_x - global_x + self.opos.x() + local_x)
                resize_y = max(self.MIN_WINDOW_SIZE, global_y - window_y + (self.window_size_y - local_y))
                move_x = global_x - local_x
                move_y = window_y
            elif local_x > self.window_size_x - gsize_x and local_y < gsize_y:
                resize_x = max(self.MIN_WINDOW_SIZE, global_x - window_x + (self.window_size_x - local_x))
                resize_y = max(self.MIN_WINDOW_SIZE, self.window_size_y - global_y + self.opos.y() + local_y)
                move_x = window_x
                move_y = global_y - local_y
            elif local_x < gsize_x and local_y < gsize_y:
                resize_x = max(self.MIN_WINDOW_SIZE, self.window_size_x - global_x + self.opos.x() + local_x)
                resize_y = max(self.MIN_WINDOW_SIZE, self.window_size_y - global_y + self.opos.y() + local_y)
                move_x = global_x - local_x
                move_y = global_y - local_y
            elif local_y > self.window_size_y - gsize_y:
                resize_x = max(self.MIN_WINDOW_SIZE, self.window_size_x)
                resize_y = max(self.MIN_WINDOW_SIZE, global_y - window_y + (self.window_size_y - local_y))
            elif local_y < gsize_y:
                resize_x = max(self.MIN_WINDOW_SIZE, self.window_size_x)
                resize_y = max(self.MIN_WINDOW_SIZE, self.window_size_y - global_y + self.opos.y() + local_y)
                move_x = window_x
                move_y = global_y - local_y
            elif local_x > self.window_size_x - gsize_x:
                resize_x = max(self.MIN_WINDOW_SIZE, global_x - window_x + (self.window_size_x - local_x))
                resize_y = max(self.MIN_WINDOW_SIZE, self.window_size_y)
            elif local_x < gsize_x:
                resize_x = max(self.MIN_WINDOW_SIZE, self.window_size_x - global_x + self.opos.x() + local_x)
                resize_y = max(self.MIN_WINDOW_SIZE, self.window_size_y)
                move_x = global_x - local_x
                move_y = window_y
            else:
                move_x = global_x - local_x
                move_y = global_y - local_y

            on_left = local_x < gsize_x
            on_right = local_x > self.window_size_x - gsize_x
            on_top = local_y < gsize_y
            on_bottom = local_y > self.window_size_y - gsize_y

            if self.aspect_lock_enabled and resize_x is not None and resize_y is not None:
                ratio = self.aspect_lock_ratio if self.aspect_lock_ratio > 0 else 1.0
                base_resize_x = resize_x
                base_resize_y = resize_y
                delta_x = abs(base_resize_x - self.window_size_x)
                delta_y = abs(base_resize_y - self.window_size_y)

                if delta_x >= delta_y:
                    resize_x = max(self.MIN_WINDOW_SIZE, base_resize_x)
                    resize_y = max(self.MIN_WINDOW_SIZE, int(round(resize_x / ratio)))
                    resize_x = max(self.MIN_WINDOW_SIZE, int(round(resize_y * ratio)))
                else:
                    resize_y = max(self.MIN_WINDOW_SIZE, base_resize_y)
                    resize_x = max(self.MIN_WINDOW_SIZE, int(round(resize_y * ratio)))
                    resize_y = max(self.MIN_WINDOW_SIZE, int(round(resize_x / ratio)))

                orig_left = self.opos.x()
                orig_top = self.opos.y()
                orig_right = orig_left + self.window_size_x
                orig_bottom = orig_top + self.window_size_y

                if on_left and not on_right:
                    move_x = orig_right - resize_x
                elif on_right and not on_left:
                    move_x = orig_left
                elif not on_left and not on_right:
                    move_x = orig_left + int(round((self.window_size_x - resize_x) / 2))

                if on_top and not on_bottom:
                    move_y = orig_bottom - resize_y
                elif on_bottom and not on_top:
                    move_y = orig_top
                elif not on_top and not on_bottom:
                    move_y = orig_top + int(round((self.window_size_y - resize_y) / 2))

            if screen_edge_snap_enabled:
                if resize_x is not None and resize_y is not None:
                    geometry_x = move_x if move_x is not None else window_x
                    geometry_y = move_y if move_y is not None else window_y
                    geometry_x, geometry_y, resize_x, resize_y = self.snapResizeGeometryToScreenEdges(
                        geometry_x,
                        geometry_y,
                        resize_x,
                        resize_y,
                        on_left,
                        on_right,
                        on_top,
                        on_bottom,
                    )
                    move_x = geometry_x
                    move_y = geometry_y
                elif move_x is not None and move_y is not None:
                    move_x, move_y = self.snapPositionToScreenEdges(
                        move_x, move_y, self.window_size_x, self.window_size_y
                    )

            if resize_x is not None and resize_y is not None:
                if ctrl_is_held:
                    # Only snap the axis being resized, using unit-aware increment
                    if (on_left or on_right) and not (on_top or on_bottom):
                        resize_x = snap(resize_x, self.getSnapIncrement("x"))
                    elif (on_top or on_bottom) and not (on_left or on_right):
                        resize_y = snap(resize_y, self.getSnapIncrement("y"))
                    else:
                        resize_x = snap(resize_x, self.getSnapIncrement("x"))
                        resize_y = snap(resize_y, self.getSnapIncrement("y"))

                    orig_left = self.opos.x()
                    orig_top = self.opos.y()
                    orig_right = orig_left + self.window_size_x
                    orig_bottom = orig_top + self.window_size_y

                    if on_left and not on_right:
                        move_x = orig_right - resize_x
                    elif on_right and not on_left:
                        move_x = orig_left

                    if on_top and not on_bottom:
                        move_y = orig_bottom - resize_y
                    elif on_bottom and not on_top:
                        move_y = orig_top

                self.resize(resize_x, resize_y)
            if move_x is not None and move_y is not None:
                if ctrl_is_held and resize_x is None and resize_y is None:
                    self.move(
                        self.snapFromOrigin(move_x, self.opos.x(), "x"), self.snapFromOrigin(move_y, self.opos.y(), "y")
                    )
                else:
                    self.move(move_x, move_y)
            self.update()

        else:
            self.update()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.hover_zones = {"left": False, "right": False, "top": False, "bottom": False}
        self.active_interaction_zones = {"left": False, "right": False, "top": False, "bottom": False}
        self.resolution_text_hovered = False
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        self.update()

    def mouseReleaseEvent(self, event):
        release_pos = event.position().toPoint()
        should_open_size_dialog = (
            event.button() == QtCore.Qt.MouseButton.LeftButton
            and self.resolution_text_click_enabled
            and self.left_press_started_on_resolution_text
            and not self.left_dragged_since_press
            and not self.is_transparent
            and self.resolution_text_rect.contains(release_pos)
        )

        self.leftclick = False
        self.middleclick = False
        self.window_size_x = self.width()
        self.window_size_y = self.height()
        self.drawPickPos = False
        self.active_interaction_zones = {"left": False, "right": False, "top": False, "bottom": False}
        self.left_press_started_on_resolution_text = False
        self.left_dragged_since_press = False
        local_pos = self.mapFromGlobal(QtGui.QCursor.pos())
        self.updateHoverState(local_pos.x(), local_pos.y())
        self.update()

        if should_open_size_dialog:
            self.setWindowSize()
