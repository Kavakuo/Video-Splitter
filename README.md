# Video Splitter

This tool helps for multicam postproduction. If you have multiple massive video files it splits each file roughly at the same position. The tool executes `ffmpeg` without re-encoding of the video files, to preserve original quality.

## How to use
- Edit `VIDEO_FILES` and `SPLIT_POINTS` in `main.py` 
- Run `python3 src/main.py --output-folder /output/folder/`
