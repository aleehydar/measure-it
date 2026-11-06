"""Calibrate the iPhone XR from photos of the on-screen checkerboard.

The board is 12 by 8 squares, so OpenCV looks for 11 by 7 inner corners.
Squares are stretched to the ProBook panel (309 mm by 174 mm), so a cell is
not a square. Shops were closed and there is no ruler.
"""

import glob
import os

import cv2
import numpy as np

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")
OUT_PATH = os.path.join(os.path.dirname(__file__), "camera.npz")
PATTERN = (11, 7)
COLS = 12
ROWS = 8
PANEL_MM = (309.0, 174.0)
SQUARE_MM = (PANEL_MM[0] / COLS, PANEL_MM[1] / ROWS)


def object_points():
    cols, rows = PATTERN
    obj = np.zeros((rows * cols, 3), np.float32)
    grid = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
    obj[:, 0] = grid[:, 0] * SQUARE_MM[0]
    obj[:, 1] = grid[:, 1] * SQUARE_MM[1]
    return obj


def main():
    paths = sorted(glob.glob(os.path.join(RAW_DIR, "*")))
    objp = object_points()
    obj_points = []
    img_points = []
    image_size = None
    used = []
    skipped = []

    for path in paths:
        image = cv2.imread(path)
        if image is None:
            skipped.append(os.path.basename(path))
            continue
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ok, corners = cv2.findChessboardCornersSB(gray, PATTERN, cv2.CALIB_CB_EXHAUSTIVE)
        if not ok:
            skipped.append(os.path.basename(path))
            continue
        obj_points.append(objp)
        img_points.append(corners.astype(np.float32))
        image_size = gray.shape[::-1]
        used.append(os.path.basename(path))

    if len(used) < 10:
        raise SystemExit(f"only {len(used)} boards found, not enough to calibrate")

    rms, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        obj_points, img_points, image_size, None, None
    )

    per_image = []
    for obj, img, rvec, tvec in zip(obj_points, img_points, rvecs, tvecs):
        projected, _ = cv2.projectPoints(obj, rvec, tvec, camera_matrix, dist_coeffs)
        err = cv2.norm(img, projected, cv2.NORM_L2) / np.sqrt(len(projected))
        per_image.append(err)

    np.savez(
        OUT_PATH,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        image_size=np.array(image_size),
        reprojection_error=np.array(rms),
        square_mm=np.array(SQUARE_MM),
        pattern=np.array(PATTERN),
    )

    print(f"images read: {len(paths)}")
    print(f"boards used: {len(used)}")
    print(f"boards skipped: {len(skipped)}")
    print(f"image size: {image_size[0]}x{image_size[1]}")
    print(f"square mm: {SQUARE_MM[0]:.2f} by {SQUARE_MM[1]:.2f}")
    print(f"rms reprojection error: {rms:.4f} px")
    print(f"per image mean: {np.mean(per_image):.4f} px")
    print(f"per image worst: {np.max(per_image):.4f} px")
    print("camera matrix:")
    print(camera_matrix)
    print("distortion:")
    print(dist_coeffs.ravel())
    if skipped:
        print("skipped:")
        for name in skipped:
            print(f"  {name}")

    sample = cv2.imread(os.path.join(RAW_DIR, used[0]))
    undistorted = cv2.undistort(sample, camera_matrix, dist_coeffs)
    preview = os.path.join(os.path.dirname(__file__), "undistorted_sample.jpg")
    cv2.imwrite(preview, undistorted)
    print(f"saved {OUT_PATH}")
    print(f"saved {preview}")


if __name__ == "__main__":
    main()
