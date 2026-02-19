"""Formatting and unit conversion presentation helpers for ruler rendering."""


class RulerRenderingFormatMixin:
    """Provide text/tick formatting helpers used by paint routines."""

    def getTickConfig(self, axis):
        if self.measurement_unit == "px":
            return {
                "small_step_px": 5.0,
                "medium_step_px": 10.0,
                "major_step_px": 50.0,
                "major_unit": 50.0,
                "distinct_subticks": False,
            }

        major_unit = 1.0
        if self.measurement_unit == "cm":
            medium_unit = 0.5
            small_unit = 0.1
        else:
            medium_unit = 0.25
            small_unit = 0.125

        small_step_px = self.convertUnitToPixels(small_unit, axis, self.measurement_unit)
        medium_step_px = self.convertUnitToPixels(medium_unit, axis, self.measurement_unit)
        major_step_px = self.convertUnitToPixels(major_unit, axis, self.measurement_unit)

        if small_step_px <= 0 or medium_step_px <= 0 or major_step_px <= 0:
            return {
                "small_step_px": 5.0,
                "medium_step_px": 10.0,
                "major_step_px": 50.0,
                "major_unit": 5.0,
                "distinct_subticks": False,
            }

        small_step_px = max(3.0, small_step_px)
        medium_step_px = max(6.0, medium_step_px)
        major_step_px = max(20.0, major_step_px)
        return {
            "small_step_px": small_step_px,
            "medium_step_px": medium_step_px,
            "major_step_px": major_step_px,
            "major_unit": major_unit,
            "distinct_subticks": True,
        }

    def isNearStep(self, value, step, tolerance):
        if step <= 0:
            return False
        nearest_index = int(round(value / step))
        nearest_value = nearest_index * step
        return abs(value - nearest_value) <= tolerance

    def formatTickLabel(self, value):
        if self.measurement_unit == "px":
            return str(int(round(value)))
        return f"{value:.2f}".rstrip("0").rstrip(".")

    def formatMeasurementValue(self, value_px, axis):
        unit = self.measurement_unit
        if unit == "px":
            return str(int(round(float(value_px))))

        converted_value = self.convertPixelsToUnit(value_px, axis, unit)
        return f"{converted_value:.2f}".rstrip("0").rstrip(".")

    def buildResolutionText(self, size_x, size_y, include_y):
        unit = self.measurement_unit
        size_x_text = self.formatMeasurementValue(size_x, "x")
        if include_y:
            size_y_text = self.formatMeasurementValue(size_y, "y")
            return f"{size_x_text} x {size_y_text} {unit}"
        return f"{size_x_text} {unit}"
