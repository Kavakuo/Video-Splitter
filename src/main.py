import subprocess
import os
from typing import List
import argparse
from splitTypes import VideoFile, SplitPoint


# Add all video files to the list
# second argument is a timestamp where all files are roughly in sync
VIDEO_FILES: List[VideoFile] = [
    VideoFile('/absolute/path/video1.MP4', "00:09:37"),
    VideoFile('/absolute/path/video2.MP4', "00:02:35"),
]

REFERENCE_FILE: VideoFile = VIDEO_FILES[0]

# Add SplitPoints where the video files should be splitted.
# The timestampes are relative to the reference file
SPLIT_POINTS: List[SplitPoint] = [
    SplitPoint('00:09:30', "Part 1"),
    SplitPoint('00:14:30', "Part 2"),
    SplitPoint('00:19:40', "Part 3"),
    # Add more split points as needed
]

def hms_to_seconds(hms: str) -> float:
    h, m, s = map(float, hms.split(':'))
    return int(h) * 3600 + int(m) * 60 + s

def seconds_to_hms(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:06.3f}" if not s.is_integer() else f"{h:02}:{m:02}:{int(s):02}"

def get_relative_split_points(ref_sync: str, file_sync: str) -> List[SplitPoint]:
    ref_sync_sec = hms_to_seconds(ref_sync)
    file_sync_sec = hms_to_seconds(file_sync)
    offset = file_sync_sec - ref_sync_sec
    rel_points: List[SplitPoint] = []
    for p in SPLIT_POINTS:
        p_sec = hms_to_seconds(p.time)
        rel_sec = p_sec + offset
        rel_points.append(SplitPoint(seconds_to_hms(max(rel_sec, 0)), p.title))
    return rel_points

def get_video_duration(file: str) -> float:
    import json
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'json', file
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"ffprobe failed for {file}")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        return 0.0
    try:
        duration = float(json.loads(result.stdout)['format']['duration'])
    except Exception:
        duration = 0.0
    return duration

def split_videos(ref_sync: str, output_folder: str) -> None:
    for file in VIDEO_FILES:
        base, ext = os.path.splitext(os.path.basename(file.path))
        file_sync = file.syncTimestamp
        if file.path == REFERENCE_FILE.path:
            rel_points = SPLIT_POINTS
        else:
            rel_points = get_relative_split_points(ref_sync, file_sync)
        duration = get_video_duration(file.path)
        for i in range(len(rel_points)-1):
            start = rel_points[i]
            end = rel_points[i+1]
            start_sec = hms_to_seconds(start.time)
            end_sec = hms_to_seconds(end.time)
            segment_duration = end_sec - start_sec
            if start_sec + segment_duration > duration:
                segment_duration = max(0, duration - start_sec)
            output = os.path.join(output_folder, f"{base}_{start.title}{ext}")
            segment_duration = seconds_to_hms(segment_duration)
            cmd = [
                "ffmpeg", "-ss", start.time, "-i", file.path, "-to", segment_duration, "-c", "copy", output
            ]
            print("Running:", " ".join(cmd))
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print(f"ffmpeg failed for {file.path} [{start.title}]")
                print("stdout:", result.stdout)
                print("stderr:", result.stderr)

def main() -> None:
    parser = argparse.ArgumentParser(description="Split videos at specified points.")
    parser.add_argument('--output-folder', type=str, required=True, help='Folder to save split video files')
    args = parser.parse_args()
    output_folder = args.output_folder
    os.makedirs(output_folder, exist_ok=True)

    ref_sync = REFERENCE_FILE.syncTimestamp
    if REFERENCE_FILE not in VIDEO_FILES:
        print("Reference file not in VIDEO_FILES.")
        exit(1)
    if not SPLIT_POINTS or len(SPLIT_POINTS) < 2:
        print("Need at least two split points.")
        exit(1)
    print(f"Reference file: {REFERENCE_FILE}, Sync at: {ref_sync}")
    split_videos(ref_sync, output_folder)

if __name__ == "__main__":
    main()