import pandas as pd
import os
import unicodedata, re

# Input directory containing preprocessed documents
input_dir = ""

# Output HD5 filename
hd5_filename = './hd5/data.h5'

# Read in the preprocessed documents and document IDs
print("Reading preprocessed files")
doc_data = []
for file in os.listdir(input_dir):
    if file.endswith('.txt'):
        with open(os.path.join(input_dir, file), 'r', encoding="utf-8") as f:
            doc = f.read()
            doc = re.sub(r'[^\x20-\x7E]', '', doc)  # Remove non-printable characters
            doc = re.sub(r'\s+', ' ', doc)  # Remove extra whitespace characters
            doc = unicodedata.normalize('NFKD', doc).encode('ascii', 'ignore').decode('utf-8')
            doc_data.append((file, doc))

# Convert the data to a DataFrame
doc_df = pd.DataFrame(doc_data, columns=['doc_id', 'doc_content'])
# Save HD5
print("Saving HD5")
doc_df.to_hdf(hd5_filename, key='df', mode='w')