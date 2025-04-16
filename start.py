import subprocess
import csv

csv_file_path = "./browser_use/websites/openai-leadgen-10k.csv"
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if int(row["rank"]) < 7705:
            continue
        website = row["website"]
        subprocess.run(["python", "run.py", website], check=True)
        print(f"Processed {website}")