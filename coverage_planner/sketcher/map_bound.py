"""Interactive field boundary mapping tool using OpenCV.

This module provides an interactive GUI for manually defining field boundaries
by clicking points on a field reference image. The polygon points are saved
for use in field coverage planning.
"""

import cv2

# Global variables for mouse event handling
points = []  # List to store polygon vertices
img = None   # Current display image


def click_event(event, x, y, flags, param):
    """Handle mouse click events for point selection.

    Args:
        event: OpenCV mouse event type
        x, y: Pixel coordinates of the mouse click
        flags: OpenCV mouse event flags
        param: Additional parameters (unused)
    """
    global points, img

    if event == cv2.EVENT_LBUTTONDOWN:
        # Add the clicked point to the polygon
        points.append((x, y))

        # Draw a red circle at the clicked point
        cv2.circle(img, (x, y), 5, (0, 0, 255), -1)

        # Draw a green line connecting to the previous point
        if len(points) > 1:
            cv2.line(img, points[-2], points[-1], (0, 255, 0), 2)

        # Update the display
        cv2.imshow("Field Selector", img)


def main():
    """Main function to run the interactive field boundary tool."""
    global points, img

    # Load the field reference image
    img = cv2.imread("media/field_reference-3.png")
    if img is None:
        print("Error: Could not load field reference image.")
        return

    clone = img.copy()

    # Display the image and set up mouse callback
    cv2.imshow("Field Selector", img)
    cv2.setMouseCallback("Field Selector", click_event)

    print("\nField Boundary Mapper")
    print("Instructions:")
    print("  - Click points on the image to define the field boundary")
    print("  - Press 'q' to finish point selection")
    print()

    # Wait for user input
    while True:
        key = cv2.waitKey(1)

        # Exit on 'q' key press
        if key == ord('q'):
            break

    # Close the polygon by drawing a line from the last point to the first
    if len(points) > 2:
        cv2.line(img, points[-1], points[0], (255, 0, 0), 2)

    # Display results
    print("\nPolygon Points:")
    print(points)

    # Save polygon points to file for later use
    with open("research/polygon_points.txt", "w") as f:
        for point in points:
            f.write(f"{point[0]},{point[1]}\n")

    print("\nPolygon points saved to research/polygon_points.txt")

    # Display the final polygon
    cv2.imshow("Final Polygon", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

