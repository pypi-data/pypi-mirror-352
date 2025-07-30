import random
import cv2
import numpy as np


class ZDraw:
    def __init__(self, class_colors=None):
        """
        Initialize the ZDraw object.
        :param class_colors: Optional dictionary for class-to-color mapping.
        """
        self.class_colors = class_colors or {}
        self.shape_colors = {
            "line": (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
            "triangle": (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
            "rectangle": (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
            "square": (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
            "polygon": (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
        }

    def get_color_for_class(self, class_name):
        """
        Get or assign a random color for the class.
        :param class_name: Name of the class.
        :return: RGB color tuple.
        """
        if class_name not in self.class_colors:
            self.class_colors[class_name] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
        return self.class_colors[class_name]

    def __draw_rec__(self, frame, top_left, bottom_right, border_color, fill_color):
        """
        Draw a rounded rectangle with dynamic corner radius and thickness.
        :param frame: The input image frame.
        :param top_left: Top-left corner (x1, y1).
        :param bottom_right: Bottom-right corner (x2, y2).
        :param border_color: Color of the border (BGR tuple).
        :param fill_color: Color of the fill (BGR tuple).
        :return: Modified frame.
        """
        x1, y1 = top_left
        x2, y2 = bottom_right
        box_width = x2 - x1
        box_height = y2 - y1

        # Dynamically adjust corner radius and thickness based on box size
        corner_radius = max(5, min(box_width, box_height) // 10)
        thickness = max(1, min(box_width, box_height) // 50)

        # Create a mask for the filled rectangle with rounded corners
        mask = np.zeros_like(frame, dtype=np.uint8)
        cv2.rectangle(mask, (x1 + corner_radius, y1), (x2 - corner_radius, y2), fill_color, -1)
        cv2.rectangle(mask, (x1, y1 + corner_radius), (x2, y2 - corner_radius), fill_color, -1)
        cv2.ellipse(mask, (x1 + corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 180, 0, 90, fill_color, -1)
        cv2.ellipse(mask, (x2 - corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 270, 0, 90, fill_color, -1)
        cv2.ellipse(mask, (x1 + corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 90, 0, 90, fill_color, -1)
        cv2.ellipse(mask, (x2 - corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 0, 0, 90, fill_color, -1)
        frame = cv2.addWeighted(frame, 1.0, mask, 0.2, 0)
        # Draw the rounded corner borders
        cv2.ellipse(frame, (x1 + corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 180, 0, 90, border_color, thickness)
        cv2.ellipse(frame, (x2 - corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 270, 0, 90, border_color, thickness)
        cv2.ellipse(frame, (x1 + corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 90, 0, 90, border_color, thickness)
        cv2.ellipse(frame, (x2 - corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 0, 0, 90, border_color, thickness)

        return frame

    def __draw_shape__(self, frame, points, shape=None, return_original_frame=False):
        """
        Draw a universal shape (line, triangle, rectangle, square, or polygon) based on points and shape type.
        :param frame: Input image frame.
        :param points: List of points defining the shape.
        :param shape: Optional shape name for double-checking ('line', 'triangle', etc.).
        :return: Frame with the drawn shape.
        """
        original_frame = frame.copy()
        num_points = len(points)
        # Determine the shape type based on points
        if num_points == 2:
            detected_shape = "line"
        elif num_points == 3:
            detected_shape = "triangle"
        elif num_points == 4:
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            width = max(x_coords) - min(x_coords)
            height = max(y_coords) - min(y_coords)
            detected_shape = "square" if abs(width - height) <= 5 else "rectangle"
        else:
            detected_shape = "polygon"
        # Use the shape parameter to confirm or override detection
        if shape and shape != detected_shape:
            raise ValueError(f"Shape mismatch: detected '{detected_shape}', but provided '{shape}'")
        # Get color for the shape
        color = self.shape_colors.get(detected_shape, (255, 255, 255))
        # Draw the shape
        if detected_shape == "line":
            cv2.line(frame, points[0], points[1], color, thickness=2)
        elif detected_shape == "triangle":
            mask = np.zeros_like(frame, dtype=np.uint8)
            cv2.fillPoly(mask, [np.array(points)], color)
            frame = cv2.addWeighted(frame, 1.0, mask, 0.2, 0)
            cv2.polylines(frame, [np.array(points)], isClosed=True, color=color, thickness=2)
        elif detected_shape == "rectangle" or detected_shape == "square":
            frame = self.__draw_rec__(frame, points[0], points[2], color, color)
        else:  # Polygon
            mask = np.zeros_like(frame, dtype=np.uint8)
            cv2.fillPoly(mask, [np.array(points)], color)
            frame = cv2.addWeighted(frame, 1.0, mask, 0.2, 0)
            cv2.polylines(frame, [np.array(points)], isClosed=True, color=color, thickness=2)
        if return_original_frame:
            return original_frame, frame
        return frame

    def ZDrawShape(self, frame, points, shape=None, return_original_frame=False):
        """
        Draw a universal shape (line, triangle, rectangle, square, or polygon) based on points and shape type.
        :param frame: Input image frame.
        :param points: List of points defining the shape.
        :param shape: Optional shape name for double-checking ('line', 'triangle', etc.).
        :return: Frame with the drawn shape.
        """
        return self.__draw_shape__(frame, points, shape, return_original_frame)

    def ZDrawRect(self, frame, x1, y1, x2, y2, class_name=None, color=None, return_original_frame=False):
        """
        Draw a custom bounding box with rounded corners and an optional label.
        :param frame: Input image frame.
        :param x1: Top-left x-coordinate of the bounding box.
        :param y1: Top-left y-coordinate of the bounding box.
        :param x2: Bottom-right x-coordinate of the bounding box.
        :param y2: Bottom-right y-coordinate of the bounding box.
        :param class_name: Optional class name for the label.
        :param color: Optional color (BGR). If None, a random color is assigned.
        :param return_original_frame: If True, return the original frame without the bounding box.
        :return: Tuple (original frame, frame with bounding box).
        """
        original_frame = frame.copy()
        frame_height, frame_width, _ = frame.shape
        # Dynamically adjust font size and thickness based on frame size
        font_scale = max(0.4, min(frame_width, frame_height) / 1000)
        font_thickness = max(1, int(min(frame_width, frame_height) / 300))
        # Assign color if not provided
        if color is None:
            color = (0, 255, 0) if class_name is None else self.get_color_for_class(class_name)
        # Draw the main bounding box with rounded corners
        frame = self.__draw_rec__(frame, (x1 - 2, y1 - 2), (x2 + 2, y2 + 2), color, color)
        # Draw the label if class_name is provided
        if class_name:
            label_size, _ = cv2.getTextSize(class_name, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
            label_width, label_height = label_size
            label_y_offset = y1 - label_height - 10 if y1 - label_height - 10 > 0 else y1 + label_height + 10
            # Draw the solid background for the label
            cv2.rectangle(frame, (x1 - 1, label_y_offset - label_height - 2),
                          (x1 + label_width + 10, label_y_offset), color, -1)
            # Draw the class name on the label
            cv2.putText(frame, class_name, (x1 + 5, label_y_offset - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
        if return_original_frame:
            return original_frame, frame
        return frame

    def ZDrawRectCustom(self, frame, x1, y1, x2, y2, main_class, sub_labels=None, color=None,
                       label_position="auto", metadata_style=True, icons=None, return_original_frame=False):
        """
        Enhanced custom bounding box with dynamic multi-label support and metadata-style display.

        :param frame: Input image frame
        :param x1, y1, x2, y2: Bounding box coordinates
        :param main_class: Primary class label
        :param sub_labels: List of additional labels
        :param color: Optional color override
        :param label_position: "auto", "inside", "outside_top", "outside_bottom", "outside_left", "outside_right"
        :param metadata_style: If True, displays labels in unified metadata panel style
        :param icons: Dictionary mapping label names to icon file paths (PNG format)
        :param return_original_frame: Whether to return original frame
        :return: Modified frame or tuple (original, modified)
        """
        original_frame = frame.copy()
        frame_height, frame_width, _ = frame.shape

        # Calculate bounding box dimensions
        bbox_width = x2 - x1
        bbox_height = y2 - y1
        bbox_area = bbox_width * bbox_height
        frame_area = frame_width * frame_height

        # Dynamic font scaling based on frame size, bbox size, and their relationship
        base_font_scale = min(frame_width, frame_height) / 1000
        bbox_scale_factor = min(1.5, max(0.6, (bbox_area / frame_area) * 10))  # Scale based on bbox relative size
        font_scale = max(0.3, min(1.2, base_font_scale * bbox_scale_factor))
        font_thickness = max(1, int(font_scale * 2))

        # Get main color
        color = color or self.get_color_for_class(main_class)
        all_labels = [main_class] + (sub_labels if sub_labels else [])

        # Draw the main bounding box
        frame = self.__draw_rec__(frame, (x1, y1), (x2, y2), border_color=color, fill_color=color)

        # Calculate label dimensions and determine optimal positioning
        label_info = []
        max_label_width = 0
        total_label_height = 0

        for label in all_labels:
            # Handle text overflow - truncate if too long
            display_label = self._truncate_label(label, bbox_width, font_scale, font_thickness)
            label_size, _ = cv2.getTextSize(display_label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
            label_width, label_height = label_size
            max_label_width = max(max_label_width, label_width)
            total_label_height += label_height
            label_info.append((display_label, label_width, label_height))

        # Dynamic spacing based on font size and bbox dimensions
        label_spacing = max(4, int(font_scale * 8))
        label_padding = max(6, int(font_scale * 12))
        total_labels_height = total_label_height + (len(all_labels) - 1) * label_spacing

        # Determine optimal label position
        position = self._determine_label_position(
            label_position, x1, y1, x2, y2, frame_width, frame_height,
            max_label_width + label_padding, total_labels_height + label_padding
        )

        # Draw labels based on style preference
        if metadata_style:
            self._draw_metadata_panel(
                frame, all_labels, label_info, position, font_scale, font_thickness,
                label_spacing, label_padding, frame_width, frame_height, x1, y1, x2, y2,
                color, icons
            )
        else:
            self._draw_labels_at_position(
                frame, all_labels, label_info, position, font_scale, font_thickness,
                label_spacing, label_padding, frame_width, frame_height, x1, y1, x2, y2, color
            )

        return (original_frame, frame) if return_original_frame else frame

    def _truncate_label(self, label, max_width, font_scale, font_thickness):
        """
        Truncate label text if it's too long for the available space.
        """
        if not label:
            return label

        # Calculate available width (leave some margin)
        available_width = max_width * 0.8

        # Check if full label fits
        full_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
        if full_size[0] <= available_width:
            return label

        # Truncate and add ellipsis
        for i in range(len(label) - 1, 0, -1):
            truncated = label[:i] + "..."
            size, _ = cv2.getTextSize(truncated, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
            if size[0] <= available_width:
                return truncated

        return label[:3] + "..." if len(label) > 3 else label

    def _determine_label_position(self, label_position, x1, y1, x2, y2, frame_width, frame_height,
                                 label_width, label_height):
        """
        Determine the optimal position for labels based on available space and preferences.
        """
        bbox_width = x2 - x1
        bbox_height = y2 - y1

        if label_position == "auto":
            # Smart positioning logic
            space_above = y1
            space_below = frame_height - y2
            space_left = x1
            space_right = frame_width - x2
            space_inside = min(bbox_width, bbox_height)

            # Prefer outside positioning if there's enough space
            if space_above >= label_height + 10:
                return "outside_top"
            elif space_below >= label_height + 10:
                return "outside_bottom"
            elif space_right >= label_width + 10:
                return "outside_right"
            elif space_left >= label_width + 10:
                return "outside_left"
            elif space_inside >= max(label_width * 0.7, label_height * 2):
                return "inside"
            else:
                # Fallback to position with most space
                max_space = max(space_above, space_below, space_left, space_right)
                if max_space == space_above:
                    return "outside_top"
                elif max_space == space_below:
                    return "outside_bottom"
                elif max_space == space_right:
                    return "outside_right"
                else:
                    return "outside_left"

        return label_position

    def _draw_labels_at_position(self, frame, all_labels, label_info, position, font_scale, font_thickness,
                                label_spacing, label_padding, frame_width, frame_height, x1, y1, x2, y2, main_color):
        """
        Draw labels at the determined position with proper spacing and backgrounds.
        """
        if not all_labels or not label_info:
            return

        # Calculate starting position based on label position and bbox coordinates
        max_label_width = max(info[1] for info in label_info)
        total_labels_height = sum(info[2] for info in label_info) + (len(label_info) - 1) * label_spacing

        if position == "inside":
            start_x = x1 + label_padding // 2
            start_y = y1 + label_info[0][2] + 5
        elif position == "outside_top":
            start_x = max(0, min(x1, frame_width - max_label_width - label_padding))
            start_y = max(label_info[0][2] + 5, y1 - total_labels_height - 5)
        elif position == "outside_bottom":
            start_x = max(0, min(x1, frame_width - max_label_width - label_padding))
            start_y = min(frame_height - 5, y2 + label_info[0][2] + 10)
        elif position == "outside_left":
            start_x = max(5, x1 - max_label_width - label_padding)
            start_y = max(label_info[0][2] + 5, y1 + label_info[0][2] + 5)
        elif position == "outside_right":
            start_x = min(frame_width - max_label_width - 5, x2 + 10)
            start_y = max(label_info[0][2] + 5, y1 + label_info[0][2] + 5)
        else:  # Default to inside
            start_x = x1 + label_padding // 2
            start_y = y1 + label_info[0][2] + 5

        # Draw each label with background
        current_y = start_y
        for label, (display_label, label_width, label_height) in zip(all_labels, label_info):
            # Ensure we don't draw outside frame boundaries
            if current_y + label_height > frame_height - 5:
                break
            if start_x + label_width > frame_width - 5:
                # Adjust x position if label would go outside frame
                start_x = max(5, frame_width - label_width - 5)

            # Use dark background for text visibility, colored border for consistency
            dark_bg_color = (40, 40, 40)  # Dark gray background for text visibility
            border_color = main_color  # Use main color for border

            # Draw semi-transparent dark background for text visibility
            bg_x1 = max(0, start_x - 3)
            bg_y1 = max(0, current_y - label_height - 3)
            bg_x2 = min(frame_width, start_x + label_width + 6)
            bg_y2 = min(frame_height, current_y + 3)

            # Create dark background with transparency
            overlay = frame.copy()
            cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), dark_bg_color, -1)
            alpha = 0.8  # More opaque for better text visibility
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            # Draw colored border to maintain color consistency with bbox
            border_thickness = max(1, int(font_scale * 2))
            cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), border_color, border_thickness)

            # Draw text with light color for visibility
            text_x = max(3, start_x)
            text_y = max(label_height, current_y - 2)
            text_color = (255, 255, 255)  # White text for good contrast
            cv2.putText(frame, display_label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                       font_scale, text_color, font_thickness)

            # Move to next line
            current_y += label_height + label_spacing

    def _draw_metadata_panel(self, frame, all_labels, label_info, position, font_scale, font_thickness,
                            label_spacing, label_padding, frame_width, frame_height, x1, y1, x2, y2,
                            panel_color, icons):
        """
        Draw a unified metadata panel containing all labels with optional icons.
        """
        if not all_labels or not label_info:
            return

        # Calculate panel dimensions
        max_label_width = max(info[1] for info in label_info)
        total_labels_height = sum(info[2] for info in label_info) + (len(label_info) - 1) * label_spacing

        # Icon size based on font scale
        icon_size = max(16, int(font_scale * 20))
        icon_margin = max(4, int(font_scale * 6))

        # Panel dimensions (accounting for icons if present)
        panel_width = max_label_width + label_padding * 2
        if icons:
            panel_width += icon_size + icon_margin

        panel_height = total_labels_height + label_padding * 2

        # Determine panel position
        panel_x, panel_y = self._get_metadata_panel_position(
            position, x1, y1, x2, y2, frame_width, frame_height, panel_width, panel_height
        )

        # Draw unified background panel with rounded corners
        panel_x2 = min(frame_width - 1, panel_x + panel_width)
        panel_y2 = min(frame_height - 1, panel_y + panel_height)

        # Create semi-transparent dark background for text visibility
        overlay = frame.copy()

        # Use dark background for label readability - simple rectangle, not rounded
        dark_bg_color = (40, 40, 40)  # Dark gray background for text visibility
        cv2.rectangle(overlay, (panel_x, panel_y), (panel_x2, panel_y2), dark_bg_color, -1)

        # Apply transparency for background
        alpha = 0.9  # Very opaque for better text visibility on bright backgrounds
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Draw visible border around the metadata panel using the same color
        border_thickness = max(2, int(font_scale * 3))
        cv2.rectangle(frame, (panel_x, panel_y), (panel_x2, panel_y2), panel_color, border_thickness)

        # Draw labels and icons
        current_y = panel_y + label_padding + label_info[0][2]

        for label, (display_label, _, label_height) in zip(all_labels, label_info):
            # Draw icon if available
            icon_x = panel_x + label_padding
            text_x = icon_x

            if icons and label in icons:
                icon = self._load_icon(icons[label], (icon_size, icon_size))
                if icon is not None:
                    icon_y = current_y - label_height
                    self._draw_icon(frame, icon, icon_x, icon_y)
                    text_x = icon_x + icon_size + icon_margin

            # Draw text with light color for visibility on dark background
            text_color = (255, 255, 255)  # White text for good contrast
            cv2.putText(frame, display_label, (text_x, current_y), cv2.FONT_HERSHEY_SIMPLEX,
                       font_scale, text_color, font_thickness)

            # Move to next line
            current_y += label_height + label_spacing

    def _get_metadata_panel_position(self, position, x1, y1, x2, y2, frame_width, frame_height,
                                   panel_width, panel_height):
        """
        Calculate the optimal position for the metadata panel.
        """
        if position == "inside":
            return x1 + 10, y1 + 10
        elif position == "outside_top":
            return max(0, min(x1, frame_width - panel_width)), max(0, y1 - panel_height - 10)
        elif position == "outside_bottom":
            return max(0, min(x1, frame_width - panel_width)), min(frame_height - panel_height, y2 + 10)
        elif position == "outside_left":
            return max(0, x1 - panel_width - 10), max(0, min(y1, frame_height - panel_height))
        elif position == "outside_right":
            return min(frame_width - panel_width, x2 + 10), max(0, min(y1, frame_height - panel_height))
        else:  # Default to inside
            return x1 + 10, y1 + 10

    def _load_icon(self, icon_path, target_size):
        """
        Load and resize a PNG icon.

        :param icon_path: Path to the PNG icon file
        :param target_size: Tuple (width, height) for resizing
        :return: Resized icon as numpy array or None if failed
        """
        try:
            icon = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)
            if icon is None:
                return None

            # Resize icon to target size
            icon_resized = cv2.resize(icon, target_size, interpolation=cv2.INTER_AREA)
            return icon_resized
        except Exception:
            return None

    def _draw_icon(self, frame, icon, x, y):
        """
        Draw a PNG icon with transparency support on the frame.

        :param frame: Target frame
        :param icon: Icon array (with or without alpha channel)
        :param x, y: Position to draw the icon
        """
        if icon is None:
            return

        icon_h, icon_w = icon.shape[:2]

        # Ensure we don't draw outside frame boundaries
        if x + icon_w > frame.shape[1] or y + icon_h > frame.shape[0] or x < 0 or y < 0:
            return

        if icon.shape[2] == 4:  # Has alpha channel
            # Extract alpha channel
            alpha = icon[:, :, 3] / 255.0

            # Blend the icon with the frame
            for c in range(3):  # BGR channels
                frame[y:y+icon_h, x:x+icon_w, c] = (
                    alpha * icon[:, :, c] +
                    (1 - alpha) * frame[y:y+icon_h, x:x+icon_w, c]
                )
        else:  # No alpha channel, direct copy
            frame[y:y+icon_h, x:x+icon_w] = icon

    def ZDrawKeypoints(self, frame, keypoints, skeleton=None, point_color=(0, 255, 255), line_color=(255, 0, 0),
                       radius=3, thickness=2):
        """
        Draw keypoints with optional skeleton connections.
        :param frame: Image frame.
        :param keypoints: List of (x, y, visibility) tuples.
        :param skeleton: Optional list of (idx1, idx2) connections.
        """
        for x, y, v in keypoints:
            if v:
                cv2.circle(frame, (int(x), int(y)), radius, point_color, -1)
        if skeleton:
            for i, j in skeleton:
                if keypoints[i][2] and keypoints[j][2]:
                    pt1 = (int(keypoints[i][0]), int(keypoints[i][1]))
                    pt2 = (int(keypoints[j][0]), int(keypoints[j][1]))
                    cv2.line(frame, pt1, pt2, line_color, thickness)
        return frame

