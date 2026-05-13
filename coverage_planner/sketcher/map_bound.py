import cv2

points = []

img = cv2.imread("research/field.png")
clone = img.copy()

def click_event(event, x, y, flags, param):
    global points, img

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))

        # draw point
        cv2.circle(img, (x, y), 5, (0, 0, 255), -1)

        # draw line
        if len(points) > 1:
            cv2.line(img, points[-2], points[-1], (0, 255, 0), 2)

        cv2.imshow("Field Selector", img)

cv2.imshow("Field Selector", img)
cv2.setMouseCallback("Field Selector", click_event)

while True:
    key = cv2.waitKey(1)

    # press q to quit
    if key == ord('q'):
        break

# close polygon
if len(points) > 2:
    cv2.line(img, points[-1], points[0], (255, 0, 0), 2)

print("\nPolygon Points:")
print(points)

# Save points to file
with open("research/polygon_points.txt", "w") as f:
    for point in points:
        f.write(f"{point[0]},{point[1]}\n") 



cv2.imshow("Final Polygon", img)
cv2.waitKey(0)

cv2.destroyAllWindows()

