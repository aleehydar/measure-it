"""One photo in, card width and height in millimetres out.

Uses the phone body as the scale (GSMArena 165.7 mm by 77.1 mm).
The card answer is compared later against ISO ID-1 85.60 mm by 53.98 mm.
"""

import argparse
import os
import sys

import cv2
import numpy as np
import torch

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "train"))
from train import MEAN, NUM_CLASSES, STD, TRAIN_SIZE, build_model, letterbox  # noqa: E402

CAMERA = os.path.join(ROOT, "calibration", "camera.npz")
WEIGHTS = os.path.join(ROOT, "train", "runs", "best.pt")
CALIB_SIZE = (1280, 960)
PHONE_LONG_MM = 165.7
PHONE_SHORT_MM = 77.1
CARD_CLASS = 1
PHONE_CLASS = 2


def undistort(image, camera_matrix, dist_coeffs):
    height, width = image.shape[:2]
    if (width, height) == CALIB_SIZE:
        return cv2.undistort(image, camera_matrix, dist_coeffs)
    if (width, height) == (CALIB_SIZE[1], CALIB_SIZE[0]):
        turned = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        straight = cv2.undistort(turned, camera_matrix, dist_coeffs)
        return cv2.rotate(straight, cv2.ROTATE_90_COUNTERCLOCKWISE)
    raise SystemExit(f"unexpected size {width}x{height}; expected 1280x960 or 960x1280")


def load_model(path, device):
    if not os.path.isfile(path):
        raise SystemExit(f"missing weights {path}")
    ckpt = torch.load(path, map_location=device, weights_only=False)
    model = build_model()
    model.load_state_dict(ckpt["model"])
    model.to(device)
    model.eval()
    return model, ckpt


def predict_mask(model, image_bgr, device):
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]
    blank = np.zeros((h, w), np.uint8)
    boxed, _ = letterbox(rgb, blank, TRAIN_SIZE)
    tensor = boxed.astype(np.float32) / 255.0
    tensor = (tensor - MEAN) / STD
    tensor = torch.from_numpy(tensor.transpose(2, 0, 1)).float().unsqueeze(0).to(device)
    with torch.inference_mode():
        logits = model(tensor)["out"][0]
        pred = logits.argmax(0).cpu().numpy().astype(np.uint8)

    # undo letterbox back to original size
    out_w, out_h = TRAIN_SIZE
    scale = min(out_w / w, out_h / h)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    x0 = (out_w - new_w) // 2
    y0 = (out_h - new_h) // 2
    crop = pred[y0 : y0 + new_h, x0 : x0 + new_w]
    return cv2.resize(crop, (w, h), interpolation=cv2.INTER_NEAREST)


def largest_mask(mask, class_id):
    binary = (mask == class_id).astype(np.uint8)
    if binary.sum() < 100:
        return None
    num, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    if num <= 1:
        return None
    areas = stats[1:, cv2.CC_STAT_AREA]
    best = 1 + int(np.argmax(areas))
    return (labels == best).astype(np.uint8)


def side_lengths(binary):
    ys, xs = np.where(binary > 0)
    points = np.stack([xs, ys], axis=1).astype(np.float32)
    rect = cv2.minAreaRect(points)
    a, b = rect[1]
    if a < 1 or b < 1:
        return None
    return max(a, b), min(a, b)


def measure_mm(card, phone):
    phone_sides = side_lengths(phone)
    card_sides = side_lengths(card)
    if phone_sides is None:
        raise SystemExit("phone not found")
    if card_sides is None:
        raise SystemExit("card not found")
    phone_long, phone_short = phone_sides
    card_long, card_short = card_sides
    mm_per_px = 0.5 * (PHONE_LONG_MM / phone_long + PHONE_SHORT_MM / phone_short)
    # long side reported as width, short as height (ID-1 style)
    width_mm = card_long * mm_per_px
    height_mm = card_short * mm_per_px
    phone_conf = float(phone.sum()) / phone.size
    card_conf = float(card.sum()) / card.size
    return width_mm, height_mm, card_conf, phone_conf


def main():
    parser = argparse.ArgumentParser(description="Measure Meezan card width and height in mm")
    parser.add_argument("image", help="path to a photo (WhatsApp size 1280x960 or 960x1280)")
    parser.add_argument("--weights", default=WEIGHTS)
    parser.add_argument("--no-undistort", action="store_true", help="skip undistort (already straight)")
    args = parser.parse_args()

    image = cv2.imread(args.image)
    if image is None:
        raise SystemExit(f"could not read {args.image}")

    if not args.no_undistort:
        data = np.load(CAMERA)
        image = undistort(image, data["camera_matrix"], data["dist_coeffs"])

    device = torch.device("cpu")
    model, _ = load_model(args.weights, device)
    mask = predict_mask(model, image, device)
    card = largest_mask(mask, CARD_CLASS)
    phone = largest_mask(mask, PHONE_CLASS)
    if phone is None:
        raise SystemExit("phone not found")
    if card is None:
        raise SystemExit("card not found")

    width_mm, height_mm, card_conf, phone_conf = measure_mm(card, phone)
    print(f"width_mm={width_mm:.2f}")
    print(f"height_mm={height_mm:.2f}")
    print(f"card_mask_fraction={card_conf:.4f}")
    print(f"phone_mask_fraction={phone_conf:.4f}")


if __name__ == "__main__":
    main()
