# Objectives

## MO-1

What is measured: Error in the Meezan card's width and height, in millimetres, against the ID-1 size.
How: At least 10 photos. Each row is 85.60 mm, 53.98 mm, the system width, the system height, and the absolute error. Then the mean absolute error, the mean percentage error, the median, and the worst case. The true size is the same on every row because I have no ruler.
Target: Mean absolute error of 1 mm or less on width and on height. Past that, I would not trust the size.
Conditions: Brother's iPhone XR, main camera, zoom locked, indoor light, card and Infinix both flat and fully in frame, camera looking straight down. Phone scale is the GSMArena body size, 165.7 mm by 77.1 mm, case off. Card truth is ISO ID-1, 85.60 mm by 53.98 mm.
Not included: The card cut off by the frame, the phone partly hidden, the phone tilted up off the table, a case on the phone, or a card that is not a full-size debit card.

## MO-2

What is measured: Mask IoU for the card on the test split.
How: The eval script on the committed test list. The test images are not used for training or for picking a checkpoint.
Target: 0.85 or higher. Under that, the outline is too rough for a 1 mm measurement.
Conditions: This ProBook, the saved weights, the committed test split.
Not included: The phone class, and the time spent training.
