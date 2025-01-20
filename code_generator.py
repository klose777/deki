import argparse
import base64
import os
import sys
from openai import OpenAI

def encode_image(image_path):
    """Encodes an image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def init():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Generate code for a mobile screen based on an image and its description.')
    parser.add_argument('input_image', help='Path to the input image.')
    parser.add_argument('input_file', help='Path to the image description file.')
    parser.add_argument('output_file', help='Path where the generated code will be saved.')
    parser.add_argument('os_system', help='Target operating system (e.g., Android, iOS).')
    args = parser.parse_args()

    # Validate the input files
    if not os.path.isfile(args.input_image):
        print(f"Error: Input image file not found at {args.input_image}")
        sys.exit(1)

    if not os.path.isfile(args.input_file):
        print(f"Error: Input description file not found at {args.input_file}")
        sys.exit(1)

    # Read the image description
    with open(args.input_file, 'r', encoding='utf-8') as f:
        image_description = f.read()

    # Set up the OpenAI API client
    openai = OpenAI()
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        print("Error: OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
        sys.exit(1)

    # Encode the image to base64
    try:
        base64_image = encode_image(args.input_image)
    except Exception as e:
        print(f"Error encoding the image file: {e}")
        sys.exit(1)

    # Prepare the messages for the chat completion
    messages = [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": f"Generate the code for this screen. The image description I created to assist you is here:\n\n{image_description}\n\nGenerate the code for {args.os_system}.",
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            },
        ],
        }
    ]

    # Call the OpenAI API with the prepared input
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=4000,
            temperature=0.7
        )
    except Exception as e:
        print(f"OpenAI API error: {e}")
        sys.exit(1)

    # Extract and print the generated code
    try:
        generated_code = response.choices[0].message.content
        print("\nGenerated Code:\n")
        print(generated_code)

        # Save the generated code to the specified output file
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        print(f"\nThe generated code has been saved to {args.output_file}")
    except Exception as e:
        print(f"Error processing the API response: {e}")
        sys.exit(1)

if __name__ == '__main__':
    init()
