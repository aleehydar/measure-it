"""Undistort the card photos and write the fixed 70/20/10 split.

Portrait frames are turned sideways to match the landscape calibration,
undistorted, then turned back. The split is written once and committed
before any training.
"""

import glob
import os

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "dataset", "raw")
OUT_DIR = os.path.join(ROOT, "dataset", "images")
SPLIT_DIR = os.path.join(ROOT, "dataset", "splits")
CAMERA = os.path.join(ROOT, "calibration", "camera.npz")
SEED = 7
CALIB_SIZE = (1280, 960)


def undistort_one(image, camera_matrix, dist_coeffs):
    height, width = image.shape[:2]
    if (width, height) == CALIB_SIZE:
        return cv2.undistort(image, camera_matrix, dist_coeffs)
    if (width, height) == (CALIB_SIZE[1], CALIB_SIZE[0]):
        turned = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        straight = cv2.undistort(turned, camera_matrix, dist_coeffs)
        return cv2.rotate(straight, cv2.ROTATE_90_COUNTERCLOCKWISE)
    raise ValueError(f"unexpected size {width}x{height}")


def write_images():
    os.makedirs(OUT_DIR, exist_ok=True)
    data = np.load(CAMERA)
    camera_matrix = data["camera_matrix"]
    dist_coeffs = data["dist_coeffs"]
    paths = sorted(glob.glob(os.path.join(RAW_DIR, "*")))
    names = []
    for path in paths:
        image = cv2.imread(path)
        if image is None:
            raise SystemExit(f"could not read {path}")
        straight = undistort_one(image, camera_matrix, dist_coeffs)
        name = os.path.splitext(os.path.basename(path))[0] + ".jpg"
        cv2.imwrite(os.path.join(OUT_DIR, name), straight, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        names.append(name)
    return names


def write_split(names):
    os.makedirs(SPLIT_DIR, exist_ok=True)
    rng = np.random.default_rng(SEED)
    order = list(names)
    rng.shuffle(order)
    n = len(order)
    n_train = int(round(n * 0.70))
    n_val = int(round(n * 0.20))
    train = order[:n_train]
    val = order[n_train:n_train + n_val]
    test = order[n_train + n_val:]
    for label, group in ("train", train), ("val", val), ("test", test):
        path = os.path.join(SPLIT_DIR, f"{label}.txt")
        with open(path, "w") as handle:
            for name in group:
                handle.write(f"images/{name}\n")
    return len(train), len(val), len(test)


def main():
    names = write_images()
    counts = write_split(names)
    print(f"images: {len(names)}")
    print(f"train/val/test: {counts[0]}/{counts[1]}/{counts[2]}")
    print(f"seed: {SEED}")


if __name__ == "__main__":
    main()
