"""Eval the saved weights on the labelled test split."""

import os
import sys

import numpy as np
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train import (  # noqa: E402
    BATCH,
    OUT_DIR,
    SPLIT_DIR,
    CardPhoneSet,
    build_model,
    class_iou,
    read_split,
)


def main():
    weights = os.path.join(OUT_DIR, "best.pt")
    ckpt = torch.load(weights, map_location="cpu", weights_only=False)
    model = build_model()
    model.load_state_dict(ckpt["model"])
    model.eval()

    names = read_split(os.path.join(SPLIT_DIR, "test_labeled.txt"))
    loader = DataLoader(CardPhoneSet(names, train=False), batch_size=BATCH, shuffle=False)

    totals = [0.0, 0.0, 0.0]
    counts = [0, 0, 0]
    rows = []
    with torch.inference_mode():
        for images, targets, batch_names in loader:
            out = model(images)["out"]
            pred = out.argmax(1)
            for b in range(images.size(0)):
                ious = class_iou(pred[b], targets[b])
                for i, value in enumerate(ious):
                    if not np.isnan(value):
                        totals[i] += value
                        counts[i] += 1
                rows.append((batch_names[b], ious[1], ious[2]))

    mean = [totals[i] / counts[i] if counts[i] else float("nan") for i in range(3)]
    print(f"test images: {len(names)}")
    print(f"IoU background: {mean[0]:.4f}")
    print(f"IoU card:       {mean[1]:.4f}")
    print(f"IoU phone:      {mean[2]:.4f}")
    print(f"checkpoint epoch {ckpt.get('epoch')} val card IoU {ckpt.get('card_iou'):.4f}")
    out_path = os.path.join(OUT_DIR, "test_metrics.txt")
    with open(out_path, "w") as handle:
        handle.write(f"n={len(names)}\n")
        handle.write(f"iou_bg={mean[0]:.6f}\n")
        handle.write(f"iou_card={mean[1]:.6f}\n")
        handle.write(f"iou_phone={mean[2]:.6f}\n")
        handle.write("name iou_card iou_phone\n")
        for name, card, phone in rows:
            handle.write(f"{name} {card:.6f} {phone:.6f}\n")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
