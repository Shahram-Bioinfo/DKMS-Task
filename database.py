import os
import sqlite3
from Bio import SeqIO

# Define the path to the directory containing the FASTA files
directory = "/path/to/your/Fasta/directory/"

# Check if the directory exists
if not os.path.exists(directory):
    print("Error: Directory not found.")
    exit()

# Connect to the SQLite database
conn = sqlite3.connect('sequences.db')
c = conn.cursor()

# Create the sequences table if it does not already exist
c.execute('''
CREATE TABLE IF NOT EXISTS sequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sequence TEXT UNIQUE,
    fixed_sequence TEXT,
    length INTEGER,
    count_of_repeat INTEGER DEFAULT 0
)
''')

# Function to update the database with sequence occurrences
def update_database(subseq, fixed_seq_format, occurrence_count):
    # Check if the sequence already exists in the database
    c.execute('SELECT id, count_of_repeat FROM sequences WHERE sequence = ?', (subseq,))
    result = c.fetchone()

    if result:
        # If the sequence exists, update its count of repeats
        seq_id, existing_count_of_repeat = result
        new_count_of_repeat = existing_count_of_repeat + occurrence_count
        c.execute('UPDATE sequences SET count_of_repeat = ? WHERE id = ?', (new_count_of_repeat, seq_id))
    else:
        # If the sequence does not exist, check for similar sequences
        c.execute('SELECT id, sequence FROM sequences')
        all_sequences = c.fetchall()

        for seq_id, seq in all_sequences:
            # Calculate the edit distance between the current subsequence and each sequence in the database
            edit_dist = sum(1 for x, y in zip(subseq, seq) if x != y) / max(len(subseq), len(seq))

            # If the edit distance is less than or equal to 1% of the length of each sequence,
            # consider them as similar sequences and keep the one with a higher count
            if edit_dist <= 0.01:
                # Compare the counts and keep the one with a higher count
                c.execute('SELECT count_of_repeat FROM sequences WHERE id = ?', (seq_id,))
                existing_count = c.fetchone()[0]

                if occurrence_count < existing_count:
                    # Skip adding the new sequence to the database
                    return

        # Add the new sequence to the database
        c.execute('INSERT INTO sequences (sequence, fixed_sequence, length, count_of_repeat) VALUES (?, ?, ?, ?)', 
                  (subseq, fixed_seq_format, len(subseq), occurrence_count))
    conn.commit()

# Function to extract and process sequences
def extract_sequences(filepath):
    # Define the pairs of start and end sequences to search for
    pairs = [('ACGCT', 'ACCGC'), ('GG', 'CTCGAA'), ('CTTCTGGCAAAA', 'CTCTTTGCAA'),('ACG', 'ACCGC')]
    
    # Loop through each record in the FASTA file
    for record in SeqIO.parse(filepath, "fasta"):
        sequence = str(record.seq)
        
        # Iterate through each pair of start and end sequences
        for start_seq, end_seq in pairs:
            start = sequence.find(start_seq)
            end = sequence.find(end_seq, start)
            
            # If both start and end sequences are found in the record, extract the subsequence
            if start != -1 and end != -1:
                subseq = sequence[start:end + len(end_seq)]
                fixed_seq_format = f"{start_seq}~~~{end_seq}"
                
                # Count occurrences of the subsequence in this file
                occurrence_count = sequence.count(subseq)
                
                # Update the database with the subsequence occurrence
                update_database(subseq, fixed_seq_format, occurrence_count)

# Get the list of FASTA files in the directory
fasta_files = [name for name in os.listdir(directory) if name.endswith(".fasta")]
total_files = len(fasta_files)

# Process each FASTA file in the specified directory
for filename in fasta_files:
    print(f"Processing {filename}...")
    filepath = os.path.join(directory, filename)
    extract_sequences(filepath)

# Close the database connection
conn.close()

