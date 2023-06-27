import os
import openai
import time
import sys
import threading
import argparse
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Max tokens for a chunk
chunk_max = 4000

# Spinner to show script is working
def spinner():
    while not stop_spinner:
        for cursor in '|/-\\':
            sys.stdout.write(cursor)
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')

def spin_cursor():
    global stop_spinner
    stop_spinner = False
    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.start()

def stop_cursor():
    global stop_spinner
    stop_spinner = True

def main(args):
    # Initialize list for summaries
    summaries = []

    # Get list of all files in current directory
    try:
        files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.txt')]
    except Exception as e:
        print(f"Error occurred while listing files: {e}")
        return

    print("Checking files in the current directory...")

    # Combine all files into one if there are multiple
    if len(files) > 1:
        print("Multiple chunk files found. Combining them into one...")
        try:
            with open(args.output_combined, 'w') as outfile:
                for fname in files:
                    with open(fname) as infile:
                        outfile.write(infile.read())
            transcript_file = args.output_combined
        except Exception as e:
            print(f"Error occurred while combining files: {e}")
            return
    else:
        print("Single transcript file found.")
        transcript_file = files[0]

    print("Transcript file prepared.")

    try:
        with open(transcript_file, 'r') as file:
            data = file.read()
    except Exception as e:
        print(f"Error occurred while reading transcript file: {e}")
        return

    # Calculate the actual chunk_max, taking into account the length of the prompt
    actual_chunk_max = chunk_max - len(args.prompt)

    # Split the transcript into chunks
    print("Breaking transcript into chunks...")
    chunks = [data[i:i+actual_chunk_max] for i in range(0, len(data), actual_chunk_max)]

    print("Transcript broken into", len(chunks), "chunks.")

    print("Generating summaries...")

    # Start spinner
    spin_cursor()

    # Generate summaries for each chunk
    for chunk in chunks:
        try:
            response = openai.Completion.create(
                engine=args.engine,
                prompt=f"{args.prompt} \n\n{chunk}\n\n",
                temperature=args.temperature,
                max_tokens=args.max_tokens
            )
        except openai.error.OpenAIError as e:
            print(f"Error occurred while generating summaries: {e}")
            return

        summaries.append(response.choices[0].text.strip())

    # Stop spinner
    stop_cursor()

    print("Summaries generated.")

    print("Deduplicating summaries...")
    summaries = list(dict.fromkeys(summaries))

    print("Writing summaries to file...")
    try:
        with open(args.output_summary, 'w') as outfile:
            for summary in summaries:
                outfile.write(summary + '\n')
    except Exception as e:
        print(f"Error occurred while writing summaries to file: {e}")
        return

    print("Summary file created.")

    # Cleanup is optional, controlled by command-line argument
    if args.cleanup:
        print("Cleaning up original files...")
        for f in files:
            try:
                os.remove(f)
            except Exception as e:
                print(f"Error occurred while deleting file {f}: {e}")
                return

        if os.path.exists(args.output_combined):
            try:
                os.remove(args.output_combined)
            except Exception as e:
                print(f"Error occurred while deleting file {args.output_combined}: {e}")
                return

        print("Cleanup completed.")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Generate summaries from text chunks.')
    parser.add_argument('--no-cleanup', dest='cleanup', action='store_false', help='Disable cleanup of original files.')
    parser.add_argument('--engine', default="text-davinci-003", help='Specify the engine to be used.')
    parser.add_argument('--temperature', type=float, default=0.5, help='Specify the temperature.')
    parser.add_argument('--max_tokens', type=int, default=200, help='Specify max tokens.')
    parser.add_argument('--prompt', default="This is a transcribed text (without diarization) from an online video. Could you summarize the main topics or points of view presented by the speakers in bullet point form?", help='Specify the prompt.')
    parser.add_argument('--output_summary', default="summary.txt", help='Specify the output summary file name.')
    parser.add_argument('--output_combined', default="combined.txt", help='Specify the output combined file name.')
    parser.set_defaults(cleanup=True)
    args = parser.parse_args()

    # Get API key from environment variables
    openai.api_key = os.getenv('OPENAI_KEY')

    if openai.api_key is None:
        print("Error: OpenAI API key not found. Please make sure the OPENAI_KEY environment variable is set.")
        sys.exit(1)

    stop_spinner = False
    main(args)
