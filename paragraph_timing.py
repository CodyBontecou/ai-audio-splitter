import json
import nltk
from pydub import AudioSegment
from difflib import SequenceMatcher


def find_paragraph_timing(data, paragraph):
    accumulated_text = ""
    best_match_ratio = 0.0
    start_time, end_time = None, None
    threshold_for_start = 0.2  # Lower threshold to catch the start more accurately

    for segment in data['segments']:
        if accumulated_text:  # Ensure there's preceding text to compare
            # Pre-append current segment text to check if it improves match significantly
            test_accumulated_text = accumulated_text + " " + segment['text']
            matcher_pre = SequenceMatcher(None, test_accumulated_text.strip(), paragraph)
            match_ratio_pre = matcher_pre.ratio()

            # If this segment improves the match significantly, consider it a potential start
            if match_ratio_pre > best_match_ratio and match_ratio_pre > threshold_for_start and not start_time:
                start_time = segment['start']
                best_match_ratio = match_ratio_pre  # Update the best match seen so far

        # Continue to accumulate text and update end time based on best match
        accumulated_text += " " + segment['text']
        matcher = SequenceMatcher(None, accumulated_text.strip(), paragraph)
        match_ratio = matcher.ratio()

        if match_ratio > best_match_ratio:
            best_match_ratio = match_ratio
            end_time = segment['end']  # Update end time as we find better matches

    return start_time, end_time

# JSON data
with open('split_17.json', 'r') as f:
    data = json.load(f)

# Example paragraph text
paragraph_text = "As we were talking about observability for build systems, I wanted to ask you if you've seen this concept that I saw somebody talking about on Twitter a while back, which was the concept was, or the question was, why don't we write tests for a build system? We write tests for our software to verify that our production system is going to work, why don't we write tests to validate that our build system is doing what we expect it to and doing it in the amount of time that we expect it to and so forth."

# Call the function with the JSON data and the paragraph text
start, end = find_paragraph_timing(data, paragraph_text)

print(f"Start: {start}, End: {end}")


def extract_audio_segment(file_path, start_time, end_time, output_file):
    """
    Extracts a segment from an audio file and saves it to a new file.

    Parameters:
    - file_path: Path to the original audio file.
    - start_time: Start time of the segment to extract, in seconds.
    - end_time: End time of the segment to extract, in seconds.
    - output_file: Path to save the extracted audio segment.
    """
    # Convert start and end times from seconds to milliseconds
    start_time_ms = start_time * 1000
    end_time_ms = end_time * 1000

    # Load the audio file
    audio = AudioSegment.from_file(file_path)

    # Extract the specified segment
    extracted_segment = audio[start_time_ms:end_time_ms]

    # Save the extracted segment to a new file
    extracted_segment.export(output_file, format="wav")

# Example usage
file_path = 'hp-output/split_17.wav'  # Update this to your audio file's path
output_file = 'split_17_test.wav'  # Update this to your desired output path

extract_audio_segment(file_path, start, end, output_file)
