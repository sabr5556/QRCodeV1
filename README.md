# Pure Python QR Code Generator

A lightweight, dependency-free QR Code generator written from scratch in Python 3.

## Features
* **No External Libraries:** Built using only standard Python lists and math.
* **Custom Implementation:** Includes manual implementation of Reed-Solomon Error Correction and Matrix placement logic.
<<<<<<< HEAD
* **Automatic Masking:** Calculates the best mask pattern to allign with ISO standards.
* **Supports:** Version 1 QR Codes (21x21) with Error Correction Levels L, M, Q, and H.
=======
* **Supports:** Version 1 QR Codes (21x21) with Error Correction Levels L, M, Q and H.
>>>>>>> 28840c71542876501d73851eb6e0bf48970e86ee

## Usage
Run the main script to generate a QR code in your terminal:

<<<<<<< HEAD
on mac: python3 main.py
on windows: python main.py
=======
python3 main.py
>>>>>>> 28840c71542876501d73851eb6e0bf48970e86ee


Special thanks to Thonky's QR code tutorial for which I owe lots.
Also thank you to Professor Gemini, my friend, teacher, and confidant through this arduous process of learning how to code.

Works if run in terminal in dark mode. Just enter your string and the error correction level you want. Currently, masking is hardcoded, requiring a manual change to the mode if false eyes are generated. 


Fails on some error handling, like if the input string is too long, but hey. Ill take it. 
