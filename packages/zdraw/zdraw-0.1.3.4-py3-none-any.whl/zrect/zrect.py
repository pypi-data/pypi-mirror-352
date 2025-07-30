import cv2
import numpy as np
import random

class ZRect:
    def __init__(self, class_colors={}):
        self.class_colors = class_colors

    def get_color_for_class(self, class_name):
        """Get a color for the class. Assign a random color if not already defined."""
        if class_name not in self.class_colors:
            self.class_colors[class_name] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )

    def draw_rec(self, frame, top_left, bottom_right, border_color, fill_color):
        x1, y1 = top_left
        x2, y2 = bottom_right
        box_width = x2 - x1
        box_height = y2 - y1
        # Dynamically adjust corner radius and thickness
        corner_radius = max(5, min(box_width, box_height) // 10)  # At least 5, 10% of the smaller dimension
        thickness = max(1, min(box_width, box_height) // 50)  # At least 1, 2% of the smaller dimension
        # Create a mask for the filled rectangle with rounded corners
        mask = np.zeros_like(frame, dtype=np.uint8)
        cv2.rectangle(mask, (x1 + corner_radius, y1), (x2 - corner_radius, y2), fill_color, -1)
        cv2.rectangle(mask, (x1, y1 + corner_radius), (x2, y2 - corner_radius), fill_color, -1)
        cv2.ellipse(mask, (x1 + corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 180, 0, 90, fill_color, -1)
        cv2.ellipse(mask, (x2 - corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 270, 0, 90, fill_color, -1)
        cv2.ellipse(mask, (x1 + corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 90, 0, 90, fill_color, -1)
        cv2.ellipse(mask, (x2 - corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 0, 0, 90, fill_color, -1)
        frame = cv2.addWeighted(frame, 1.0, mask, 0.2, 0)
        # Draw the four rounded corners borders
        cv2.ellipse(frame, (x1 + corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 180, 0, 90, border_color, thickness)
        cv2.ellipse(frame, (x2 - corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 270, 0, 90, border_color, thickness)
        cv2.ellipse(frame, (x1 + corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 90, 0, 90, border_color, thickness)
        cv2.ellipse(frame, (x2 - corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 0, 0, 90, border_color, thickness)
        # Draw lines on the center of the left and right edges
        center_y = (y1 + y2) // 2
        cv2.line(frame, (x1, center_y - corner_radius), (x1, center_y + corner_radius), border_color, thickness)
        cv2.line(frame, (x2, center_y - corner_radius), (x2, center_y + corner_radius), border_color, thickness)
        return frame

    def draw_zrect(self, frame, x1, y1, x2, y2, class_name, color):
        """Draw a custom bounding box with rounded corners and a solid background for the label."""
        # Draw the main bounding box with rounded corners
        frame = self.draw_rec(frame, (x1 - 2, y1 - 2), (x2 + 2, y2 + 2), color, color)
        # Draw the label with a solid background
        label_size, _ = cv2.getTextSize(class_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        label_width = label_size[0]
        label_height = label_size[1]
        label_y_offset = y1 - label_height - 10 if y1 - label_height - 10 > 0 else y1 + label_height + 10
        # Draw the solid background for the label
        cv2.rectangle(frame, (x1 - 1, label_y_offset - label_height - 2),
                      (x1 + label_width + 10, label_y_offset), color, -1)

        # Draw the class name on the label
        cv2.putText(frame, class_name, (x1 + 5, label_y_offset - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return frame