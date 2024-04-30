# DKMS-Task
This repository features tools for bioinformatics sequence analysis from FASTQ files, enabling the identification of unique sequences absent in existing databases. Designed to enhance bioinformatics research, it forms part of a DKMS training project

# Bioinformatics Sequence Processing Tool
The cornerstone of this repository is a Python script named query.py, meticulously crafted to automate the merging and conversion of FASTQ files, update sequence databases, and generate comprehensive outputs in both FASTA and CSV formats. Designed with versatility in mind, the script seamlessly handles scenarios where paired-end FASTQ files necessitate merging, sequences require extraction based on user-defined criteria, and database updates are imperative.

# Prerequisites

Before deploying this script, ensure your system meets the following prerequisites:

- **Python 3.x**: Ensure Python 3 is installed on your system as the script is compatible with Python 3.
- **BioPython Library**: Required for biological computation tasks.
- **SQLite3**: Utilized for database management purposes.
- **FLASH Tool**: Necessary for merging FASTQ files efficiently.

## Installation of Prerequisites

You can install the required libraries and tools using the commands below:

### Python Packages

Install BioPython and SQLite3 using pip:

```bash
pip install biopython
pip install pysqlite3
```
### Installing FLASH Tool
For Debian-based systems, use apt-get to install the FLASH tool:

 ```bash
sudo apt-get install flash
```

Refer to the [official FLASH documentation](https://ccb.jhu.edu/software/FLASH/) for installation instructions on other systems.



# Installation

To set up this project locally, follow these steps:

1. **Clone the repository**
   
   Start by cloning the repository to your local machine. Open a terminal and run the following command:

```bash
git clone https://github.com/Shahram-Bioinfo/DKMS-Task.git
```   
This command downloads all the project files to a directory named DKMS-Task on your computer.

2. Navigate to the project directoryChange into the project directory with:

```bash
cd DKMS-Task
```
# Usage
To execute the script, provide two FASTQ files as input. Ensure accessibility of these files to the script and possession of the requisite permissions for reading.

1. **Configure Script Parameters** (if necessary):
   Customize the script parameters and paths to fit your specific requirements.

2. **Executing the Script**:
   Navigate to the directory containing the script in your terminal.
   Run the script using Python:

```bash
python3 query.py
```

   You'll be prompted to input the paths to your FASTQ files:
```bash
Enter the path to the first FASTQ file: /path/to/your/first_file.fastq
Enter the path to the second FASTQ file: /path/to/your/second_file.fastq
```

   *Note*: Tow FASTQ files for testing are available.

3. **Output**:
   The script manages the merging of FASTQ files, database updates with new sequences, and exportation of these novel sequences to a FASTA file, alongside exporting the entire database to a CSV file.
   Outputs are stored within the "Results" directory, conveniently situated alongside the script.

# Features
 - **FASTQ Processing**: Seamlessly merges paired-end FASTQ files using the FLASH tool.
 - **Database Updates**: Integrates new sequences into a SQLite database or updates existing entries.
 - **Output Generation**: Produces new sequences in FASTA format and exports the entire sequence database to a CSV file.
 - **Backups**: Ensures the safety of the database with pre- and post-update backups.

# Contact
For inquiries and further assistance, feel free to contact aliyari.shahram@gmail.com.
