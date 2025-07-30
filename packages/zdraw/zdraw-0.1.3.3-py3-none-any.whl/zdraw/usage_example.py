"""
Enhanced ZDrawRectCustom Usage Examples
======================================

This script demonstrates the enhanced features of ZDrawRectCustom function.
"""

import cv2
import numpy as np
from zdraw import ZDraw

def create_sample_frame():
    """Create a sample frame for demonstration."""
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    # Add some background pattern
    cv2.rectangle(frame, (0, 0), (800, 600), (40, 40, 40), -1)
    return frame

def main():
    # Initialize ZDraw
    zdraw = ZDraw()
    frame = create_sample_frame()
    
    print("Enhanced ZDrawRectCustom Usage Examples")
    print("=" * 50)
    
    # Example 1: PPE Detection with Auto Positioning
    print("1. PPE Detection with Auto Positioning")
    frame = zdraw.ZDrawRectCustom(
        frame, 50, 50, 250, 300,
        main_class="person",
        sub_labels=["helmet", "safety_vest", "steel_boots"],
        label_position="auto"  # Automatically chooses best position
    )
    
    # Example 2: Violation Detection
    print("2. Violation Detection")
    frame = zdraw.ZDrawRectCustom(
        frame, 300, 100, 500, 350,
        main_class="person",
        sub_labels=["violator", "no_helmet"],
        label_position="auto"
    )
    
    # Example 3: Small bbox with long labels (text truncation)
    print("3. Text Truncation for Long Labels")
    frame = zdraw.ZDrawRectCustom(
        frame, 550, 50, 650, 150,
        main_class="very_long_class_name_that_will_be_truncated",
        sub_labels=["extremely_long_sublabel_name"],
        label_position="auto"
    )
    
    # Example 4: Different positioning options
    print("4. Manual Positioning Options")
    
    # Inside positioning
    frame = zdraw.ZDrawRectCustom(
        frame, 50, 400, 150, 550,
        main_class="inside",
        sub_labels=["label1", "label2"],
        label_position="inside"
    )
    
    # Outside top positioning
    frame = zdraw.ZDrawRectCustom(
        frame, 200, 400, 300, 550,
        main_class="outside_top",
        sub_labels=["label1"],
        label_position="outside_top"
    )
    
    # Outside right positioning
    frame = zdraw.ZDrawRectCustom(
        frame, 350, 400, 450, 550,
        main_class="outside_right",
        sub_labels=["label1"],
        label_position="outside_right"
    )
    
    # Example 5: Edge case - bbox near frame boundaries
    print("5. Edge Case Handling")
    frame = zdraw.ZDrawRectCustom(
        frame, 700, 10, 790, 100,
        main_class="edge_case",
        sub_labels=["boundary_test"],
        label_position="auto"  # Will automatically adjust position
    )
    
    # Save and display result
    cv2.imwrite("usage_example_result.jpg", frame)
    print("\nResult saved as: usage_example_result.jpg")
    
    # Display the result
    cv2.imshow("Enhanced ZDrawRectCustom Examples", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    print("\nKey Features Demonstrated:")
    print("✓ Dynamic font scaling based on frame and bbox size")
    print("✓ Smart auto-positioning (chooses best location)")
    print("✓ Text truncation for long labels")
    print("✓ Multiple positioning options")
    print("✓ Boundary checking and adjustment")
    print("✓ Dynamic spacing and padding")

if __name__ == "__main__":
    main()
