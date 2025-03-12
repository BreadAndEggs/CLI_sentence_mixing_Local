#!/usr/bin/env python3

import argparse
import concurrent.futures

import sentence_mixing.sentence_mixer as sm
from sentence_mixing.video_creator.video import create_video_file

from cli_interface import loop_interface

VIDEO_OUT = "out.mp4"

# New function to handle local video files instead of downloading
def process_local_videos(local_files):
    # Assuming local_files are paths to video files already on your system
    # You can modify this function to do anything you want with the local files
    return local_files  # Just returning the list of paths for now

def main(audio_command, config_path, skip_first, video_files, seed=0):
    sm.prepare_sm_config_file(config_path)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Skip the video downloading and just pass local files directly
        futures_vids = executor.map(process_local_videos, [video_files])
        futures_vids_audio = executor.map(sm.get_videos, [video_files], [seed])

        total_timestamps, total_text, videos = loop_interface(
            audio_command, futures_vids_audio
        )

        # We're not downloading anything, so just assign the paths directly
        paths = list(futures_vids)[0]

    for v, p in zip(videos, paths):
        n = len(v._base_path)
        assert p[:n] == v._base_path
        v.extension = p[n + 1 :]

    create_video_file(total_timestamps, VIDEO_OUT)

    return total_text


DEFAULT_AUDIO_COMMAND = 'tycat "{}"'

DESCRIPTION = "CLI Interface to create sentence mixing videos."

AUDIO_COMMAND_HELP = f"a command to launch a playback of an audio file passed as a format parameter (default: {DEFAULT_AUDIO_COMMAND})"
CONFIG_PATH_HELP = "path to the json config file"
VIDEO_FILE_HELP = "path to the local video file(s)"
SKIP_ANALYSIS_HELP = "tell the generator to skip the analysis (default: false)"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "-c",
        "--audio-command",
        default=DEFAULT_AUDIO_COMMAND,
        help=AUDIO_COMMAND_HELP,
    )
    parser.add_argument(
        "config_path",
        metavar="CONFIG_PATH",
        action="store",
        help=CONFIG_PATH_HELP,
    )
    parser.add_argument(
        "video_files",
        metavar="VIDEO_FILE",
        nargs="+",
        action="store",
        help=VIDEO_FILE_HELP,
    )
    parser.add_argument(
        "-s",
        "--skip",
        dest="skip_first_analysis",
        action="store_true",
        default=False,
        help=SKIP_ANALYSIS_HELP,
    )

    args = parser.parse_args()

    print(
        main(
            args.audio_command,
            args.config_path,
            args.skip_first_analysis,
            args.video_files,
        )
    )
