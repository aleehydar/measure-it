# Objectives

## MO-1

What is measured: Error in the card's width and height, in millimetres, against a ruler.
How: At least 10 photos. Each row is the ruler width, ruler height, system width, system height, and the absolute error. Then the mean absolute error, the mean percentage error, the median, and the worst case.
Target: Mean absolute error of 1 mm or less on width and on height. The card is only about 54 mm on the short side, so an error bigger than 1 mm is a size I would not trust.
Conditions: Brother's iPhone XR, main camera, zoom locked, indoor light, card and Infinix both flat and fully in frame, camera looking straight down.
Not included: The card cut off by the frame, the phone partly hidden, or the phone tilted up off the table.

## MO-2

What is measured: Mask IoU for the card on the test split.
How: The eval script on the committed test list. The test images are not used for training or for picking a checkpoint.
Target: 0.85 or higher. Under that, the outline is too rough for a 1 mm measurement.
Conditions: This ProBook, the saved weights, the committed test split.
Not included: The phone class, and the time spent training.
