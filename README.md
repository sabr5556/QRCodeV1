# Pure Python QR Code Generator

A lightweight, dependency-free QR Code generator written from scratch in Python 3.

## Features
* **No External Libraries:** Built using only standard Python lists and math.
* **Custom Implementation:** Includes manual implementation of Reed-Solomon Error Correction and Matrix placement logic.
* **Supports:** Version 1 QR Codes (21x21) with Error Correction Levels L, M, Q and H.

## Usage
Run the main script to generate a QR code in your terminal:

python main.py


Special thanks to Thonky's QR code tutorial for which I owe lots.
Also thank you to Professor Gemini, my friend, teacher, and confedant through this arduous process of learning how to code.

Works if run in terminal in dark mode. Just enter your string and the error correction level you want. 


Fails on some error handling, like if the input string is too long, but hey. Ill take it. 
