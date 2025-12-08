from pdf_writer import create_pdf
import os

segments = [
    {'start': 0.0, 'end': 5.0, 'text': ' This is the first segment.'},
    {'start': 5.0, 'end': 12.5, 'text': ' Here is another segment, a bit longer than the first one to test wrapping.'},
    {'start': 15.0, 'end': 20.0, 'text': ' And a final segment.'}
]

output_file = "test_transcript.pdf"

try:
    create_pdf(segments, output_file)
    if os.path.exists(output_file):
        print(f"SUCCESS: {output_file} created.")
        # Clean up
        os.remove(output_file)
    else:
        print("FAILURE: output file not found.")
except Exception as e:
    print(f"FAILURE: {e}")
