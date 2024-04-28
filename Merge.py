import os
import subprocess

# Paths
INPUT_DIRECTORY = "/media/ubuntu1/09143127104./Fastq/"
OUTPUT_DIRECTORY = "/media/ubuntu1/09143127104./Merge/"
FAILED_LOG = "/media/ubuntu1/09143127104./failed_files.txt"

# Ensure output directory exists
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

# Function to merge FASTQ files using FLASH
def merge_fastq(file1, file2, output_prefix):
    try:
        subprocess.run([
            "/usr/local/bin/flash",
            file1, file2,
            "-d", OUTPUT_DIRECTORY,
            "-o", output_prefix,
            "--min-overlap", "200",
            "--max-overlap", "400",
            "--quiet"  # Remove this if you want to see FLASH output
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to merge {file1} and {file2}: {e}")
        return False

# Scan directory for FASTQ files and group them
paired_files = {}
for filename in os.listdir(INPUT_DIRECTORY):
    if filename.endswith("_1.fastq"):
        mate_filename = filename.replace("_1.fastq", "_2.fastq")
        if mate_filename in os.listdir(INPUT_DIRECTORY):
            prefix = filename.split('_1.fastq')[0]
            paired_files[prefix] = (os.path.join(INPUT_DIRECTORY, filename), os.path.join(INPUT_DIRECTORY, mate_filename))

# List to track failed files
failed_files = []

# Process each pair
for prefix, files in paired_files.items():
    file1, file2 = files
    if not merge_fastq(file1, file2, prefix):
        failed_files.append(f"{file1} and {file2}")

# Save the names of failed files
if failed_files:
    with open(FAILED_LOG, "w") as f:
        f.write("\n".join(failed_files))

