"""Turn the CVAT COCO export into PNG masks for the 71 labelled photos.

Labels stop at frame 71. The other 45 photos stay in dataset/images but
are left out of the labelled split lists. The original 70/20/10 lists stay
as they were committed; these *_labeled.txt files only keep the ones that
have both a card and a phone outline.
"""

import json
import os

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COCO = os.path.join(ROOT, "measure-it_annotations", "annotations", "instances_default.json")
MASK_DIR = os.path.join(ROOT, "dataset", "masks")
SPLIT_DIR = os.path.join(ROOT, "dataset", "splits")
# 0 background, 1 card, 2 phone
CLASS_ID = {"card": 1, "phone": 2}


def load_coco():
    with open(COCO) as handle:
        return json.load(handle)


def raster_mask(image_meta, annotations, categories):
    height = image_meta["height"]
    width = image_meta["width"]
    mask = np.zeros((height, width), np.uint8)
    for class_name, class_id in (("phone", CLASS_ID["phone"]), ("card", CLASS_ID["card"])):
        for ann in annotations:
            if categories[ann["category_id"]] != class_name:
                continue
            for poly in ann["segmentation"]:
                points = np.array(poly, np.float32).reshape(-1, 2)
                cv2.fillPoly(mask, [np.round(points).astype(np.int32)], class_id)
    return mask


def write_masks(data):
    os.makedirs(MASK_DIR, exist_ok=True)
    categories = {cat["id"]: cat["name"] for cat in data["categories"]}
    by_image = {}
    for ann in data["annotations"]:
        by_image.setdefault(ann["image_id"], []).append(ann)

    labeled = []
    for image in data["images"]:
        anns = by_image.get(image["id"], [])
        names = {categories[ann["category_id"]] for ann in anns}
        if names != {"card", "phone"}:
            continue
        mask = raster_mask(image, anns, categories)
        name = image["file_name"]
        out = os.path.join(MASK_DIR, os.path.splitext(name)[0] + ".png")
        cv2.imwrite(out, mask)
        labeled.append(name)
    return labeled


def write_labeled_splits(labeled):
    labeled_set = set(labeled)
    for split in ("train", "val", "test"):
        src = os.path.join(SPLIT_DIR, f"{split}.txt")
        kept = []
        with open(src) as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                name = os.path.basename(line)
                if name in labeled_set:
                    kept.append(line)
        out = os.path.join(SPLIT_DIR, f"{split}_labeled.txt")
        with open(out, "w") as handle:
            for line in kept:
                handle.write(line + "\n")
        print(f"{split}_labeled: {len(kept)}")
    with open(os.path.join(SPLIT_DIR, "labeled.txt"), "w") as handle:
        for name in sorted(labeled):
            handle.write(f"images/{name}\n")


def main():
    data = load_coco()
    labeled = write_masks(data)
    write_labeled_splits(labeled)
    print(f"masks: {len(labeled)}")


if __name__ == "__main__":
    main()
