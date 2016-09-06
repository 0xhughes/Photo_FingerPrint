# Photo_FingerPrint
This script was written in Python and is intended for use in the identification and correlation of images based on color variation percentage analysis.

This script was inspired during my time in law enforcement working on image based contraband cases. Microsoft has a product they put together called PhotoDNA that is incorporated into many products used by law enforcement to find matching images based on non-hash based characteristics. (Don't quote me on that as gospel.)

I thought the idea was interesting and myself believe you could perform image correlation and identification based on color pattern usage. This script takes an image file, generates it into 100 "quadrants", and then calculates an average RGB value for each quadrant. Then a "signature" (rather, list of RGB values) is generated of an image, and either stored for later comparison, or used in a comparison.

It compars the stored quadrants within a DB to the calculated quadrants of an comparison target and generates an overall percentage difference in the colors of the image. The aim of this is to be able to identify like images after resizing, light editing, minor cropping, etc.

I no longer work in law enforcement but do work on this project from time to time as it was an intersting idea. It is fairly slow, there is A LOT of optimization I feel that could be done.

I am releasing this as maybe further collabarators would like to contribute to it, or maybe even someone finds it useful!

To use, run the script via Python interpreter and follow the options. This was written in Windows 7 with Python 2.7.x.
