# Multimedia-File-Visualization

This is a GUI Programming project that reads .wav and .bmp files to display the waveforms and images respectively.

## WAV File Viewer

This is a GUI program that can open a PCM-encoded stereo .wav file and display the waveforms of its two channels. This GUI also displays the total number of samples and the sampling frequency of the selected audio file.

### How to run the program

python3 wav_viewer.py

### Workflow

1. The program first shows an open file dialog for the user to select and load a .wav file.
2. After loading the file, it displays the waveforms of both channels, with the left channel on top and the right channel at the bottom
3. The total number of samples and the sampling frequency are also displayed on the screen.

### Assumptions

- This program only works on audio files that are PCM-encoded and stereo only (contains exactly 2 channels)
- Total number of samples will be an even number less than 65,536

## BMP Image Viewer

This is a GUI program that can open and display an uncompressed .bmp image file.

### How to run the program

python3 wav_viewer.py

### Workflow

1. The GUI displays an Open File menu item. Click on it to open a file dialog to select a .bmp file.
2. After selecting a file, the image gets displayed on the screen. You can use the Open File again to select and display other BMP files, which would clear the previously displayed image and display the newly-selected one.
3. To end the program, click on the Exit menu item.

### Assumptions
- Only works for 24-bit RGB full-color, uncompressed BMP images.
- Each image cannot be larger than 704 × 576 pixels, corresponding to 4 × CIF size