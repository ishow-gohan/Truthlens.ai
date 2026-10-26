from pathlib import Path
import pandas as pd

# Locate the folder containing this Python file
BASE_DIR = Path(__file__).resolve().parent
data_dir = BASE_DIR / "data"

print("Python file location:", BASE_DIR)
print("Looking for CSV files in:", data_dir)

# Check the data folder
if not data_dir.exists():
    print("ERROR: The data folder was not found!")
    print("Create the data folder inside:", BASE_DIR)
    raise SystemExit

# Check the CSV files
print("Files in data folder:", [f.name for f in data_dir.iterdir()])

fake_file = data_dir / "Fake.csv.zip"
real_file = data_dir / "True.csv.zip"

if not fake_file.is_file() or not real_file.is_file():
    print("ERROR: Fake.csv or True.csv is missing.")
    print("Make sure both CSV files are inside the data folder.")
    raise SystemExit

# Load datasets
fake = pd.read_csv(fake_file)
real = pd.read_csv(real_file)

# Add labels
fake["label"] = "fake"
real["label"] = "real"

# Combine datasets
df = pd.concat([fake, real], ignore_index=True)

# Check required columns
for col in ["title", "text"]:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col}")

# Handle missing values
df["title"] = df["title"].fillna("").astype(str)
df["text"] = df["text"].fillna("").astype(str)

# Combine title and text
df["text"] = (
    df["title"].str.strip() + " " +
    df["text"].str.strip()
).str.replace(r"\s+", " ", regex=True).str.strip()

# Keep required columns
df = df[["text", "label"]]

# Remove empty articles
df = df[df["text"].str.len() > 0].copy()

# Remove duplicate articles
df["text_key"] = df["text"].str.lower().str.strip()
df = df.drop_duplicates(subset="text_key")
df = df.drop(columns=["text_key"])

# Save cleaned dataset
output_file = data_dir / "cleaned_news.csv"
df.to_csv(output_file, index=False)

# Display summary
print("\nPREPROCESSING COMPLETED!")
print("Total articles:", len(df))
print("\nArticles per label:")
print(df["label"].value_counts())
print("\nMissing values:")
print(df.isnull().sum())
print("\nSaved file:", output_file)