import os
import csv

class HistoryManager:
    def __init__(self, csv_path):
        self.csv_path = csv_path

    def save_record(self, image_path, date, prediction, confidence):
        with open(self.csv_path, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([image_path, date, prediction, confidence])
    
    def load_records(self):
        if not os.path.exists(self.csv_path):
            return []
        with open(self.csv_path, newline="") as f:
            reader = csv.reader(f)
            return list(reader)
    
    def remove_record(self, image_path):
        if not os.path.exists(self.csv_path):
            return
        rows_to_keep = []
        with open(self.csv_path, "r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 1:
                    continue
                if row[0] != image_path:
                    rows_to_keep.append(row)
        with open(self.csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows_to_keep)

    def remove_record_by_index(self, idx):
        with open(self.csv_path, newline='') as f:
            rows = list(csv.reader(f))
        if 0 <= idx < len(rows):
            del rows[idx]
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)


    def delete_all_records(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
