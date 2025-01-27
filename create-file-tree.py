import os
import re
from collections import defaultdict


# Store the list_choice variable outside of run_script to persist across calls
list_all_files = None  # This will hold the user choice for listing files



def list_directory_as_tree(root_path, indent="", output_lines=None, list_all_files=False):
    """ Recursively list directory structure using ASCII-style tree and write to file """
    try:
        entries = sorted(os.listdir(root_path))
    except FileNotFoundError:
        print("â Error: Directory not found. Please check the path and try again.")
        return


    files, dirs = [], []


    # Separate files and directories, skipping hidden files and .DS_Store
    for entry in entries:
        if entry.startswith(".") or entry == ".DS_Store" or entry == "file_list.txt":
            continue  # Skip hidden files and .DS_Store
        full_path = os.path.join(root_path, entry)
        if os.path.isdir(full_path):
            dirs.append(entry)
        else:
            files.append(entry)


    # Print and save directories first
    for directory in dirs:
        line = f"{indent}{directory}/"
        print(line)  # Print to terminal
        output_lines.append(line)
        list_directory_as_tree(os.path.join(root_path, directory), indent + "  ", output_lines, list_all_files)


    # Format and print image sequences or list all files based on user choice
    if list_all_files:
        list_all_files_func(files, indent, output_lines)
    else:
        format_image_sequences(files, indent, output_lines)



def format_image_sequences(files, indent, output_lines):
    """ Identify and format image sequences in condensed format """
    frame_sequences = defaultdict(set)
    pattern = re.compile(r"(.*?)(\d{4})\.(\w+)$")  # Match sequences like file.0001.exr


    other_files = []


    for filename in files:
        match = pattern.match(filename)
        if match:
            base, frame, ext = match.groups()
            frame_sequences[(base, ext)].add(int(frame))
        else:
            other_files.append(filename)


    # Print and save image sequences as "[image sequence].extension"
    for (base, ext), _ in frame_sequences.items():
        line = f"{indent}{base}[image sequence].{ext}"
        print(line)  # Print to terminal
        output_lines.append(line)


    # Print and save non-sequence files normally
    for filename in other_files:
        line = f"{indent}{filename}"
        print(line)  # Print to terminal
        output_lines.append(line)



def list_all_files_func(files, indent, output_lines):
    """ List all files, including individual frames, without condensing sequences """
    for filename in files:
        line = f"{indent}{filename}"
        print(line)  # Print to terminal
        output_lines.append(line)



def get_unique_output_file(root_directory):
    """ Generate a unique output file name by appending an incremented number if the file already exists """
    base_output_file = os.path.join(root_directory, "file_list.txt")
    if not os.path.exists(base_output_file):
        return base_output_file


    counter = 2
    while True:
        new_output_file = os.path.join(root_directory, f"file_list-{counter:02d}.txt")
        if not os.path.exists(new_output_file):
            return new_output_file
        counter += 1



def adjust_indentation_in_file(output_file):
    """ Remove 2 spaces from the indent of every line in the output file """
    with open(output_file, "r", encoding="utf-8") as f:
        lines = f.readlines()


    # Adjust indentation by removing the first 2 spaces from each line
    adjusted_lines = [line[2:] if line.startswith("  ") else line for line in lines]


    # Rewrite the file with the adjusted indentation
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(adjusted_lines)
    print(f"Indentation adjusted in: {output_file}")



def run_script():
    """ Main script execution function """
    global list_all_files  # Use the global variable


    root_directory = input("ð Paste the directory path to create a file tree: ").strip()


    if not os.path.exists(root_directory):
        print("â Error: The provided path does not exist. Please try again.")
    else:
        if list_all_files is None:
            # Ask if user wants condensed image sequences or all files listed
            list_choice = input("Do you want to list image sequences in condensed format? (y/n): ").strip().lower()


            # Check for valid input and decide whether to condense or list all files
            if list_choice == "y":
                list_all_files = False
            elif list_choice == "n":
                list_all_files = True
            else:
                print("Invalid input. Defaulting to listing all files.")
                list_all_files = True


        output_lines = []  # Store lines for file writing


        print(f"\nScanning: {root_directory}\n")
        print(f"{root_directory}/")  # Print root directory in terminal (but not saving it)
        list_directory_as_tree(root_directory, "  ", output_lines, list_all_files)


        # Get a unique output file name
        output_file = get_unique_output_file(root_directory)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))  # No extra newline at the end


        # Adjust the indentation by removing 2 spaces
        adjust_indentation_in_file(output_file)


        print(f"\nâ DONE! File tree saved to: \n\n{output_file}\n\n")


    # Ask for a new directory to scan
    run_script()



if __name__ == "__main__":
    run_script()

