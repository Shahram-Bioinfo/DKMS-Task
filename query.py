import os
import subprocess
import shutil
import datetime
import sqlite3
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import csv

def get_common_prefix(file1, file2):
    return os.path.commonprefix([file1, file2]).rstrip('_')

def backup_database(db_path, result_dir, backup_suffix):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_suffix}_{timestamp}.db"
    backup_path = os.path.join(result_dir, backup_file)
    if os.path.exists(db_path):
        try:
            shutil.copy2(db_path, backup_path)
            print(f"Backup of the database created at {backup_path}")
        except IOError as e:
            print(f"Failed to create database backup: {e}")
    else:
        print("Database file does not exist, cannot create backup.")

def run_flash_and_convert(file1, file2, prefix, result_dir):
    output_fastq = os.path.join(result_dir, f"{prefix}_combined.fastq")
    output_fasta = os.path.join(result_dir, f"{prefix}_combined.fasta")
    flash_command = ["/usr/local/bin/flash", file1, file2, "--to-stdout", "-m", "200", "-M", "400"]
    try:
        with open(output_fastq, "wb") as out_file:
            subprocess.run(flash_command, check=True, stdout=out_file)
        print("FLASH run successfully, output saved to", output_fastq)
        records = SeqIO.parse(output_fastq, "fastq")
        SeqIO.write(records, output_fasta, "fasta")
        print("Conversion to FASTA completed:", output_fasta)
        return output_fasta
    except subprocess.CalledProcessError as e:
        print("Error running FLASH:", e)
        return None
    except IOError as e:
        print(f"Error writing file {output_fastq}: {e}")
        return None

def initialize_database(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS sequences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sequence TEXT UNIQUE,
        fixed_sequence TEXT,
        length INTEGER,
        count_of_repeat INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()

def update_database(conn, subseq, fixed_seq_format, occurrence_count):
    c = conn.cursor()
    c.execute('SELECT id, count_of_repeat FROM sequences WHERE sequence = ?', (subseq,))
    result = c.fetchone()
    new_sequence_added = False

    if result:
        seq_id, existing_count_of_repeat = result
        c.execute('UPDATE sequences SET count_of_repeat = count_of_repeat + ? WHERE id = ?', (occurrence_count, seq_id))
    else:
        c.execute('INSERT INTO sequences (sequence, fixed_sequence, length, count_of_repeat) VALUES (?, ?, ?, ?)', 
                  (subseq, fixed_seq_format, len(subseq), occurrence_count))
        new_sequence_added = True
    conn.commit()
    return new_sequence_added

def extract_sequences(filepath, conn, result_dir):
    pairs = [('ACGCT', 'ACCGC'), ('GG', 'CTCGAA'), ('CTTCTGGCAAAA', 'CTCTTTGCAA'), ('ACG', 'ACCGC')]
    new_sequences = []
    new_sequences_count = 0
    
    for record in SeqIO.parse(filepath, "fasta"):
        sequence = str(record.seq)
        for start_seq, end_seq in pairs:
            start = sequence.find(start_seq)
            end = sequence.find(end_seq, start + len(start_seq))
            if start != -1 and end != -1:
                subseq = sequence[start + len(start_seq):end]
                fixed_seq_format = f"{start_seq}~~~{end_seq}"
                occurrence_count = sequence.count(subseq)
                if update_database(conn, subseq, fixed_seq_format, occurrence_count):
                    new_sequences.append(SeqRecord(Seq(subseq), id=record.id, description="New sequence found"))
                    new_sequences_count += 1

    if new_sequences:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_fasta_filename = f"new_sequences_{timestamp}.fasta"
        new_fasta_path = os.path.join(result_dir, new_fasta_filename)
        SeqIO.write(new_sequences, new_fasta_path, "fasta")
        print(f"{new_sequences_count} new sequences added and saved to {new_fasta_path}.")

def export_database_to_csv(db_path, result_dir):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM sequences")
    data = c.fetchall()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"database_export_{timestamp}.csv"
    csv_path = os.path.join(result_dir, csv_filename)

    with open(csv_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['ID', 'Sequence', 'Fixed Sequence', 'Length', 'Count of Repeat'])
        csvwriter.writerows(data)

    print(f"Database exported to CSV at {csv_path}")
    conn.close()

def process_files(file1, file2):
    prefix = get_common_prefix(os.path.basename(file1), os.path.basename(file2))
    result_dir = os.path.join(os.getcwd(), "Results")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    db_path = os.path.join(os.getcwd(), "sequences.db")
    
    initialize_database(db_path)
    
    # Backup before any updates
    backup_database(db_path, result_dir, "pre_update")
    
    fasta_path = run_flash_and_convert(file1, file2, prefix, result_dir)
    if fasta_path:
        conn = sqlite3.connect(db_path)
        try:
            extract_sequences(fasta_path, conn, result_dir)
        finally:
            conn.close()
        
        # Backup after updates
        backup_database(db_path, result_dir, "post_update")
        
        # Export database to CSV
        export_database_to_csv(db_path, result_dir)

file1 = input("Enter the path to the first FASTQ file: ")
file2 = input("Enter the path to the second FASTQ file: ")
process_files(file1, file2)

