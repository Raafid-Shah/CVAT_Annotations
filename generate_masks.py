import json
import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw

# ==========================================
# CONFIGURATION (Update these 2 variables)
# ==========================================
ENROLMENT_NO = "2023BCSE030"  # Replace with your actual enrolment number
INPUT_JSON_PATH = "instances_default.json"  # Path to your CVAT exported COCO JSON
OUTPUT_DIR = "drive_upload_ready"  # Folder that will hold 'json/' and 'rgb_images/'

# Strict mapping from your assignment table
CLASS_COLOR_MAP = {
    "Bottle": "#FF0000",
    "Bottle Cap": "#FF9900",
    "Wrapper": "#FFFF00",
    "Polythene": "#00CC00",
    "Shoe, Jacket": "#0099FF",
    "Foam": "#FF66FF"
}

def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Converts '#FF9900' to (255, 153, 0) tuple."""
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def generate_rgb_masks(json_path: str, output_base: str, enrolment_no: str):
    # 1. Create exact required directory structure (Step 4)
    json_out_dir = Path(output_base) / "json"
    rgb_out_dir = Path(output_base) / "rgb_images"
    json_out_dir.mkdir(parents=True, exist_ok=True)
    rgb_out_dir.mkdir(parents=True, exist_ok=True)

    # 2. Copy and rename the JSON file without modifying its contents
    target_json_name = f"{enrolment_no}_annotations.json"
    shutil.copy2(json_path, json_out_dir / target_json_name)
    print(f"[✓] Copied untouched JSON to: {json_out_dir / target_json_name}")

    # 3. Load COCO JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        coco_data = json.load(f)

    # 4. Validate Categories against strict assignment rules
    cat_id_to_color = {}
    cat_id_to_name = {}
    for cat in coco_data.get("categories", []):
        name = cat["name"]
        cat_id = cat["id"]
        if name not in CLASS_COLOR_MAP:
            raise ValueError(
                f"[CRITICAL ERROR] Invalid label found in JSON: '{name}'. "
                f"Allowed labels are strictly: {list(CLASS_COLOR_MAP.keys())}"
            )
        cat_id_to_color[cat_id] = hex_to_rgb(CLASS_COLOR_MAP[name])
        cat_id_to_name[cat_id] = name

    # 5. Group annotations by image_id for fast lookup
    annotations_by_image = {}
    for ann in coco_data.get("annotations", []):
        img_id = ann["image_id"]
        annotations_by_image.setdefault(img_id, []).append(ann)

    images = coco_data.get("images", [])
    print(f"[*] Found {len(images)} images in COCO JSON. Generating masks...")

    blank_images = []

    # 6. Render each mask
    for img_info in images:
        img_id = img_info["id"]
        file_name = os.path.basename(img_info["file_name"])
        width = img_info["width"]
        height = img_info["height"]

        # Create black RGB background: (0, 0, 0)
        mask = Image.new("RGB", (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(mask)

        anns = annotations_by_image.get(img_id, [])
        if not anns:
            blank_images.append(file_name)

        for ann in anns:
            cat_id = ann["category_id"]
            color = cat_id_to_color[cat_id]
            segmentation = ann.get("segmentation", [])

            # Check if someone accidentally used RLE/brush instead of polygon
            if not isinstance(segmentation, list):
                raise TypeError(
                    f"[ERROR] Image '{file_name}' (Annotation ID {ann['id']}) uses RLE/Brush "
                    f"instead of a Polygon! Redraw it in CVAT with the Polygon tool."
                )

            # Each segmentation list can contain 1 or more polygon parts [x1, y1, x2, y2, ...]
            for poly in segmentation:
                if len(poly) >= 6:  # Needs at least 3 (x, y) points to form a polygon
                    xy_coords = [(poly[i], poly[i + 1]) for i in range(0, len(poly), 2)]
                    draw.polygon(xy_coords, fill=color, outline=color)

        # Save as PNG with the same base filename
        base_name = os.path.splitext(file_name)[0]
        out_mask_path = rgb_out_dir / f"{base_name}.png"
        mask.save(out_mask_path, format="PNG")

    # 7. Final Audit Report
    print("\n================ AUDIT REPORT ================")
    print(f"Total Images Processed : {len(images)} (Expected: 60)")
    print(f"Masks Saved To         : {rgb_out_dir.resolve()}")
    
    if len(images) != 60:
        print(f"[WARNING] Image count is {len(images)}, not 60! Check your CVAT task.")
        
    if blank_images:
        print(f"[WARNING] {len(blank_images)} image(s) have ZERO annotations (Penalized by rubric!):")
        for b_img in blank_images:
            print(f"  - {b_img}")
    else:
        print("[✓] All images have at least 1 polygon annotation.")
    print("==============================================")

if __name__ == "__main__":
    generate_rgb_masks(INPUT_JSON_PATH, OUTPUT_DIR, ENROLMENT_NO)