"""Fine-tune DeepLabV3 MobileNet on the labelled card/phone masks.

Train list is dataset/splits/train_labeled.txt. Val picks the checkpoint.
Test stays untouched until eval. CPU only on this ProBook.
"""

import os
import time

import cv2
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision.models.segmentation import deeplabv3_mobilenet_v3_large
from torchvision.models.segmentation.deeplabv3 import DeepLabHead
from torchvision.models.segmentation.fcn import FCNHead

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(ROOT, "dataset", "images")
MASK_DIR = os.path.join(ROOT, "dataset", "masks")
SPLIT_DIR = os.path.join(ROOT, "dataset", "splits")
OUT_DIR = os.path.join(ROOT, "train", "runs")
NUM_CLASSES = 3  # background, card, phone
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
# short side / long side target so CPU training finishes in time
TRAIN_SIZE = (384, 288)  # (width, height) for landscape; portrait keeps aspect via letterbox
EPOCHS = 25
BATCH = 2
LR = 3e-4
SEED = 7


def read_split(path):
    names = []
    with open(path) as handle:
        for line in handle:
            line = line.strip()
            if line:
                names.append(os.path.basename(line))
    return names


def letterbox(image, mask, size):
    """Resize keeping aspect, pad to size=(w,h). Mask uses nearest."""
    out_w, out_h = size
    h, w = image.shape[:2]
    scale = min(out_w / w, out_h / h)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    mask = cv2.resize(mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
    canvas_img = np.zeros((out_h, out_w, 3), dtype=np.uint8)
    canvas_mask = np.zeros((out_h, out_w), dtype=np.uint8)
    x0 = (out_w - new_w) // 2
    y0 = (out_h - new_h) // 2
    canvas_img[y0 : y0 + new_h, x0 : x0 + new_w] = image
    canvas_mask[y0 : y0 + new_h, x0 : x0 + new_w] = mask
    return canvas_img, canvas_mask


class CardPhoneSet(Dataset):
    def __init__(self, names, train=False):
        self.names = names
        self.train = train

    def __len__(self):
        return len(self.names)

    def __getitem__(self, index):
        name = self.names[index]
        image = cv2.imread(os.path.join(IMAGE_DIR, name))
        if image is None:
            raise FileNotFoundError(name)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mask_name = os.path.splitext(name)[0] + ".png"
        mask = cv2.imread(os.path.join(MASK_DIR, mask_name), cv2.IMREAD_GRAYSCALE)
        if mask is None:
            raise FileNotFoundError(mask_name)

        if self.train:
            if np.random.rand() < 0.5:
                image = np.ascontiguousarray(image[:, ::-1])
                mask = np.ascontiguousarray(mask[:, ::-1])
            # small brightness jitter
            alpha = 0.85 + 0.3 * np.random.rand()
            image = np.clip(image.astype(np.float32) * alpha, 0, 255).astype(np.uint8)

        image, mask = letterbox(image, mask, TRAIN_SIZE)
        tensor = image.astype(np.float32) / 255.0
        tensor = (tensor - MEAN) / STD
        tensor = torch.from_numpy(tensor.transpose(2, 0, 1)).float()
        target = torch.from_numpy(mask.astype(np.int64))
        return tensor, target, name


def build_model():
    model = deeplabv3_mobilenet_v3_large(weights="DEFAULT")
    model.classifier = DeepLabHead(960, NUM_CLASSES)
    model.aux_classifier = FCNHead(40, NUM_CLASSES)
    return model


def class_iou(pred, target, num_classes=NUM_CLASSES):
    pred = pred.view(-1)
    target = target.view(-1)
    ious = []
    for cls in range(num_classes):
        p = pred == cls
        t = target == cls
        inter = (p & t).sum().item()
        union = (p | t).sum().item()
        if union == 0:
            ious.append(float("nan"))
        else:
            ious.append(inter / union)
    return ious


def evaluate(model, loader, device):
    model.eval()
    totals = [0.0, 0.0, 0.0]
    counts = [0, 0, 0]
    loss_sum = 0.0
    n = 0
    criterion = nn.CrossEntropyLoss()
    with torch.inference_mode():
        for images, targets, _ in loader:
            images = images.to(device)
            targets = targets.to(device)
            out = model(images)["out"]
            loss_sum += criterion(out, targets).item() * images.size(0)
            n += images.size(0)
            pred = out.argmax(1)
            for b in range(images.size(0)):
                ious = class_iou(pred[b].cpu(), targets[b].cpu())
                for i, value in enumerate(ious):
                    if not np.isnan(value):
                        totals[i] += value
                        counts[i] += 1
    mean_ious = [totals[i] / counts[i] if counts[i] else float("nan") for i in range(3)]
    return loss_sum / max(n, 1), mean_ious


def main():
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    os.makedirs(OUT_DIR, exist_ok=True)
    device = torch.device("cpu")

    train_names = read_split(os.path.join(SPLIT_DIR, "train_labeled.txt"))
    val_names = read_split(os.path.join(SPLIT_DIR, "val_labeled.txt"))
    print(f"train {len(train_names)} val {len(val_names)} size {TRAIN_SIZE} epochs {EPOCHS}")

    train_loader = DataLoader(
        CardPhoneSet(train_names, train=True),
        batch_size=BATCH,
        shuffle=True,
        num_workers=0,
        # DeepLab ASPP BatchNorm needs more than one sample in the batch
        drop_last=True,
    )
    val_loader = DataLoader(
        CardPhoneSet(val_names, train=False),
        batch_size=BATCH,
        shuffle=False,
        num_workers=0,
    )

    model = build_model().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

    best_card_iou = -1.0
    best_path = os.path.join(OUT_DIR, "best.pt")
    log_path = os.path.join(OUT_DIR, "train_log.txt")
    started = time.time()

    with open(log_path, "w") as log:
        log.write("epoch train_loss val_loss iou_bg iou_card iou_phone\n")
        for epoch in range(1, EPOCHS + 1):
            model.train()
            running = 0.0
            seen = 0
            for images, targets, _ in train_loader:
                images = images.to(device)
                targets = targets.to(device)
                optimizer.zero_grad(set_to_none=True)
                out = model(images)
                loss = criterion(out["out"], targets)
                if out.get("aux") is not None:
                    loss = loss + 0.4 * criterion(out["aux"], targets)
                loss.backward()
                optimizer.step()
                running += loss.item() * images.size(0)
                seen += images.size(0)
            scheduler.step()
            train_loss = running / max(seen, 1)
            val_loss, ious = evaluate(model, val_loader, device)
            line = (
                f"{epoch:02d} train={train_loss:.4f} val={val_loss:.4f} "
                f"iou bg={ious[0]:.3f} card={ious[1]:.3f} phone={ious[2]:.3f} "
                f"({time.time() - started:.0f}s)"
            )
            print(line)
            log.write(
                f"{epoch} {train_loss:.6f} {val_loss:.6f} "
                f"{ious[0]:.6f} {ious[1]:.6f} {ious[2]:.6f}\n"
            )
            log.flush()
            if ious[1] > best_card_iou:
                best_card_iou = ious[1]
                torch.save(
                    {
                        "model": model.state_dict(),
                        "epoch": epoch,
                        "card_iou": best_card_iou,
                        "num_classes": NUM_CLASSES,
                        "train_size": TRAIN_SIZE,
                        "mean": MEAN.tolist(),
                        "std": STD.tolist(),
                    },
                    best_path,
                )
                print(f"  saved best card IoU {best_card_iou:.3f}")

    print(f"best card IoU {best_card_iou:.3f}")
    print(f"weights {best_path}")
    print(f"elapsed {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
