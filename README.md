# Plastic Waste Image Annotation & RGB Mask Generation Pipeline

This project covers the complete dataset annotation and mask generation pipeline for plastic waste segmentation. It includes task setup in CVAT, COCO 1.0 JSON export, programmatic conversion of polygon segmentations into multi-class RGB masks, and final submission packaging for Google Drive.

---

## 1. Class Definitions & Color Palette

All annotations strictly follow the 6 defined classes with their respective exact RGB hex codes:

| Class Name | CVAT Label | Hex Code | RGB Tuple | Visual Representation |
| :--- | :--- | :--- | :--- | :--- |
| **Bottle** | `Bottle` | `#FF0000` | `(255, 0, 0)` | Red |
| **Bottle Cap** | `Bottle Cap` | `#FF9900` | `(255, 153, 0)` | Orange |
| **Wrapper** | `Wrapper` | `#FFFF00` | `(255, 255, 0)` | Yellow |
| **Polythene** | `Polythene` | `#00CC00` | `(0, 204, 0)` | Green |
| **Shoe, Jacket** | `Shoe, Jacket` | `#0099FF` | `(0, 153, 255)` | Blue |
| **Foam** | `Foam` | `#FF66FF` | `(255, 102, 255)` | Violet |

*Note: Background pixels are rendered as solid black `(0, 0, 0)` (`#000000`).*

---

## 2. Directory Structure

```text
cvat_project/
├── instances_default.json         # Raw exported COCO 1.0 file from CVAT (untouched)
├── create_masks.py                # Processing and mask generation script
├── README.md                      # Pipeline documentation
└── drive_submission/              # Generated automatically by create_masks.py
    ├── json/
    │   └── <ENROLMENT_NO>_annotations.json
    └── rgb_images/
        ├── image_01.png
        ├── image_02.png
        └── ... (all 60 PNG mask images matching original dimensions)
```

---

## 3. Prerequisites & macOS Environment Setup

This project requires **Python 3.8+** and the **Pillow** imaging library.

### Setting Up on macOS

If running `pip` directly returns `command not found: pip` or hits an `externally-managed-environment` error, set up an isolated virtual environment:

1. **Open Terminal** and navigate to your project directory:
   ```bash
   cd /path/to/cvat_project
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   *(Your terminal prompt will now show `(venv)` at the beginning).*

3. **Install dependencies:**
   ```bash
   pip install Pillow
   ```
   *(Alternatively, if running without a virtual environment: `python3 -m pip install Pillow`)*

---

## 4. Workflow & Execution

### Step 1: Annotation in CVAT
1. All 60 allotted images are imported into a CVAT task.
2. The 6 polygon classes are created with exact casing, spacing, and hex codes.
3. Every plastic object is traced strictly with the **Polygon tool** (`N`).
4. Labels are assigned using shortcuts (`Control + 1` through `Control + 6`).

### Step 2: Dataset Export
1. In CVAT: **Actions** $\rightarrow$ **Export task dataset**.
2. Select format: **`COCO 1.0`**.
3. Ensure **"Save images" is UNCHECKED** (exports annotations only).
4. Extract the downloaded zip file and place `instances_default.json` inside your working folder.
5. Keep the JSON file untouched; do not edit it manually.

### Step 3: RGB Mask Generation
1. Configure your enrollment number in `create_masks.py`:
   ```python
   ENROLMENT_NO = "YOUR_ENROLMENT_NUMBER"
   ```
2. Execute the conversion script:
   ```bash
   python3 create_masks.py
   ```
3. The script will:
   - Validate categories against the allowed 6-class schema.
   - Verify polygon coordinate integrity.
   - Draw filled polygons onto a black canvas `(0, 0, 0)` matching original image dimensions.
   - Save masks as lossless `.png` files under `drive_submission/rgb_images/`.
   - Copy and rename the exported JSON to `drive_submission/json/<ENROLMENT_NO>_annotations.json`.
   - Run an automated audit checking for 60 output files and warning about any unannotated frames.

---

## 5. Submission Checklist (Google Drive)

Before uploading to your assigned Google Drive folder, verify:

- [ ] `json/` contains exactly one file named `<ENROLMENT_NO>_annotations.json`.
- [ ] The JSON content is identical to the CVAT export (unmodified).
- [ ] `rgb_images/` contains exactly **60 PNG files**.
- [ ] Mask file names match the original image stems (e.g., `IMG_001.jpg` $\rightarrow$ `IMG_001.png`).
- [ ] Masks maintain identical width and height as source images.
- [ ] Folder names are strictly in lowercase: `json` and `rgb_images`.
- [ ] Polygons are cleanly filled with the assigned hex colors against a black background.