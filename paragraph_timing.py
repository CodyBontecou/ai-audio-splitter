import json
import nltk
from pydub import AudioSegment
from difflib import SequenceMatcher


def find_paragraph_timing(data, paragraph):
    # Initialize variables for tracking the best match and its corresponding times
    best_match_ratio = 0.0
    best_match_start_time = None
    best_match_end_time = None

    # Initialize a list to accumulate words and track the current match ratio
    accumulated_text = ""
    current_start_time = None

    # Iterate over each segment and then each word within the segment
    for segment in data['segments']:
        for word_info in segment['words']:
            # If we're starting a new accumulation, update the current start time
            if not accumulated_text:
                current_start_time = word_info['start']
            
            # Add the current word to the accumulated text
            accumulated_text += word_info['word'] + " "
            
            # Calculate the match ratio of the accumulated text to the target paragraph
            match_ratio = SequenceMatcher(None, accumulated_text.strip(), paragraph).ratio()

            # Update the best match if the current ratio is higher
            if match_ratio > best_match_ratio:
                best_match_ratio = match_ratio
                best_match_start_time = current_start_time
                best_match_end_time = word_info['end']
            
            # Criteria to reset the accumulation: if the text diverges significantly from the paragraph
            if match_ratio < 0.5 and len(accumulated_text) > len(paragraph) / 2:
                accumulated_text = ""
                current_start_time = None

    return best_match_start_time, best_match_end_time

# JSON data
with open('split_17.json', 'r') as f:
    data = json.load(f)

# Example paragraph text
text1 = "As we were talking about observability for build systems, I wanted to ask you if you've seen this concept that I saw somebody talking about on Twitter a while back, which was the concept was, or the question was, why don't we write tests for a build system? We write tests for our software to verify that our production system is going to work, why don't we write tests to validate that our build system is doing what we expect it to and doing it in the amount of time that we expect it to and so forth."

text2 = "One of the reasons we switched to Gradle a long time ago in one of the places I worked is because you could separate out the build logic into modules that you could test. We tended not to. We were using AMP before as well. So you could do it with AMP because you can write little Java code and test that. I mean, it's kind of difficult because sometimes what you want to test is it moves a file from here to here. And like, that's the sort of difficult thing to unit test, right?"

text3 = "With a build scan you can see like visually the parallelism of your build so you can see like it's run five different threads and this is where the tasks were run and I really like that because it's not quite the same as an automated test but it's at least some kind of feedback into what is happening in the build. And so I use these build scans to be like, I want to tune the build now I want to, with this build I was trying to add parallelization, add the build cache."

# Call the function with the JSON data and the paragraph text
start, end = find_paragraph_timing(data, text2)

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
