import pika
import json
import yaml
from spellchecker import SpellChecker
from compound_split import char_split
from nltk import jaccard_distance

QUEUE_NAME = None
BATCH_SIZE = None
RABBITMQ_HOST = None
RABBITMQ_PORT = None
RABBITMQ_USER = None
RABBITMQ_PASS = None
OUTPUT_FOLDER = ''

#Loading PySpellChecker with German corpus to detect Incorrect Words
spell = SpellChecker(language=['en', 'de'])
spell.word_frequency.load_text_file('/mnt/drive/RabbitMQ/removeDictionaryWords4/wordlist-german.txt')

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
        host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials, heartbeat=7200, socket_timeout=7200))

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

    contents = contents.split(' ')
    
    #List of cleaned words
    final_words = []

    dict_desc = '\nFilename: {}\n'.format(filename)
        
    #Removing the duplicate topics
    contents = list(set(contents))
        
    #Iterating over all the words and validating
    for word in contents:
        word_to_check = word.strip()
        
        #Checking if the word is a compound word and if it is than extracting the split with the highest probabilty
        compound_word_prob = char_split.split_compound(word_to_check)
        if (len(compound_word_prob) > 1) and (compound_word_prob[0][0] > 0):
            word_to_check = compound_word_prob[0][1]
            #print('Compound word found:\n{}'.format(word))
            dict_desc += '\nCompound Word Found: \n{}'.format(word)
            
        #Checking for the garbage words which are not part of the dictionary
        dict_word = spell.correction(word_to_check)

        if dict_word == None:
            dict_desc += '\nNoneType found for the word: {}'.format(word_to_check)
            continue

        dict_desc += 'Original Word: {} \tDictionary Word: {} \tJaccard similarity: {}\n'.format(
                word, dict_word, jaccard_distance(set(dict_word), set(word_to_check)))

        if (dict_word == word_to_check) and (not spell.known(spell.edit_distance_1(word_to_check))):
            print('Incorrect word found: {}'.format(word_to_check))
            dict_desc += '\nIncorrect word found: {}'.format(word_to_check)
            continue
        
        #Checking how far is the dictionary word from the original word using Jaccard Distance
        if (dict_word == word_to_check) or (jaccard_distance(set(dict_word), set(word_to_check)) < 0.2):
            final_words.append(word.strip() if ((len(compound_word_prob) > 1) and (compound_word_prob[0][0] > 0)) else dict_word)
            dict_desc += '\nAppending the word: {}'.format(word.strip() if ((len(compound_word_prob) > 1) and (compound_word_prob[0][0] > 0)) else dict_word)
        
    contents = ' '.join(list(set(final_words)))
    print('Appending Content: {}\n\n'.format(contents))

    #Writing the validation results for each topic in a separate file
    with open('/mnt/drive/RabbitMQ/removeDictionaryWordsCorpus/file_stat.txt', 'a+', encoding='utf-8') as file:
        file.writelines(dict_desc)

    # Save the contents to a file with the specified filename
    with open(OUTPUT_FOLDER + filename, 'w') as file:
        file.write(contents)

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
    yaml_config = '/mnt/drive/RabbitMQ/removeDictionaryWordsCorpus/prod_config.yml'
    config = load_config(yaml_config)
    if config:
        set_config_vars(config)
        start_consuming()
