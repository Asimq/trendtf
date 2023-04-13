import numpy as np
from sentence_transformers import SentenceTransformer
import pandas as pd

#Input Files
embeddings_filename = './embedding/embeddings.npy'
hd5_filename = './hd5/data.h5'


# Load DataFrame from HDF5
doc_df = pd.read_hdf(hd5_filename, key='df')

# Prepare embeddings
sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = sentence_model.encode(doc_df['doc_content'], show_progress_bar=True)

# Save embeddings to file
np.save(embeddings_filename, embeddings)
