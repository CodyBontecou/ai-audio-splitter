import json
import nltk
from pydub import AudioSegment
from difflib import SequenceMatcher
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
client = OpenAI()

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

    print(f"Start: {best_match_start_time}, End: {best_match_end_time}")

    return best_match_start_time, best_match_end_time


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


with open('split_17.txt', 'r') as file:
    transcript_text = file.read()

generate_prompt = lambda text : f"${text} Give me three sections of text extracted from this block of text that you believe to be the most interesting and worth sharing with others. Make sure the sections of text are at least 50 words longs. Do not create any text yourself and instead only use sentences from what was provided above."

response = client.chat.completions.create(
  model="gpt-3.5-turbo-0125",
  response_format={ "type": "json_object" },
  messages=[
    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
    {"role": "user", "content": generate_prompt(transcript_text)}
  ]
)

gpt_json = response.choices[0].message.content

# JSON data
with open('split_17.json', 'r') as f:
    split_json_data = json.load(f)

file_path = 'hp-output/wav/split_17.wav'

for key, value in json.loads(gpt_json).items():
    print(f"Key: {key}, Value: {value}")
    # Call the function with the JSON data and the paragraph text
    start_time, end_time = find_paragraph_timing(split_json_data, value)
    extract_audio_segment(file_path, start_time, end_time, f'split_17_{key}.wav')
