# Accuracy table

Truth is ISO ID-1 85.60 mm by 53.98 mm on every row. No ruler.
Phone scale is GSMArena 165.7 mm by 77.1 mm.
Photos are the undistorted set in dataset/images. measure.py --no-undistort.

| # | image | true W | true H | sys W | sys H | abs err W | abs err H |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | WhatsApp Image 2026-11-06 at 2.05.42 AM (1).jpg | 85.60 | 53.98 | 87.84 | 60.55 | 2.24 | 6.57 |
| 2 | WhatsApp Image 2026-11-06 at 2.05.32 AM (1).jpg | 85.60 | 53.98 | 82.06 | 53.64 | 3.54 | 0.34 |
| 3 | WhatsApp Image 2026-11-06 at 2.05.47 AM.jpg | 85.60 | 53.98 | 76.54 | 49.05 | 9.06 | 4.93 |
| 4 | WhatsApp Image 2026-11-06 at 2.05.38 AM.jpg | 85.60 | 53.98 | 82.77 | 54.89 | 2.83 | 0.91 |
| 5 | WhatsApp Image 2026-11-06 at 2.05.46 AM.jpg | 85.60 | 53.98 | 111.64 | 71.50 | 26.04 | 17.52 |
| 6 | WhatsApp Image 2026-11-06 at 2.05.44 AM.jpg | 85.60 | 53.98 | 93.23 | 61.83 | 7.63 | 7.85 |
| 7 | WhatsApp Image 2026-11-06 at 2.05.29 AM.jpg | 85.60 | 53.98 | 88.41 | 55.72 | 2.81 | 1.74 |
| 8 | WhatsApp Image 2026-11-06 at 2.05.37 AM.jpg | 85.60 | 53.98 | 91.54 | 60.60 | 5.94 | 6.62 |
| 9 | WhatsApp Image 2026-11-06 at 2.05.26 AM (2).jpg | 85.60 | 53.98 | 80.77 | 47.66 | 4.83 | 6.32 |
| 10 | WhatsApp Image 2026-11-06 at 2.05.25 AM.jpg | 85.60 | 53.98 | 73.61 | 34.25 | 11.99 | 19.73 |

Mean abs error width: 7.69 mm
Mean abs error height: 7.25 mm
Mean pct error width: 8.98 %
Mean pct error height: 13.44 %
Median abs error width: 5.39 mm
Median abs error height: 6.45 mm
Worst abs error width: 26.04 mm (WhatsApp Image 2026-11-06 at 2.05.46 AM.jpg)
Worst abs error height: 19.73 mm (WhatsApp Image 2026-11-06 at 2.05.25 AM.jpg)

MO-1 target was 1 mm mean on both. Missed. Likely causes: phone outline includes case-free body but some shots are tilted or the phone is partly foreshortened, and one frame (2.05.46) is a clear outlier.
