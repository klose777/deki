import ultralytics
import cv2
from ultralytics import YOLO
import os
import glob
import argparse

def iou(box1, box2):
    # Convert normalized coordinates to (x1, y1, x2, y2)
    x1_1 = box1[0] - box1[2] / 2
    y1_1 = box1[1] - box1[3] / 2
    x2_1 = box1[0] + box1[2] / 2
    y2_1 = box1[1] + box1[3] / 2

    x1_2 = box2[0] - box2[2] / 2
    y1_2 = box2[1] - box2[3] / 2
    x2_2 = box2[0] + box2[2] / 2
    y2_2 = box2[1] + box2[3] / 2

    # Compute intersection
    xi1 = max(x1_1, x1_2)
    yi1 = max(y1_1, y1_2)
    xi2 = min(x2_1, x2_2)
    yi2 = min(y2_1, y2_2)
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

    # Compute union
    box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
    box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
    union_area = box1_area + box2_area - inter_area

    # Compute IoU
    iou_value = inter_area / union_area if union_area > 0 else 0
    return iou_value

def init():
    parser = argparse.ArgumentParser(description='Process YOLO inference and NMS on an image.')
    parser.add_argument('input_image', help='Path to the input image.')
    parser.add_argument('weights_file', help='Path to the YOLO weights file.')
    parser.add_argument('output_dir', nargs='?', default='./yolo_run', help='Output directory (optional).')
    args = parser.parse_args()

    # Ensure the output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Get the input image's base name and extension
    input_image_name = os.path.basename(args.input_image)
    base_name, ext = os.path.splitext(input_image_name)

    # Generate output image filenames
    output_image_name = f"{base_name}_yolo{ext}"
    updated_output_image_name = f"{base_name}_yolo_updated{ext}"

    # Print version info
    print(ultralytics.checks())

    # Load custom pretrained YOLO model
    model = YOLO(args.weights_file)

    # Perform inference
    results = model(source=args.input_image, 
                    save_txt=True, 
                    project=args.output_dir, 
                    name="yolo_labels_output",
                    exist_ok=True)

    # Save the initial inference image
    img = results[0].plot(font_size=2, line_width=1)
    output_image_path = os.path.join(args.output_dir, output_image_name)
    cv2.imwrite(output_image_path, img)
    print(f"Image saved as '{output_image_path}'")

    # Directory containing labels files
    labels_dir = os.path.join(args.output_dir, 'yolo_labels_output', 'labels')

    # Search for txt files whose filenames contain the original base name
    label_files = [
        f for f in glob.glob(os.path.join(labels_dir, '*.txt'))
        if base_name in os.path.basename(f)
    ]

    if not label_files:
        print(f"No label files found for the image '{base_name}'.")
        exit()
    
    label_file = label_files[0]

    with open(label_file, 'r') as f:
        lines = f.readlines()

    boxes = []
    for idx, line in enumerate(lines):
        tokens = line.strip().split()
        class_id = int(tokens[0])
        x_center = float(tokens[1])
        y_center = float(tokens[2])
        width = float(tokens[3])
        height = float(tokens[4])
        boxes.append({
            'class_id': class_id,
            'bbox': [x_center, y_center, width, height],
            'line': line,
            'index': idx
        })

    # sort by y-coordinate
    boxes.sort(key=lambda b: b['bbox'][1] - (b['bbox'][3] / 2))

    # Perform NMS
    keep_indices = []
    suppressed = [False] * len(boxes)
    num_removed = 0
    for i in range(len(boxes)):
        if suppressed[i]:
            continue
        keep_indices.append(i)
        for j in range(i + 1, len(boxes)):
            if suppressed[j]:
                continue
            if boxes[i]['class_id'] == boxes[j]['class_id']:
                iou_value = iou(boxes[i]['bbox'], boxes[j]['bbox'])
                if iou_value > 0.7:
                    suppressed[j] = True
                    num_removed += 1

    # Write the kept boxes back to the file
    with open(label_file, 'w') as f:
        for idx in keep_indices:
            f.write(boxes[idx]['line'])

    print(f"Number of bounding boxes removed: {num_removed}")

    # Create image with updated bounding boxes
    # Load the original image
    image_path = args.input_image
    image = cv2.imread(image_path)
    if image is None:
        print("Error loading image.")
        exit()

    height, width, _ = image.shape

    # Draw updated bounding boxes
    for i, idx in enumerate(keep_indices):
        box = boxes[idx]
        class_id = box['class_id']
        x_center, y_center, w, h = box['bbox']

        # Convert normalized coordinates to pixel coordinates
        x_center *= width
        y_center *= height
        w *= width
        h *= height

        x1 = int(x_center - w / 2)
        y1 = int(y_center - h / 2)
        x2 = int(x_center + w / 2)
        y2 = int(y_center + h / 2)

        # Draw rectangle
        color = (0, 255, 0)  # Green color for bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        # ultra marine color
        color = (143, 10, 18)
        # # Put class ID text
        # Put index
        font_scale = 0.3
        font_thickness = 1
        cv2.putText(
            image,
            str(i + 1),
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            font_thickness
        )


    # Save the updated image
    updated_output_image_path = os.path.join(args.output_dir, updated_output_image_name)
    cv2.imwrite(updated_output_image_path, image)
    print(f"Updated image saved as '{updated_output_image_path}'")

if __name__ == '__main__':
    init()
