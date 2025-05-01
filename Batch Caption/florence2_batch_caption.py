import os
import sys
from pathlib import Path
from gradio_client import Client, handle_file
import time
import ast # For parsing dictionary strings safely

# --- Constants ---
TASK_CHOICE_MAP = {
    # Store BOTH the API string (user-friendly) and the Dictionary Key (internal tag)
    '1': {'api_string': 'Caption',             'dict_key': '<CAPTION>',             'desc': 'Standard Caption',        'tag': 'caption'},
    '2': {'api_string': 'Detailed Caption',      'dict_key': '<DETAILED_CAPTION>',      'desc': 'Detailed Caption',      'tag': 'detailed'},
    '3': {'api_string': 'More Detailed Caption', 'dict_key': '<MORE_DETAILED_CAPTION>', 'desc': 'More Detailed Caption', 'tag': 'more_detailed'}
}

# --- Configuration ---
GRADIO_SERVER_URL = "http://127.0.0.1:7860"
API_NAME = "/process_image" # Confirmed

# --- User Interaction ---
print("Please choose the type of caption:")
for key, value in TASK_CHOICE_MAP.items():
    print(f"  {key}: {value['desc']}")

# Initialize variables
selected_api_task_string = None # String to send to API (e.g., "Detailed Caption")
selected_dict_key = None        # Key to lookup in result dict (e.g., "<DETAILED_CAPTION>")
selected_task_tag = None        # For naming output files (e.g., "detailed")

while selected_api_task_string is None:
    choice = input("Enter the number of your choice: ").strip()
    if choice in TASK_CHOICE_MAP:
        # Assign values based on the chosen task from the map
        selected_api_task_string = TASK_CHOICE_MAP[choice]['api_string']
        selected_dict_key        = TASK_CHOICE_MAP[choice]['dict_key'] # *** Use the correct key for lookup ***
        selected_task_tag        = TASK_CHOICE_MAP[choice]['tag']
        print(f"You selected: {TASK_CHOICE_MAP[choice]['desc']}")
    else:
        print("Invalid choice. Please enter a number from the list.")

# --- Get Input Folder Path ---
input_folder_path = None
while input_folder_path is None:
    path_str = input("Enter the full path to the folder containing your images: ").strip()
    if not path_str:
        print("Path cannot be empty.")
        continue
    potential_path = Path(path_str)
    if potential_path.is_dir():
        input_folder_path = potential_path
        print(f"Using image folder: {input_folder_path}")
    else:
        print(f"Error: '{path_str}' is not a valid directory or does not exist. Please try again.")

# --- Prepare Output Paths ---
if selected_task_tag is None:
     print("Error: Task tag was not set after selection. Exiting.")
     sys.exit(1)
csv_output_filename = f"florence2_{selected_task_tag}_captions_summary.csv"
csv_output_file_path = input_folder_path / csv_output_filename
print(f"CSV Summary will be saved to: {csv_output_file_path}")
print(f"Individual .txt captions will be saved in: {input_folder_path}")


# --- Script Execution ---
print(f"\nConnecting to Gradio server at {GRADIO_SERVER_URL}...")
try:
    client = Client(GRADIO_SERVER_URL, verbose=False)
except Exception as e:
    print(f"Error connecting to Gradio server: {e}")
    print("Please ensure the Florence-2 Pinokio app is running and accessible.")
    sys.exit(1)

print(f"Processing images from: {input_folder_path}")

image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
try:
    image_files = [
        f for f in input_folder_path.glob('*')
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
except Exception as e:
    print(f"Error accessing or reading the image folder: {e}")
    sys.exit(1)

if not image_files:
    print(f"No images with supported extensions ({', '.join(image_extensions)}) found in {input_folder_path}.")
    sys.exit(0)

print(f"Found {len(image_files)} images to process.")

try:
    # Open the main CSV file for writing
    with open(csv_output_file_path, 'w', encoding='utf-8') as csv_outfile:
        csv_outfile.write("filename,caption\n") # CSV Header

        total_start_time = time.time()
        processed_count = 0
        error_count = 0

        for i, image_path_obj in enumerate(image_files):
            print(f"  Processing ({i+1}/{len(image_files)}): {image_path_obj.name}...")
            caption = "" # Initialize caption for this iteration
            raw_result_str = "" # Store raw result for debugging errors
            try:
                # Use handle_file (preferred) to prepare image path
                image_arg = handle_file(str(image_path_obj))

                predict_start_time = time.time()
                # Call the prediction endpoint
                result = client.predict(
                    image_arg,                # Image FIRST
                    selected_api_task_string, # Task string SECOND (e.g., "Detailed Caption")
                    api_name=API_NAME         # Use the confirmed API name "/process_image"
                )
                predict_end_time = time.time()

                # Extract the actual caption text
                if isinstance(result, (list, tuple)) and len(result) > 0:
                    raw_result_str = str(result[0]).strip()
                    try:
                        result_dict = ast.literal_eval(raw_result_str)
                        if isinstance(result_dict, dict):
                             # *** Use the CORRECT dictionary key for lookup ***
                             caption = result_dict.get(selected_dict_key, "").strip()
                        else:
                             caption = raw_result_str
                    except (ValueError, SyntaxError):
                        print(f"    Warning: Could not parse result as dict for {image_path_obj.name}. Using raw string.")
                        caption = raw_result_str
                else:
                    raw_result_str = str(result).strip()
                    caption = raw_result_str

                if not caption:
                    # Raise specific error if caption is empty after processing
                    raise ValueError(f"Caption extracted was empty from result: {raw_result_str}")

                print(f"    Caption: {caption} (took {predict_end_time - predict_start_time:.2f}s)")

                # Write Individual TXT file
                txt_filepath = image_path_obj.with_suffix('.txt')
                try:
                    with open(txt_filepath, 'w', encoding='utf-8') as txt_outfile:
                        txt_outfile.write(caption)
                except IOError as txt_e:
                    print(f"    ERROR writing individual TXT file {txt_filepath.name}: {txt_e}")

                # Write to main CSV file
                cleaned_caption_csv = caption.replace("\"", "\"\"")
                csv_outfile.write(f'"{image_path_obj.name}","{cleaned_caption_csv}"\n')
                processed_count += 1

            except Exception as e:
                error_count += 1
                error_message_str = f"{type(e).__name__} - {e}"
                print(f"    ERROR processing {image_path_obj.name}: {error_message_str}")
                if raw_result_str:
                    print(f"      Raw result before error: {raw_result_str}")
                error_message_csv = error_message_str.replace("\"", "\"\"")
                csv_outfile.write(f'"{image_path_obj.name}","ERROR: {error_message_csv}"\n')

    total_end_time = time.time()
    print("-" * 30)
    print(f"Batch captioning complete.")
    print(f"Successfully processed {processed_count}/{len(image_files)} images.")
    if error_count > 0:
         print(f"Encountered errors on {error_count} images. Check the output CSV for details.")
    print(f"Total time: {total_end_time - total_start_time:.2f} seconds.")
    print(f"CSV summary saved to: {csv_output_file_path}")
    print(f"Individual caption .txt files saved in: {input_folder_path}")

except IOError as e:
    print(f"Error opening or writing to the main CSV output file '{csv_output_file_path}': {e}")
    print("Please check file permissions and available disk space.")
except Exception as e:
    print(f"An unexpected error occurred during processing: {e}")
