# =============================================================================
# FrameDisplayHelper - Unified Frame Handling for Both BGR and RGBA Formats
# =============================================================================
# This class handles both older containers using frame.data() (BGRA)
# and newer containers supporting frame.data_rgba() (RGBA).
#
# Key features:
# - Automatically detects and uses frame.data_rgba() when available
# - Handles color channel swapping for OpenCV functions (BGRA vs RGBA)
# - Only detects the format once and caches the result for performance
# - Provides consistent drawing functions that work with both formats
# - Passes the correct format parameter to self.write_label_on_frame
#
# Usage:
#   with FrameDisplayHelper.init(frame) as wrapped_frame:
#       wrapped_frame.rectangle(pt1, pt2, (0, 255, 0), 2)
#       wrapped_frame.text(x, y, "Text")
# =============================================================================
import cv2
import textwrap
from contextlib import contextmanager

class FrameDisplayHelper:
    """
    Utility class for displaying content on frames with automatic format handling.
    This class handles both BGRA (frame.data()) and RGBA (frame.data_rgba()) formats,
    automatically detecting the best format to use and managing color channel
    swapping as needed.
    Features:
    - Automatically detects the best frame data access method
    - Handles color channel swapping for different formats
    - Provides consistent drawing methods that work with any format
    """

    # Class-level cache for format detection
    _format_detected = False
    _supports_rgba = None

    def __init__(self, mat=None, using_rgba=False):
        """Initialize with an optional matrix and format flag"""
        self._mat = mat  # Store as private attribute
        self._using_rgba = using_rgba
        self._detected = using_rgba is not None

    @property
    def mat(self):
        """Get the raw matrix data"""
        return self._mat  # Return the actual numpy array, not a context manager

    @classmethod
    @contextmanager
    def init(cls, frame):
        """Context manager to create a helper with the best available frame data"""
        # Only detect the format once across all instances
        if not cls._format_detected:
            cls._supports_rgba = hasattr(frame, 'data_rgba')
            cls._format_detected = True

        # Explicitly enter the context managers to get the actual matrix data
        if cls._supports_rgba:
            with frame.data_rgba() as actual_mat:
                helper = cls(actual_mat, True)
        else:
            with frame.data() as actual_mat:
                helper = cls(actual_mat, False)

        try:
            yield helper
        finally:
            # Clean up if needed
            pass

    def _swap_rb_if_needed(self, color):
        """Swap red and blue channels if needed based on frame format"""
        # Swap channels if needed (for RGBA format)
        if self._using_rgba and color is not None and hasattr(color, '__len__') and len(color) >= 3:
            # For RGBA we need to swap R and B
            color_list = list(color)
            color_list[0], color_list[2] = color_list[2], color_list[0]
            return tuple(color_list)
        return color

    # OpenCV display operations
    def rectangle(self, pt1, pt2, color, thickness=1, lineType=None, shift=0):
        """Draw rectangle with correct color channels for both BGR and RGBA"""
        if lineType is None:
            lineType = cv2.LINE_8
        color = self._swap_rb_if_needed(color)
        return cv2.rectangle(self.mat, pt1, pt2, color, thickness, lineType, shift)

    def polylines(self, pts, is_closed, color, thickness=1, lineType=None, shift=0):
        """Draw polylines with correct color channels for both BGR and RGBA"""
        if lineType is None:
            lineType = cv2.LINE_8
        color = self._swap_rb_if_needed(color)
        return cv2.polylines(self.mat, pts, is_closed, color, thickness, lineType, shift)

    def circle(self, center, radius, color, thickness=1, lineType=None, shift=0):
        """Draw circle with correct color channels for both BGR and RGBA"""
        if lineType is None:
            lineType = cv2.LINE_8
        color = self._swap_rb_if_needed(color)
        return cv2.circle(self.mat, center, radius, color, thickness, lineType, shift)

    def line(self, pt1, pt2, color, thickness=1, lineType=None, shift=0):
        """Draw line with correct color channels for both BGR and RGBA"""
        if lineType is None:
            lineType = cv2.LINE_8
        color = self._swap_rb_if_needed(color)
        return cv2.line(self.mat, pt1, pt2, color, thickness, lineType, shift)

    def put_text(self, text, org, fontFace, fontScale, color, thickness=1, lineType=None, bottomLeftOrigin=False):
        """Write text with correct color channels for both BGR and RGBA"""
        if lineType is None:
            lineType = cv2.LINE_8
        color = self._swap_rb_if_needed(color)
        return cv2.putText(self.mat, text, org, fontFace, fontScale, color, thickness, lineType, bottomLeftOrigin)

    def write_label_on_frame(self, xidx, yidx, label, color=(255, 255, 255), font_scale=None, thickness=None, bg_color=None, font=None):
        """Auxiliary function to write text label on frame"""
        my_font_scale = 0.75
        my_wrap_width = 120

        black = (0, 0, 0)
        if self._using_rgba:
            yellow = (255, 255, 0)  # RGBA format
        else:
            yellow = (0, 255, 255)  # BGRA format

        frame_width = self.mat.shape[1]
        if frame_width <= 640:
            my_font_scale = 0.75
            my_wrap_width = 120
        elif frame_width <= 1280:
            my_font_scale = 1.0
            my_wrap_width = 160
        else:
            my_font_scale = 1.5
            my_wrap_width = 200

        wrapped_label = textwrap.wrap(label, width=my_wrap_width)
        total_label_height = 0

        for line in wrapped_label:
            (label_width, label_height), baseline = cv2.getTextSize(line, cv2.FONT_HERSHEY_PLAIN,
                                                                   my_font_scale, 1)
            label_height = label_height + 5
            cv2.rectangle(self.mat, (xidx, yidx), (xidx + label_width, yidx + label_height + baseline), yellow, -1)
            cv2.putText(self.mat, line, (xidx, yidx + label_height), cv2.FONT_HERSHEY_PLAIN, my_font_scale, black, 1,
                       cv2.LINE_AA)
            yidx = yidx + label_height + baseline
            total_label_height = total_label_height + label_height + baseline

        return (label_width, total_label_height)

    def text(self, x, y, text, color=(255, 255, 255), font_scale=None, thickness=None, bg_color=None, font=None):
        """Write text with correct format for both BGR and RGBA"""
        color = self._swap_rb_if_needed(color)
        bg_color = self._swap_rb_if_needed(bg_color) if bg_color is not None else None

        return self.write_label_on_frame(x, y, text,
                                        color=color,
                                        font_scale=font_scale,
                                        thickness=thickness,
                                        bg_color=bg_color,
                                        font=font)
