# ZDraw

ZDraw is a powerful Python library for drawing custom bounding boxes with rounded corners on images using OpenCV. It features advanced multi-label support, metadata-style panels, PNG icon integration, and intelligent dynamic sizing for professional computer vision applications.

## Features

### Core Drawing Capabilities
- **Rounded rectangles** with dynamic corner radius and border thickness
- **Universal shape drawing** (lines, triangles, rectangles, polygons)
- **Keypoint visualization** with skeleton connections
- **Smart color management** with automatic class-to-color mapping

### Advanced Label System (ZDrawRectCustom)
- **Multi-label support** - Display multiple labels per bounding box
- **Metadata-style panels** - Unified background for all labels (like professional CV applications)
- **PNG icon support** - Add icons next to labels with full transparency support
- **Dynamic positioning** - Auto-detection of optimal label placement
- **Smart text handling** - Automatic truncation for long labels
- **Responsive sizing** - Font and spacing adapt to frame and bounding box dimensions
- **Boundary-aware** - Prevents labels from extending outside frame boundaries

## Installation

```bash
pip install zdraw
```

## Quick Start

### Basic Bounding Box with Label

```python
import cv2
from zdraw import ZDraw

# Initialize ZDraw
zdraw = ZDraw()

# Load an image
frame = cv2.imread("image.jpg")
frame = cv2.resize(frame, (800, 600), interpolation=cv2.INTER_AREA)

# Draw simple bounding box with label
x1, y1, x2, y2 = 100, 150, 400, 300
frame = zdraw.ZDrawRect(frame, x1, y1, x2, y2, class_name="person")
```

### Advanced Multi-Label with Metadata Style

```python
# PPE Detection with metadata-style panel
frame = zdraw.ZDrawRectCustom(
    frame, x1, y1, x2, y2,
    main_class="person",
    sub_labels=["helmet", "safety_vest", "steel_boots"],
    metadata_style=True,  # Unified background panel
    label_position="auto"  # Smart positioning
)

# With PNG icons (optional)
icons = {
    "person": "icons/person.png",
    "helmet": "icons/helmet.png",
    "safety_vest": "icons/vest.png"
}

frame = zdraw.ZDrawRectCustom(
    frame, x1, y1, x2, y2,
    main_class="person",
    sub_labels=["helmet", "safety_vest"],
    metadata_style=True,
    icons=icons,  # Optional PNG icons
    label_position="outside_top"
)
```

## Usage Examples

### Shape Drawing

```python
# Draw various shapes
line_points = [(50, 50), (200, 50)]
triangle_points = [(250, 100), (350, 100), (300, 200)]
rectangle_points = [(50, 300), (200, 300), (200, 400), (50, 400)]

frame = zdraw.ZDrawShape(frame, line_points, shape="line")
frame = zdraw.ZDrawShape(frame, triangle_points, shape="triangle")
frame = zdraw.ZDrawShape(frame, rectangle_points, shape="rectangle")
```

### PPE Detection Example

```python
# Real-world PPE monitoring scenario
frame = zdraw.ZDrawRectCustom(
    frame, 100, 100, 300, 400,
    main_class="person",
    sub_labels=["helmet", "vest", "boots"],
    metadata_style=True,
    label_position="auto"
)

# Violation detection
frame = zdraw.ZDrawRectCustom(
    frame, 400, 100, 600, 400,
    main_class="person",
    sub_labels=["violator"],
    metadata_style=True,
    label_position="outside_top"
)
```

## API Reference

### Core Methods

#### `ZDraw(class_colors=None)`
Initializes the ZDraw object.

**Parameters:**
- `class_colors` (dict, optional): Dictionary mapping class names to RGB tuples

#### `ZDrawRect(frame, x1, y1, x2, y2, class_name=None, color=None, return_original_frame=False)`
Draws a simple bounding box with optional label.

**Parameters:**
- `frame`: Input image frame
- `x1, y1, x2, y2`: Bounding box coordinates
- `class_name`: Optional class label
- `color`: Optional color override
- `return_original_frame`: Whether to return original frame

#### `ZDrawRectCustom(frame, x1, y1, x2, y2, main_class, sub_labels=None, color=None, label_position="auto", metadata_style=True, icons=None, return_original_frame=False)`
Enhanced bounding box with multi-label support and metadata-style panels.

**Parameters:**
- `frame`: Input image frame
- `x1, y1, x2, y2`: Bounding box coordinates
- `main_class`: Primary class label
- `sub_labels`: List of additional labels
- `color`: Optional color override
- `label_position`: Label positioning ("auto", "inside", "outside_top", "outside_bottom", "outside_left", "outside_right")
- `metadata_style`: If True, displays unified metadata panel (default: True)
- `icons`: Dictionary mapping label names to PNG icon file paths (optional)
- `return_original_frame`: Whether to return original frame

#### `ZDrawShape(frame, points, shape=None, return_original_frame=False)`
Draws universal shapes (lines, triangles, rectangles, polygons).

**Parameters:**
- `frame`: Input image frame
- `points`: List of points defining the shape
- `shape`: Optional shape type for validation
- `return_original_frame`: Whether to return original frame

#### `ZDrawKeypoints(frame, keypoints, skeleton=None, point_color=(0, 255, 255), line_color=(255, 0, 0), radius=3, thickness=2)`
Draws keypoints with optional skeleton connections.

**Parameters:**
- `frame`: Input image frame
- `keypoints`: List of (x, y, visibility) tuples
- `skeleton`: Optional list of (idx1, idx2) connections
- `point_color`: Color for keypoints
- `line_color`: Color for skeleton lines
- `radius`: Keypoint radius
- `thickness`: Line thickness

### Label Positioning Options

- `"auto"`: Automatically chooses the best position based on available space
- `"inside"`: Places labels inside the bounding box
- `"outside_top"`: Places labels above the bounding box
- `"outside_bottom"`: Places labels below the bounding box
- `"outside_left"`: Places labels to the left of the bounding box
- `"outside_right"`: Places labels to the right of the bounding box

### Icon Support

Icons should be PNG files with transparency support. The `icons` parameter accepts a dictionary mapping label names to file paths:

```python
icons = {
    "person": "path/to/person.png",
    "helmet": "path/to/helmet.png",
    "vest": "path/to/vest.png"
}
```

### Dependencies

- Python 3.8 or higher
- OpenCV (opencv-python)
- NumPy

## License

This project is licensed under the MIT License. See the LICENSE file for details.