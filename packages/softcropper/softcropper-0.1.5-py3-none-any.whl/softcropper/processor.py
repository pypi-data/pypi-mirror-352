import cv2
import numpy as np
import os
import argparse

def make_square(image):
    height, width = image.shape[:2]
    size = max(height, width)
    square_image = np.zeros((size, size, 3), dtype=np.uint8)
    x_offset = (size - width) // 2
    y_offset = (size - height) // 2
    square_image[y_offset:y_offset + height, x_offset:x_offset + width] = image
    return square_image, x_offset, y_offset, size

def add_borders(image, original_image, x_offset, y_offset, mode="blur"):
    height, width = image.shape[:2]
    final_image = image.copy()

    if mode == "solid" or mode == "gradient":
        avg_color = original_image.mean(axis=(0, 1)).astype(np.uint8)

        if mode == "solid":
            # Fill with a single color
            if x_offset > 0:
                final_image[:, :x_offset] = avg_color
                final_image[:, -x_offset:] = avg_color
            if y_offset > 0:
                final_image[:y_offset, :] = avg_color
                final_image[-y_offset:, :] = avg_color

        elif mode == "gradient":
            # Left & right gradient
            if x_offset > 0:
                for i in range(x_offset):
                    alpha = i / x_offset
                    color = (avg_color * alpha).astype(np.uint8)
                    final_image[:, i] = color
                    final_image[:, -i - 1] = color

            # Top & bottom gradient
            if y_offset > 0:
                for j in range(y_offset):
                    alpha = j / y_offset
                    color = (avg_color * alpha).astype(np.uint8)
                    final_image[j, :] = color
                    final_image[-j - 1, :] = color

    else:
        # Blur mode (default)
        border_width = max(30, original_image.shape[1] // 10)
        border_height = max(30, original_image.shape[0] // 10)
        blur_amount = 51

        if x_offset > 0:
            left_border = original_image[:, :border_width]
            right_border = original_image[:, -border_width:]
            left_expanded = cv2.resize(left_border, (x_offset, height), interpolation=cv2.INTER_CUBIC)
            right_expanded = cv2.resize(right_border, (x_offset, height), interpolation=cv2.INTER_CUBIC)
            final_image[:, :x_offset] = cv2.GaussianBlur(left_expanded, (blur_amount, blur_amount), 0)
            final_image[:, -x_offset:] = cv2.GaussianBlur(right_expanded, (blur_amount, blur_amount), 0)

        if y_offset > 0:
            top_border = original_image[:border_height, :]
            bottom_border = original_image[-border_height:, :]
            top_expanded = cv2.resize(top_border, (width, y_offset), interpolation=cv2.INTER_CUBIC)
            bottom_expanded = cv2.resize(bottom_border, (width, y_offset), interpolation=cv2.INTER_CUBIC)
            final_image[:y_offset, :] = cv2.GaussianBlur(top_expanded, (blur_amount, blur_amount), 0)
            final_image[-y_offset:, :] = cv2.GaussianBlur(bottom_expanded, (blur_amount, blur_amount), 0)

    return final_image

def process_images(input_folder, output_folder=None, mode="blur"):
    if output_folder is None:
        output_folder = os.path.join(input_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    total_images = 0
    processed_images = 0
    skipped_images = 0

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('png', 'jpg', 'jpeg', 'webp')):
            total_images += 1
            image_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            image = cv2.imread(image_path)
            if image is None:
                skipped_images += 1
                print(f"⚠️ Skipped: {filename} (unreadable or corrupted)")
                continue
            squared_image, x_offset, y_offset, _ = make_square(image)
            final_image = add_borders(squared_image, image, x_offset, y_offset, mode=mode)
            cv2.imwrite(output_path, final_image)
            processed_images += 1
            print(f"✅ Processed: {filename}")

    print("\n📦 Processing Complete")
    print(f"🔢 Total images found: {total_images}")
    print(f"✅ Successfully processed: {processed_images}")
    print(f"⛔ Skipped (unreadable): {skipped_images}")
    print(f"📁 Output folder: {output_folder}")
    