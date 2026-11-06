# Definition of Done

Written before the work. A box gets ticked only when a number or a commit sits next to it.

- [x] Reprojection error reported, with the calibration image count. 0.3928 px rms, 21 boards used out of 27 photos. calibration/result.txt
- [x] Test split file committed before training started. dataset/splits/test.txt, 12 images, seed 7.
- [x] Labels stopped at 71 photos for time. Masks in dataset/masks. Training uses train_labeled.txt (49/13/9).
- [x] Command runs on a new image and prints width and height in mm. `python3 measure.py path.jpg`
- [x] Accuracy table for 10 instances, raw outputs saved. results/accuracy.md, results/accuracy_raw.txt
- [x] MO-1 missed. Mean abs error about 7.7 mm width and 7.3 mm height. results/accuracy.md
- [x] What I did not finish: tilt / breaking-condition test, refusal path, full 116 labels, MO-1 target.
