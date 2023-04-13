import pika
import json
import yaml
import csv
import re
import math
import nltk
nltk.download('stopwords')
from collections import defaultdict
from nltk.corpus import stopwords

QUEUE_NAME = None
BATCH_SIZE = None
RABBITMQ_HOST = None
RABBITMQ_PORT = None
RABBITMQ_USER = None
RABBITMQ_PASS = None
OUTPUT_FOLDER = ''
TERMINOLOGY = None
MAX_KEYPHRASES = 0
NUMBER_OF_DOCUMENTS_IN_CORPUS = 0
STOP_WORDS_DE = None
STOP_WORDS_EN = None

def load_stopwords(stopwords_list, file_path):
    stopwords_set = set(stopwords_list)
    with open(file_path, encoding='utf-8') as f:
        stopwords_set.update(f.read().split())
    return stopwords_set


def load_terminology(file_path):
    terminology = {}
    with open(file_path, encoding='latin-1') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            prepilot = row['pilot'].lower()
            pilot_lemma = row['lemma']
            pilot_freq = int(row['freq'])
            pilot_spec = float(row['spec'].replace(',','.'))
            terminology[row['pilot']] = {'prepilot': prepilot, 'lemma': pilot_lemma, 'freq': pilot_freq, 'spec': pilot_spec}
    return terminology

def extract_keyphrases(content, terminology, stop_words_de, stop_words_en, max_keyphrases, number_of_documents_in_corpus):
   
    content = content.lower()

    # Find all pilots and their term frequency
    tf = defaultdict(int)
    for pilot in terminology:
        if 'prepilot' in terminology[pilot]:
            prepilot = terminology[pilot]['prepilot']
            pattern = r'\b{}\b'.format(re.escape(prepilot))
            matches = re.findall(pattern, content)
            tf[pilot] += len(matches)

    # Calculate the IDF for each pilot
    idf = {pilot: math.log(number_of_documents_in_corpus / terminology[pilot]['freq']) for pilot in tf}
    # Calculate the TF-IDF for each pilot
    tfidf = {pilot: (tf[pilot] / len(tf)) * idf[pilot] * terminology[pilot]['spec'] for pilot in tf}

    # Sort the pilots by their TF-IDF score
    sorted_pilots = sorted(tfidf, key=tfidf.get, reverse=True)
    if max_keyphrases > len(sorted_pilots):
        max_keyphrases = len(sorted_pilots)
    sorted_pilots = sorted_pilots[:max_keyphrases]

    # Extract the keyphrases from the top pilots
    keyphrases = []
    for pilot in sorted_pilots:
        terms = terminology[pilot]['lemma']
        if isinstance(terms, str):
            terms = [terms]
        filtered_terms = []
        for term in terms:
            if term not in stop_words_de and term not in stop_words_en:
                filtered_terms.append(term)
        keyphrase = ''.join(filtered_terms)
        keyphrases.append(keyphrase)


    return keyphrases


def load_config(filename):
    try:
        with open(filename, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Could not find {filename}.")
        return {}
    return config

def set_config_vars(config):
    global QUEUE_NAME, BATCH_SIZE, RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASS, OUTPUT_FOLDER, TERMINOLOGY, MAX_KEYPHRASES, NUMBER_OF_DOCUMENTS_IN_CORPUS, STOP_WORDS_DE, STOP_WORDS_EN
    QUEUE_NAME = config.get('QUEUE_NAME', QUEUE_NAME)
    BATCH_SIZE = config.get('BATCH_SIZE', BATCH_SIZE)
    RABBITMQ_HOST = config.get('RABBITMQ_HOST', RABBITMQ_HOST)
    RABBITMQ_PORT = config.get('RABBITMQ_PORT', RABBITMQ_PORT)
    RABBITMQ_USER = config.get('RABBITMQ_USER', RABBITMQ_USER)
    RABBITMQ_PASS = config.get('RABBITMQ_PASS', RABBITMQ_PASS)
    OUTPUT_FOLDER = config.get('OUTPUT_FOLDER', OUTPUT_FOLDER)
    terminology_file = '/mnt/drive/dtf_text/cs/computerscienceTerm.tsv'
    TERMINOLOGY = load_terminology(terminology_file)
    MAX_KEYPHRASES = 50
    NUMBER_OF_DOCUMENTS_IN_CORPUS = 2311
    stop_words_de_file = '/mnt/drive/RabbitMQ/extract_cs_keyphrases/german_stopwords_extention.txt'
    stop_words_en_file = '/mnt/drive/RabbitMQ/extract_cs_keyphrases/english_stopwords_extention.txt'
    STOP_WORDS_DE = load_stopwords(stopwords.words('german'), stop_words_de_file)
    STOP_WORDS_EN = load_stopwords(stopwords.words('english'), stop_words_en_file)

def connect_to_queue():
    # Establish connection to RabbitMQ server
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials, heartbeat=1800, socket_timeout=1800))
    
    channel = connection.channel()
    # Create a queue for receiving tasks from distributor
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    return channel

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
    
    keyphrases = extract_keyphrases(contents, TERMINOLOGY, STOP_WORDS_DE, STOP_WORDS_EN, MAX_KEYPHRASES, NUMBER_OF_DOCUMENTS_IN_CORPUS)

    # Save the contents to a file with the specified filename
    with open(OUTPUT_FOLDER + filename, 'w') as file:
        file.write(' '.join(keyphrases))

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
    yaml_config = '/mnt/drive/RabbitMQ/extract_cs_keyphrases/prod_config.yml'
    config = load_config(yaml_config)
    if config:
        set_config_vars(config)
        start_consuming()
