import cv2
from zdraw import ZDraw
# Initialize ZDraw with an optional class color map
# Initialize ZDraw
zdraw = ZDraw()

# Load an image
frame = cv2.imread("image.jpg")
frame = cv2.resize(frame, (800, 600), interpolation=cv2.INTER_AREA)
# Define bounding box coordinates and class
x1, y1, x2, y2 = 100, 150, 400, 300
class_name = "DynamicObject"

# Draw bounding box with label
line_x1, line_y1, line_x2, line_y2 = 50, 50, 200, 50
tri_x1, tri_y1, tri_x2, tri_y2 = 250, 100, 350, 200
rect_x1, rect_y1, rect_x2, rect_y2 = 50, 300, 200, 400
poly_x1, poly_y1, poly_x2, poly_y2 = 250, 300, 350, 400
line_points = [(line_x1, line_y1), (line_x2, line_y2)]
triangle_points = [(tri_x1, tri_y1), (tri_x2, tri_y1), (tri_x2, tri_y2)]
rectangle_points = [(rect_x1, rect_y1), (rect_x2, rect_y1), (rect_x2, rect_y2), (rect_x1, rect_y2)]
polygon_points = [
    (poly_x1, poly_y1),
    (poly_x2, poly_y1),
    (poly_x2, poly_y2),
    (poly_x1, poly_y2 - 50),
    (poly_x1, poly_y2 - 100),
]
frame_l = zdraw.ZDrawShape(frame.copy(), line_points, shape="line")
frame_t = zdraw.ZDrawShape(frame.copy(), triangle_points, shape="triangle")
frame_r = zdraw.ZDrawShape(frame.copy(), rectangle_points, shape="rectangle")
frame_p = zdraw.ZDrawShape(frame.copy(), polygon_points, shape="polygon")
original_frame, modified_frame = zdraw.ZDrawRect(frame.copy(), x1, y1, x2, y2, class_name, return_original_frame=True)

# Display the result
cv2.imshow("Original Frame", original_frame)
cv2.imshow("Modified Frame", modified_frame)
cv2.imshow("Modified Frame  Line", frame_l)
cv2.imshow("Modified Frame Triangle", frame_t)
cv2.imshow("Modified Frame Rectangle", frame_r)
cv2.imshow("Modified Frame Polygon", frame_p)
cv2.waitKey(0)
cv2.destroyAllWindows()