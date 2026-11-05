# Plan

8 hours. Written before any code.

I am measuring my university card, not a bank card.

Changed after the first commit: the object is the university card, and the phone size comes from the published spec, not from a ruler.

The camera is my brother's iPhone XR. Main camera only, no zoom. Focus and resolution stay as they are after I calibrate. The pixel size goes in the README once I have the first photo.

The reference is my Infinix Smart 9, flat on the table next to the card. I am using the body size from GSMArena: 165.7 mm high and 77.1 mm wide. I am not measuring the phone with a ruler. The case stays off, and the outline I use is the outer body, not the screen. The phone is thicker than the card, so both have to lie flat and the photo has to be looking straight down. If the phone is tilted, the millimetres are wrong.

Order:

1. These docs. About 30 minutes.
2. Print a checkerboard with at least 7 by 9 inner corners, tape it to something rigid, and measure one square with the ruler. Shoot 20 or more photos on the iPhone XR and calibrate with OpenCV. Save the camera matrix and distortion. About 90 minutes.
3. Shoot 70 or more photos of the university card with the Infinix in the same frame. Same camera settings. Undistort, then label the card and the phone. About 2 hours. Split 70/20/10 and commit those file lists before training.
4. Fine-tune torchvision DeepLabV3 with a MobileNet backbone. Two classes, card and phone. This machine is an HP ProBook 445 G7, so I am not training a heavy model. Not YOLO, not Roboflow. About 2 hours.
5. One command. New photo in, undistort, segment, find the phone, print the card width and height in mm. About 90 minutes.
6. If that runs, check at least 10 photos of the card against the ruler. About 30 minutes.

The tilt test and the "do not answer when the shot is bad" rule wait until the command and the ruler check are done. If I run out of time I stop and write what I did not reach.

## Decision record

Not written yet.
