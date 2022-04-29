# word-recog
This is a web application that can decipher words written in unistroke gestures of Palm OS.

## Installation
Flask must be installed in order to run this project. It can be installed in a directory for Python with the following commands on Linux:
```
mkdir wordrecog
cd wordrecog
python3 -m venv venv
. venv/bin/activate
pip3 install Flask
```
After this is done, the provided files of **main.py**, **templateLibrary.py**, and **recognize.html** must be included in this directory.

## How to Use
The application can be used by running **main.py**. This will provide a link to the Flask app.
Upon opening, the webpage will provide a brief description of the project and will include a canvas on which the user can draw. All strokes that are not significantly small will be matched to a capital English letter and displayed in the text area below the canvas. The user can also click on the Clear Board button to reset the canvas.
