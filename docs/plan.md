# Plan

8 hours. Written before any code.

Changed after the first commit: I dropped the university card. I do not know its size, and I have no ruler. The object is my brother's Meezan debit card. A normal Meezan debit card is ISO/IEC 7810 ID-1, 85.60 mm by 53.98 mm. I am using that published size as the true size on every photo. I am not measuring the card by hand.

The camera is my brother's iPhone XR. Main camera only, no zoom. Focus and resolution stay as they are after I calibrate. The pixel size goes in the README once I have the first photo.

The reference is my Infinix Smart 9, flat on the table next to the card. Body size from GSMArena: 165.7 mm high and 77.1 mm wide. The case stays off, and the outline is the outer body, not the screen. The phone is thicker than the card, so both have to lie flat and the photo has to be looking straight down. If the phone is tilted, the millimetres are wrong.

The card is not the scale. The phone is not the answer. The error is the published card size against the published phone size.

Order:

1. These docs. About 30 minutes.
2. Print a checkerboard with at least 7 by 9 inner corners, tape it to something rigid. I have no ruler, so the square size is whatever the PDF says, and I will write that it was not checked. Shoot 20 or more photos on the iPhone XR and calibrate with OpenCV. Save the camera matrix and distortion. About 90 minutes.
3. Shoot 70 or more photos of the Meezan card with the Infinix in the same frame. Same camera settings. Undistort, then label the card and the phone. About 2 hours. Split 70/20/10 and commit those file lists before training.
4. Fine-tune torchvision DeepLabV3 with a MobileNet backbone. Two classes, card and phone. This machine is an HP ProBook 445 G7, so I am not training a heavy model. Not YOLO, not Roboflow. About 2 hours.
5. One command. New photo in, undistort, segment, find the phone, print the card width and height in mm. About 90 minutes.
6. If that runs, compare at least 10 photos with 85.60 mm by 53.98 mm. About 30 minutes.

The tilt test and the "do not answer when the shot is bad" rule wait until the command and that comparison are done. If I run out of time I stop and write what I did not reach.

## Decision record

Not written yet.
