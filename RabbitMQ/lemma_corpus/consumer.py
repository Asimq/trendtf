import pika
import json
import yaml
import spacy
from nltk.tokenize import word_tokenize
import os
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

QUEUE_NAME = None
BATCH_SIZE = None
RABBITMQ_HOST = None
RABBITMQ_PORT = None
RABBITMQ_USER = None
RABBITMQ_PASS = None
OUTPUT_FOLDER = ''
metadata_dir = "/mnt/drive/metadata/ExtractedMetaDataJson/ExtractedMetaDataJson/"
# Load the appropriate spacy model for each language
nlp_en = spacy.load("en_core_web_sm")
nlp_de = spacy.load("de_core_news_sm")
stop_words_de_file = '/mnt/drive/RabbitMQ/extract_cs_keyphrases/german_stopwords_extention.txt'
stop_words_en_file = '/mnt/drive/RabbitMQ/extract_cs_keyphrases/english_stopwords_extention.txt'

def load_stopwords(stopwords_list, file_path):
    stopwords_set = set(stopwords_list)
    with open(file_path, encoding='utf-8') as f:
        stopwords_set.update(f.read().split())
    return stopwords_set

STOP_WORDS_DE = load_stopwords(stopwords.words('german'), stop_words_de_file)
STOP_WORDS_EN = load_stopwords(stopwords.words('english'), stop_words_en_file)

def load_config(filename):
    try:
        with open(filename, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Could not find {filename}.")
        return {}

    return config

def set_config_vars(config):
    global QUEUE_NAME, BATCH_SIZE, RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASS, OUTPUT_FOLDER
    QUEUE_NAME = config.get('QUEUE_NAME', QUEUE_NAME)
    BATCH_SIZE = config.get('BATCH_SIZE', BATCH_SIZE)
    RABBITMQ_HOST = config.get('RABBITMQ_HOST', RABBITMQ_HOST)
    RABBITMQ_PORT = config.get('RABBITMQ_PORT', RABBITMQ_PORT)
    RABBITMQ_USER = config.get('RABBITMQ_USER', RABBITMQ_USER)
    RABBITMQ_PASS = config.get('RABBITMQ_PASS', RABBITMQ_PASS)
    OUTPUT_FOLDER = config.get('OUTPUT_FOLDER', OUTPUT_FOLDER)

def connect_to_queue():
    # Establish connection to RabbitMQ server
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials))

    channel = connection.channel()
    # Create a queue for receiving tasks from distributor
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    return channel

def lemmatize(filename, content):
    # Determine the name of the corresponding JSON file
        json_filename = os.path.splitext(filename)[0] + ".json"
        json_path = os.path.join(metadata_dir, json_filename)

        # Load the metadata for the file from the JSON file
        try:
            with open(json_path, "r") as json_file:
                metadata = json.load(json_file)
        except FileNotFoundError:
            metadata = {"language": {"language": "de"}}

        # Determine the language of the content
        language = metadata.get("language", {}).get("language", "de")

        # Load the appropriate spacy model for the language
        if language == "de":
            nlp = nlp_de
        else:
            nlp = nlp_en
            
        # Tokenize the content into words
        words = word_tokenize(content)

        # Lemmatize each word using the appropriate spacy model
        lemmatized_words = []
        for word in words:
            # Ignore proper nouns (PROPN)
            doc = nlp(word)
            if doc[0].pos_ != "PROPN":
                # Check if the word is not a stopword in both STOP_WORDS_DE and STOP_WORDS_EN
                if word.lower() not in STOP_WORDS_DE and word.lower() not in STOP_WORDS_EN:
                    lemma = doc[0].lemma_
                    lemmatized_words.append(lemma)
                    
        # Join the lemmatized words back into a string
        lemmatized_content = " ".join(lemmatized_words)
        return lemmatized_content

# Define the callback function to handle incoming messages
def callback(ch, method, properties, body):
    # Decode the JSON object from the message body
    task = json.loads(body.decode('utf-8'))
    filename = task['filename']
    contents = task['contents']

    # Print the task to the console
    """WRITE YOUR TASK HERE OR REFER IT FROM ANOTHER FILE
    As an example the code is just priting the filename
	"""
    print(f"Received task {filename} from distributor")

    lemmas = lemmatize(filename, contents)
    # Save the contents to a file with the specified filename
    with open(OUTPUT_FOLDER + filename, 'w', encoding="utf-8") as file:
        file.write(lemmas)

    # Acknowledge the message to remove it from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    # Start consuming messages from the queue
    channel = connect_to_queue()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print('Waiting for tasks...')
    channel.start_consuming()

if __name__ == '__main__':

    #Define yaml config file and load it here    
    yaml_config = '/mnt/drive/RabbitMQ/lemma_corpus/prod_config.yml'
    config = load_config(yaml_config)
    if config:
        set_config_vars(config)
        start_consuming()
