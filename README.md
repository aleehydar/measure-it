# Measure It

Measure a Meezan debit card in millimetres from a photo.

Camera: my brother's iPhone XR, main camera, zoom locked.
Object: my brother's Meezan debit card. Full-size card, ISO ID-1, 85.60 mm by 53.98 mm. Not measured with a ruler.
Reference: my Infinix Smart 9, lying flat next to the card. Body size from GSMArena, 165.7 mm by 77.1 mm. No case.

Labels stop at 71 photos. The rest of the 116 frames are in `dataset/images` but unused for training.

## Run

```bash
python3 measure.py path/to/photo.jpg
```

Photo size must match the calibration: 1280×960 or 960×1280. The command undistorts, segments card and phone, scales from the phone body, and prints width and height in mm.

If the photo is already undistorted (from `dataset/images`):

```bash
python3 measure.py --no-undistort dataset/images/"WhatsApp Image 2026-11-06 at 2.05.38 AM.jpg"
```

Weights: `train/runs/best.pt`  
SHA-256: see `results/weights_sha256.txt`

## Rebuild steps

```bash
python3 calibration/calibrate.py
python3 dataset/prepare.py
python3 dataset/build_masks.py
python3 train/train.py
python3 train/eval.py
```
