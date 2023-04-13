import pandas as pd
import bertopic
from bertopic.representation import MaximalMarginalRelevance
from sentence_transformers import SentenceTransformer
import numpy as np
from umap import UMAP
from sklearn.decomposition import PCA

#Input Files
embeddings_filename = './embedding/embeddings.npy'
hd5_filename = './hd5/data.h5'

#Output Files
trained_model = './model/dtfTopicModel'
topicsList_csv = './csv/dtf_topicsList.csv'
document2topics_csv = './csv/dtf_document2topics.csv'

#Bertopic parameters
corpus_language="multilingual"
number_of_topics="auto"
ngrams_range =(1, 3) #How many words should be each keyword e.g., Software is one word Engineering another. Software Enginener is a 2 ngram word
 
 #Topics diversity range - 0-1 the more you increase the value the more diverse keywords for each topics are produced. similar keywords vs different.
 #High value could have disadvantages such as overshadowing some topics, but again depends on usecase
topics_diversity=0.1 
#Other partameters are tuned in and could be changed according to usecase

# Load DataFrame from HDF5
doc_df = pd.read_hdf(hd5_filename, key='df')

class CustomBERTopic(bertopic.BERTopic):
    def fit_transform(self, doc_ids, docs, embeddings):
        topics, probs = super().fit_transform(docs, embeddings)
        return doc_ids, topics, probs

    def get_document_info(self, doc_ids, docs):
        topics, probs = super().transform(docs)
        doc_info = super().get_document_info(docs)
        doc_info['Document'] = doc_ids
        return doc_info

def rescale(x, inplace=False):
    """ Rescale an embedding so optimization will not have convergence issues.
    """
    if not inplace:
        x = np.array(x, copy=True)

    x /= np.std(x[:, 0]) * 10000

    return x

sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
representation_model = MaximalMarginalRelevance(diversity=topics_diversity)
# Load saved embeddings
embeddings = np.load(embeddings_filename)

# Initialize and rescale PCA embeddings
pca_embeddings = rescale(PCA(n_components=5).fit_transform(embeddings))

# Start UMAP from PCA embeddings
umap_model = UMAP(
    n_neighbors=15,
    n_components=5,
    min_dist=0.0,
    metric="cosine",
    init=pca_embeddings,
)

# Perform BERTopic modeling with "auto" topics and save the model to file
print("Training the model...")
model = CustomBERTopic(umap_model=umap_model, embedding_model=sentence_model, representation_model=representation_model, nr_topics=number_of_topics, language=corpus_language, n_gram_range=ngrams_range, calculate_probabilities=True)
doc_ids, topics, probs = model.fit_transform(doc_df['doc_id'], doc_df['doc_content'], embeddings)

# Reduce outliers and update topics
print("Reducing the outliers")
new_topics = model.reduce_outliers(doc_df['doc_content'], topics, strategy="embeddings")
model.update_topics(doc_df['doc_content'], topics=new_topics)

print("Saving the model")
model.save(trained_model)

# Save all the topics to csv 
print("Saving topics to csv...")
topics_df = model.get_topic_info()
topics_df.to_csv(topicsList_csv)

# Get document to topic information from BERTopic model
print("Saving document-topics to csv...")
doc_info = model.get_document_info(doc_df['doc_id'], doc_df['doc_content'])
# Save to CSV file
doc_info.to_csv(document2topics_csv, index=False)

print("Done...")