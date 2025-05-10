import cv2
import os
import random
import numpy as np
import hashlib
import string

COLORS = {
    'vang': (0, 255, 255),      # Vàng
    'tim': (128, 0, 128),       # Tím
    'xanh_blue': (255, 0, 0),   # Xanh dương
    'xanh_la': (0, 128, 0),     # Xanh lá
    'cam': (0, 165, 255)        # Cam
}

FONTS = [
    cv2.FONT_HERSHEY_SIMPLEX,
    cv2.FONT_HERSHEY_PLAIN,
    cv2.FONT_HERSHEY_DUPLEX,
    cv2.FONT_HERSHEY_COMPLEX,
    cv2.FONT_HERSHEY_TRIPLEX
]

def generate_random_filename(extension='png', length=6):
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    hash_object = hashlib.md5(random_string.encode())
    short_hash = hash_object.hexdigest()[:length]
    return f"{short_hash}.{extension}"

def read_content_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} không tồn tại!")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    
    return lines

def save_path_to_file(file_path, absolute_path):
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f"{absolute_path}\n")

def get_random_image(folder_path):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder {folder_path} không tồn tại!")
    
    valid_extensions = ('.jpg', '.jpeg', '.png')
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]
    
    if not images:
        raise FileNotFoundError(f"Không có ảnh nào trong folder {folder_path}!")
    
    random_image = random.choice(images)
    return os.path.join(folder_path, random_image)

def get_random_color():
    return random.choice(list(COLORS.values()))

def get_appropriate_font_size(img, text, font):
    img_height, img_width = img.shape[:2]
    
    max_font_scale = 10.0
    min_font_scale = 0.3
    
    margin = 20
    target_width = img_width - (2 * margin)
    target_height = img_height - (2 * margin)
    
    left = min_font_scale
    right = max_font_scale
    
    while right - left > 0.01:
        mid = (left + right) / 2
        thickness = max(1, int(mid))
        (text_width, text_height), _ = cv2.getTextSize(text, font, mid, thickness)
        
        if text_width <= target_width and text_height <= target_height:
            left = mid
        else:
            right = mid
    
    return left

def get_random_thickness(font_scale):
    min_thickness = max(1, int(font_scale * 0.5))
    max_thickness = max(1, int(font_scale * 2))
    return random.randint(min_thickness, max_thickness)

def get_image_size(img):
    height, width = img.shape[:2]
    return width, height

def get_random_position(img, text, font, font_scale, thickness):
    img_width, img_height = get_image_size(img)
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    margin = 20
    max_x = max(margin, img_width - text_width - margin)
    max_y = img_height - margin
    min_y = text_height + margin
    if max_x <= margin or min_y >= max_y:
        x = margin
        y = img_height // 2
    else:
        x = random.randint(margin, max_x)
        y = random.randint(min_y, max_y)
    
    return (x, y)

def get_random_font():
    return random.choice(FONTS)

def add_random_text_to_image(image_path, text, output_path, max_attempts=5):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Không thể đọc ảnh: {image_path}")
    for attempt in range(max_attempts):
        try:
            font = get_random_font()
            font_scale = get_appropriate_font_size(img, text, font)
            font_scale *= random.uniform(0.6, 0.9)
            thickness = get_random_thickness(font_scale)
            color = get_random_color()
            position = get_random_position(img, text, font, font_scale, thickness)
            cv2.putText(img, text, position, font, font_scale, color, thickness)
            cv2.imwrite(output_path, img)
            
            return True
            
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            continue
    
    raise Exception("Không thể thêm text vào ảnh sau nhiều lần thử")

def process_content_file(content_file, images_folder, output_folder, path_file):
    lines = read_content_file(content_file)
    print(f"Đọc được {len(lines)} dòng nội dung")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if os.path.exists(path_file):
        os.remove(path_file)
    
    success_count = 0
    
    for i, line in enumerate(lines, 1):
        try:
            print(f"\nĐang xử lý dòng {i}/{len(lines)}: {line[:50]}...")
            random_image_path = get_random_image(images_folder)
            output_filename = generate_random_filename('png')
            output_path = os.path.join(output_folder, output_filename)
            success = add_random_text_to_image(random_image_path, line, output_path)
            if success:
                absolute_path = os.path.abspath(output_path)
                save_path_to_file(path_file, absolute_path)
                
                success_count += 1
                print(f"✓ Đã tạo: {absolute_path}")
            
        except Exception as e:
            print(f"✗ Lỗi khi xử lý dòng {i}: {e}")
            continue
    
    return success_count

if __name__ == "__main__":
    content_file = 'noidung.txt'
    images_folder = 'images'
    output_folder = 'output'
    path_file = 'path_images.txt'
    
    try:
        success_count = process_content_file(content_file, images_folder, output_folder, path_file)
        
        print(f"\n=== KẾT QUẢ ===")
        print(f"Đã xử lý {success_count} ảnh thành công")
        print(f"Tất cả đường dẫn đã được lưu vào: {path_file}")
        
        print(f"\nMột số đường dẫn ảnh đã tạo:")
        if os.path.exists(path_file):
            with open(path_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:3], 1):
                    print(f"{i}. {line.strip()}")
                if len(lines) > 3:
                    print(f"... và {len(lines) - 3} ảnh khác")
        
        print(f"\nBạn có thể copy các đường dẫn từ file '{path_file}' và paste vào File Explorer để mở ảnh.")
            
    except Exception as e:
        print(f"Lỗi: {e}")