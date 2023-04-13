"""Importing Libraries"""
import os
from string import punctuation
from langdetect import detect
import re

### NLTK ###
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
import spacy


class PreprocessingDocuments():
    """Preprocessing Document class perform several pre processing steps to clean the textual data
    and make it ready to feed data to the model."""

    def __init__(self, basepath):
        """Set up directory path which contain full extracted text of documents.

        Parameters:
        basepath (string): folder path which contain full extracted text of documents
       """

        self.basepath = basepath

        ###Lemmatize using WordNet's built-in morphy function. Returns the input word unchanged if it cannot be found in WordNet.
        #self.lemmatizer = WordNetLemmatizer()
        
        #Loading the Spacy German corpus for tagging purposes
        self.spacy_de = spacy.load('de_core_news_sm')

    def listAllDocs(self):
        """Function that returns list of all documents in the base path
       """
        return os.listdir(self.basepath)

    def tokenArray(self, doc_name):
        """Function that the read the content of the document, preprocess it and detect the language of document

        Parameters:
        doc_name (String): name of file being currently parsed

        Returns:
        List: return preprocessed text of document, document name and language of document

       """
        documentToken = []
        full_path = self.basepath + doc_name
        f = open(full_path, "rt", encoding="utf8")
        data = str(f.read())
        f.close()
        tokenData = self.preProcessing(data)  # preprocess the text
        documentToken.append(tokenData)
        documentToken.append(doc_name)
        documentToken.append(detect(data))
        return documentToken
    
    def removeUnnecessaryWords(self, filedata):
        """Function to remove the Unnecessary words like Proper Nouns, Adjective etc. 
        from the text

        Parameters
        ----------
        filedata : (String)
            Text from the file which has to be processed

        Returns
        -------
        String:
            return processed text without Proper Nouns

        """
        
        tags_to_remove = ['ADJ', 'AUX', 'PUNCT', 'ADP', 'DET','VERB','ADV', 'PROPN', 'INTJ', 'PART', 'PRON', 'SPACE']
        
        single_string = self.spacy_de(filedata)
        
        edited_sentence = [word.orth_ for word in single_string if word.pos_ not in tags_to_remove]
        
        return ' '.join(edited_sentence)

    def preProcessing(self, filedata):
        """Function that the read the content of the document, preprocess it and detect the language of document

        Parameters:
        filedata (String): text of the file being currently parsed

        Returns:
        List: return preprocessed tokenized text of document

       """

        input_lower = filedata.lower()  # function to transform text of document to lower case
        words = input_lower.split()  # function to split the text of document based on newline character '\n'
        tokenwords = self.tokens(' '.join(words))  # function to tokenize the text of document
        return tokenwords

    def remove_numbers(self, text):
        """Function that removes the digits from the content of the document

        Parameters:
        text (String): text of the file being currently parsed

        Returns:
        String: return preprocessed text without digits

       """
        result = re.sub(r'\d+', '', str(text))
        return result

    def spaces(self, text):
        """Function that removes the new line character from the content of the document

        Parameters:
        text (String): text of the file being currently parsed

        Returns:
        String: return preprocessed text without newline character

       """

        return text.replace(r"\n+", " ")

    def remove_punctuation(self, text):
        """Function that removes the punctuations from the content of the document. Underscore "-" was removed
        from the list of punctuations else the topics of documents contain miss spelled words 

        Parameters:
        text (String): text of the file being currently parsed

        Returns:
        String: return preprocessed text without punctuations
       """

        punctuations_subset = punctuation.replace("-", "")
        translator = str.maketrans('', '', punctuations_subset)
        return text.translate(translator)

    def remove_whitespace(self, text):
        """Function that removes the whitespace from the content of the document

        Parameters:
        text (String): text of the file being currently parsed

        Returns:
        String: return preprocessed text without whitespaces
       """

        return " ".join(text.split())

    def specialCharector(self, text):
        """Function that removes the special character from the content of the document

        Parameters:
        text (String): text of the file being currently parsed

        Returns:
        String: return preprocessed text without special characters
       """
       
        text = re.sub(r'\W+[-]*\W+', ' ', text)
        return re.sub(r"[^a-zA-Z0-9äöüÄÖÜß-]+", ' ', text)

    def removeThreechar(self, text):
        """Function that removes the words less than three character long from the content of the document

        Parameters:
        text (String): text of the file being currently parsed

        Returns:
        String: return preprocessed text without three character long words
       """
        return re.sub(r'\b\w{1,3}\b', '', text)

    def tokens(self, text):
        """Function that tokenize the content of the document

        Parameters:
        text (String): text of the file being currently parsed

        Returns:
        list: return preprocessed tokenize text
       """
        return word_tokenize(text)

    def removeStopwordsEnglish(self, text_tokens):
        """Function that removes the english stopwords from the preprocessed tokenize text of the document. We also extended
        the NLTK stopword list with new stop words which occurred commonly in the topic modelling results.

        Parameters:
        text_tokens (list): preprocessed tokenize text

        Returns:
        list: return preprocessed tokenize text without english stopwords
       """

        stop_words = stopwords.words('english')
        # extended list of stopwords
        stop_words.extend(
            ['proc', 'increase', 'unfortunately', 'this', 'wafe', 'variou', 'value', 'tion', 'stable', 'nite', 'p1p2',
             'recent', 'site', 'hahn', 'ramesh', 'write', 'type', 'background', 'speci', 'anti', 'completeness', 'link',
             'usion', 'ability', 'advantage', 'catalan', 'order', 'completeness', 'complete'])
        stop_words.extend(
            ["woods", "0o", "0s", "3a", "3b", "3d", "6b", "6o", "a", "a1", "a2", "a3", "a4", "ab", "able", "about",
             "above", "abst", "ac", "accordance", "according", "accordingly", "across", "act", "actually", "ad",
             "added", "adj", "ae", "af", "affected", "affecting", "affects", "after", "afterwards", "ag", "again",
             "against", "ah", "ain", "ain't", "aj", "al", "all", "allow", "allows", "almost", "alone", "along",
             "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and",
             "announce", "another", "any", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway", "anyways",
             "anywhere", "ao", "ap", "apart", "apparently", "appear", "appreciate", "appropriate", "approximately",
             "ar", "are", "aren", "arent", "aren't", "arise", "around", "as", "a's", "aside", "ask", "asking",
             "associated", "at", "au", "auth", "av", "available", "aw", "away", "awfully", "ax", "ay", "az", "b", "b1",
             "b2", "b3", "ba", "back", "bc", "bd", "be", "became", "because", "become", "becomes", "becoming", "been",
             "before", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "being", "believe",
             "below", "beside", "besides", "best", "better", "between", "beyond", "bi", "bill", "biol", "bj", "bk",
             "bl", "bn", "both", "bottom", "bp", "br", "brief", "briefly", "bs", "bt", "bu", "but", "bx", "by", "c",
             "c1", "c2", "c3", "ca", "call", "came", "can", "cannot", "cant", "can't", "cause", "causes", "cc", "cd",
             "ce", "certain", "certainly", "cf", "cg", "ch", "changes", "ci", "cit", "cj", "cl", "clearly", "cm",
             "c'mon", "cn", "co", "com", "come", "comes", "con", "concerning", "consequently", "consider",
             "considering", "contain", "containing", "contains", "corresponding", "could", "couldn", "couldnt",
             "couldn't", "course", "cp", "cq", "cr", "cry", "cs", "c's", "ct", "cu", "currently", "cv", "cx", "cy",
             "cz", "d", "d2", "da", "date", "dc", "dd", "de", "definitely", "describe", "described", "despite",
             "detail", "df", "di", "did", "didn", "didn't", "different", "dj", "dk", "dl", "do", "does", "doesn",
             "doesn't", "doing", "don", "done", "don't", "down", "downwards", "dp", "dr", "ds", "dt", "du", "due",
             "during", "dx", "dy", "e", "e2", "e3", "ea", "each", "ec", "ed", "edu", "ee", "ef", "effect", "eg", "ei",
             "eight", "eighty", "either", "ej", "el", "eleven", "else", "elsewhere", "em", "empty", "en", "end",
             "ending", "enough", "entirely", "eo", "ep", "eq", "er", "es", "especially", "est", "et", "et-al", "etc",
             "eu", "ev", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly",
             "example", "except", "ey", "f", "f2", "fa", "far", "fc", "few", "ff", "fi", "fifteen", "fifth", "fify",
             "fill", "find", "fire", "first", "five", "fix", "fj", "fl", "fn", "fo", "followed", "following", "follows",
             "for", "former", "formerly", "forth", "forty", "found", "four", "fr", "from", "front", "fs", "ft", "fu",
             "full", "further", "furthermore", "fy", "g", "ga", "gave", "ge", "get", "gets", "getting", "gi", "give",
             "given", "gives", "giving", "gj", "gl", "go", "goes", "going", "gone", "got", "gotten", "gr", "greetings",
             "gs", "gy", "h", "h2", "h3", "had", "hadn", "hadn't", "happens", "hardly", "has", "hasn", "hasnt",
             "hasn't", "have", "haven", "haven't", "having", "he", "hed", "he'd", "he'll", "hello", "help", "hence",
             "her", "here", "hereafter", "hereby", "herein", "heres", "here's", "hereupon", "hers", "herself", "hes",
             "he's", "hh", "hi", "hid", "him", "himself", "his", "hither", "hj", "ho", "home", "hopefully", "how",
             "howbeit", "however", "how's", "hr", "hs", "http", "hu", "hundred", "hy", "i", "i2", "i3", "i4", "i6",
             "i7", "i8", "ia", "ib", "ibid", "ic", "id", "i'd", "ie", "if", "ig", "ignored", "ih", "ii", "ij", "il",
             "i'll", "im", "i'm", "immediate", "immediately", "importance", "important", "in", "inasmuch", "inc",
             "indeed", "index", "indicate", "indicated", "indicates", "information", "inner", "insofar", "instead",
             "interest", "into", "invention", "inward", "io", "ip", "iq", "ir", "is", "isn", "isn't", "it", "itd",
             "it'd", "it'll", "its", "it's", "itself", "iv", "i've", "ix", "iy", "iz", "j", "jj", "jr", "js", "jt",
             "ju", "just", "k", "ke", "keep", "keeps", "kept", "kg", "kj", "km", "know", "known", "knows", "ko", "l",
             "l2", "la", "largely", "last", "lately", "later", "latter", "latterly", "lb", "lc", "le", "least", "les",
             "less", "lest", "let", "lets", "let's", "lf", "like", "liked", "likely", "line", "little", "lj", "ll",
             "ll", "ln", "lo", "look", "looking", "looks", "los", "lr", "ls", "lt", "ltd", "m", "m2", "ma", "made",
             "mainly", "make", "makes", "many", "may", "maybe", "me", "mean", "means", "meantime", "meanwhile",
             "merely", "mg", "might", "mightn", "mightn't", "mill", "million", "mine", "miss", "ml", "mn", "mo", "more",
             "moreover", "most", "mostly", "move", "mr", "mrs", "ms", "mt", "mu", "much", "mug", "must", "mustn",
             "mustn't", "my", "myself", "n", "n2", "na", "name", "namely", "nay", "nc", "nd", "ne", "near", "nearly",
             "necessarily", "necessary", "need", "needn", "needn't", "needs", "neither", "never", "nevertheless", "new",
             "next", "ng", "ni", "nine", "ninety", "nj", "nl", "nn", "no", "nobody", "non", "none", "nonetheless",
             "noone", "nor", "normally", "nos", "not", "noted", "nothing", "novel", "now", "nowhere", "nr", "ns", "nt",
             "ny", "o", "oa", "ob", "obtain", "obtained", "obviously", "oc", "od", "of", "off", "often", "og", "oh",
             "oi", "oj", "ok", "okay", "ol", "old", "om", "omitted", "on", "once", "one", "ones", "only", "onto", "oo",
             "op", "oq", "or", "ord", "os", "ot", "other", "others", "otherwise", "ou", "ought", "our", "ours",
             "ourselves", "out", "outside", "over", "overall", "ow", "owing", "own", "ox", "oz", "p", "p1", "p2", "p3",
             "page", "pagecount", "pages", "par", "part", "particular", "particularly", "pas", "past", "pc", "pd", "pe",
             "per", "perhaps", "pf", "ph", "pi", "pj", "pk", "pl", "placed", "please", "plus", "pm", "pn", "po",
             "poorly", "possible", "possibly", "potentially", "pp", "pq", "pr", "predominantly", "present",
             "presumably", "previously", "primarily", "probably", "promptly", "proud", "provides", "ps", "pt", "pu",
             "put", "py", "q", "qj", "qu", "que", "quickly", "quite", "qv", "r", "r2", "ra", "ran", "rather", "rc",
             "rd", "re", "readily", "really", "reasonably", "recent", "recently", "ref", "refs", "regarding",
             "regardless", "regards", "related", "relatively", "research", "research-articl", "respectively",
             "resulted", "resulting", "results", "rf", "rh", "ri", "right", "rj", "rl", "rm", "rn", "ro", "rq", "rr",
             "rs", "rt", "ru", "run", "rv", "ry", "s", "s2", "sa", "said", "same", "saw", "say", "saying", "says", "sc",
             "sd", "se", "sec", "second", "secondly", "section", "see", "seeing", "seem", "seemed", "seeming", "seems",
             "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "sf", "shall",
             "shan", "shan't", "she", "shed", "she'd", "she'll", "shes", "she's", "should", "shouldn", "shouldn't",
             "should've", "show", "showed", "shown", "showns", "shows", "si", "side", "significant", "significantly",
             "similar", "similarly", "since", "sincere", "six", "sixty", "sj", "sl", "slightly", "sm", "sn", "so",
             "some", "somebody", "somehow", "someone", "somethan", "something", "sometime", "sometimes", "somewhat",
             "somewhere", "soon", "sorry", "sp", "specifically", "specified", "specify", "specifying", "sq", "sr", "ss",
             "st", "still", "stop", "strongly", "sub", "substantially", "successfully", "such", "sufficiently",
             "suggest", "sup", "sure", "sy", "system", "sz", "t", "t1", "t2", "t3", "take", "taken", "taking", "tb",
             "tc", "td", "te", "tell", "ten", "tends", "tf", "th", "than", "thank", "thanks", "thanx", "that",
             "that'll", "thats", "that's", "that've", "the", "their", "theirs", "them", "themselves", "then", "thence",
             "there", "thereafter", "thereby", "thered", "therefore", "therein", "there'll", "thereof", "therere",
             "theres", "there's", "thereto", "thereupon", "there've", "these", "they", "theyd", "they'd", "they'll",
             "theyre", "they're", "they've", "thickv", "thin", "think", "third", "this", "thorough", "thoroughly",
             "those", "thou", "though", "thoughh", "thousand", "three", "throug", "through", "throughout", "thru",
             "thus", "ti", "til", "tip", "tj", "tl", "tm", "tn", "to", "together", "too", "took", "top", "toward",
             "towards", "tp", "tq", "tr", "tried", "tries", "truly", "try", "trying", "ts", "t's", "tt", "tv", "twelve",
             "twenty", "twice", "two", "tx", "u", "u201d", "ue", "ui", "uj", "uk", "um", "un", "under", "unfortunately",
             "unless", "unlike", "unlikely", "until", "unto", "uo", "up", "upon", "ups", "ur", "us", "use", "used",
             "useful", "usefully", "usefulness", "uses", "using", "usually", "ut", "v", "va", "value", "various", "vd",
             "ve", "ve", "very", "via", "viz", "vj", "vo", "vol", "vols", "volumtype", "vq", "vs", "vt", "vu", "w",
             "wa", "want", "wants", "was", "wasn", "wasnt", "wasn't", "way", "we", "wed", "we'd", "welcome", "well",
             "we'll", "well-b", "went", "were", "we're", "weren", "werent", "weren't", "we've", "what", "whatever",
             "what'll", "whats", "what's", "when", "whence", "whenever", "when's", "where", "whereafter", "whereas",
             "whereby", "wherein", "wheres", "where's", "whereupon", "wherever", "whether", "which", "while", "whim",
             "whither", "who", "whod", "whoever", "whole", "who'll", "whom", "whomever", "whos", "who's", "whose",
             "why", "why's", "wi", "widely", "will", "willing", "wish", "with", "within", "without", "wo", "won",
             "wonder", "wont", "won't", "words", "world", "would", "wouldn", "wouldnt", "wouldn't", "www", "x", "x1",
             "x2", "x3", "xf", "xi", "xj", "xk", "xl", "xn", "xo", "xs", "xt", "xv", "xx", "y", "y2", "yes", "yet",
             "yj", "yl", "you", "youd", "you'd", "you'll", "your", "youre", "you're", "yours", "yourself", "yourselves",
             "you've", "yr", "ys", "yt", "z", "zero", "zi", "zz"])
        stop_words.extend(
            ["yellow", 'advantage', 'instance', 'property', 'achievable', 'emphasis', "achieveapart", "achieving",
             "achieves", "achieved", "worked", "yielding", "zone", "wrong", "work", "achieve", "based", "budget",
             "basis", "goverment", "analyzed", "abstract", "question", "verifying", "resource", "fouzitabetdbfzde"])

        tokens_without_sw = [word for word in text_tokens if not word in stop_words]
        return tokens_without_sw

    def removeStopwordsGerman(self, text_tokens):
        """Function that removes the german stopwords from the preprocessed tokenize text of the document. We also extended
        the NLTK stopword list with new stop words which occurred commonly in the topic modelling results.

        Parameters:
        text_tokens (list): preprocessed tokenize text

        Returns:
        list: return preprocessed tokenize text without german stopwords
       """

        stop_words = stopwords.words('german')
        stop_words.extend(
            ['ab', 'aber', 'alle', 'allein', 'allem', 'allen', 'aller', 'allerdings', 'allerlei', 'alles', 'allmählich',
             'allzu', 'als', 'alsbald', 'also', 'am', 'an', 'and', 'ander', 'andere', 'anderem', 'anderen', 'anderer',
             'andererseits', 'anderes', 'anderm', 'andern', 'andernfalls', 'anders', 'anstatt', 'auch', 'auf', 'aus',
             'ausgenommen', 'ausser', 'ausserdem', 'außer', 'außerdem', 'außerhalb', 'bald', 'bei', 'beide', 'beiden',
             'beiderlei', 'beides', 'beim', 'beinahe', 'bereits', 'besonders', 'besser', 'beträchtlich', 'bevor',
             'bezüglich', 'bin', 'bis', 'bisher', 'bislang', 'bist', 'bloß', 'bsp.', 'bzw', 'ca', 'ca.', 'content',
             'da', 'dabei', 'dadurch', 'dafür', 'dagegen', 'daher', 'dahin', 'damals', 'damit', 'danach', 'daneben',
             'dann', 'daran', 'darauf', 'daraus', 'darin', 'darum', 'darunter', 'darüber', 'darüberhinaus', 'das',
             'dass', 'dasselbe', 'davon', 'davor', 'dazu', 'daß', 'dein', 'deine', 'deinem', 'deinen', 'deiner',
             'deines', 'dem', 'demnach', 'demselben', 'den', 'denen', 'denn', 'dennoch', 'denselben', 'der', 'derart',
             'derartig', 'derem', 'deren', 'derer', 'derjenige', 'derjenigen', 'derselbe', 'derselben', 'derzeit',
             'des', 'deshalb', 'desselben', 'dessen', 'desto', 'deswegen', 'dich', 'die', 'diejenige', 'dies', 'diese',
             'dieselbe', 'dieselben', 'diesem', 'diesen', 'dieser', 'dieses', 'diesseits', 'dir', 'direkt', 'direkte',
             'direkten', 'direkter', 'doch', 'dort', 'dorther', 'dorthin', 'drauf', 'drin', 'drunter', 'drüber', 'du',
             'dunklen', 'durch', 'durchaus', 'eben', 'ebenfalls', 'ebenso', 'eher', 'eigenen', 'eigenes', 'eigentlich',
             'ein', 'eine', 'einem', 'einen', 'einer', 'einerseits', 'eines', 'einfach', 'einführen', 'einführte',
             'einführten', 'eingesetzt', 'einig', 'einige', 'einigem', 'einigen', 'einiger', 'einigermaßen', 'einiges',
             'einmal', 'eins', 'einseitig', 'einseitige', 'einseitigen', 'einseitiger', 'einst', 'einstmals', 'einzig',
             'entsprechend', 'entweder', 'er', 'erst', 'es', 'etc', 'etliche', 'etwa', 'etwas', 'euch', 'euer', 'eure',
             'eurem', 'euren', 'eurer', 'eures', 'falls', 'fast', 'ferner', 'folgende', 'folgenden', 'folgender',
             'folgendes', 'folglich', 'fuer', 'für', 'gab', 'ganze', 'ganzem', 'ganzen', 'ganzer', 'ganzes', 'gar',
             'gegen', 'gemäss', 'ggf', 'gleich', 'gleichwohl', 'gleichzeitig', 'glücklicherweise', 'gänzlich', 'hab',
             'habe', 'haben', 'haette', 'hast', 'hat', 'hatte', 'hatten', 'hattest', 'hattet', 'heraus', 'herein',
             'hier', 'hiermit', 'hiesige', 'hin', 'hinein', 'hinten', 'hinter', 'hinterher', 'http', 'hätt', 'hätte',
             'hätten', 'höchstens', 'ich', 'igitt', 'ihm', 'ihn', 'ihnen', 'ihr', 'ihre', 'ihrem', 'ihren', 'ihrer',
             'ihres', 'im', 'immer', 'immerhin', 'in', 'indem', 'indessen', 'infolge', 'innen', 'innerhalb', 'ins',
             'insofern', 'inzwischen', 'irgend', 'irgendeine', 'irgendwas', 'irgendwen', 'irgendwer', 'irgendwie',
             'irgendwo', 'ist', 'ja', 'je', 'jed', 'jede', 'jedem', 'jeden', 'jedenfalls', 'jeder', 'jederlei', 'jedes',
             'jedoch', 'jemand', 'jene', 'jenem', 'jenen', 'jener', 'jenes', 'jenseits', 'jetzt', 'jährig', 'jährige',
             'jährigen', 'jähriges', 'kam', 'kann', 'kannst', 'kaum', 'kein', 'keine', 'keinem', 'keinen', 'keiner',
             'keinerlei', 'keines', 'keineswegs', 'klar', 'klare', 'klaren', 'klares', 'klein', 'kleinen', 'kleiner',
             'kleines', 'koennen', 'koennt', 'koennte', 'koennten', 'komme', 'kommen', 'kommt', 'konkret', 'konkrete',
             'konkreten', 'konkreter', 'konkretes', 'können', 'könnt', 'künftig', 'leider', 'machen', 'man', 'manche',
             'manchem', 'manchen', 'mancher', 'mancherorts', 'manches', 'manchmal', 'mehr', 'mehrere', 'mein', 'meine',
             'meinem', 'meinen', 'meiner', 'meines', 'mich', 'mir', 'mit', 'mithin', 'muessen', 'muesst', 'muesste',
             'muss', 'musst', 'musste', 'mussten', 'muß', 'mußt', 'müssen', 'müsste', 'müssten', 'müßt', 'müßte',
             'nach', 'nachdem', 'nachher', 'nachhinein', 'nahm', 'natürlich', 'neben', 'nebenan', 'nehmen', 'nein',
             'nicht', 'nichts', 'nie', 'niemals', 'niemand', 'nirgends', 'nirgendwo', 'noch', 'nun', 'nur', 'nächste',
             'nämlich', 'nötigenfalls', 'ob', 'oben', 'oberhalb', 'obgleich', 'obschon', 'obwohl', 'oder', 'oft', 'per',
             'plötzlich', 'schließlich', 'schon', 'sehr', 'sehrwohl', 'seid', 'sein', 'seine', 'seinem', 'seinen',
             'seiner', 'seines', 'seit', 'seitdem', 'seither', 'selber', 'selbst', 'sich', 'sicher', 'sicherlich',
             'sie', 'sind', 'so', 'sobald', 'sodass', 'sodaß', 'soeben', 'sofern', 'sofort', 'sogar', 'solange',
             'solch', 'solche', 'solchem', 'solchen', 'solcher', 'solches', 'soll', 'sollen', 'sollst', 'sollt',
             'sollte', 'sollten', 'solltest', 'somit', 'sondern', 'sonst', 'sonstwo', 'sooft', 'soviel', 'soweit',
             'sowie', 'sowohl', 'tatsächlich', 'tatsächlichen', 'tatsächlicher', 'tatsächliches', 'trotzdem', 'ueber',
             'um', 'umso', 'unbedingt', 'und', 'unmöglich', 'unmögliche', 'unmöglichen', 'unmöglicher', 'uns', 'unser',
             'unsere', 'unserem', 'unseren', 'unserer', 'unseres', 'unter', 'usw', 'viel', 'viele', 'vielen', 'vieler',
             'vieles', 'vielleicht', 'vielmals', 'vom', 'von', 'vor', 'voran', 'vorher', 'vorüber', 'völlig', 'wann',
             'war', 'waren', 'warst', 'warum', 'was', 'weder', 'weil', 'weiter', 'weitere', 'weiterem', 'weiteren',
             'weiterer', 'weiteres', 'weiterhin', 'weiß', 'welche', 'welchem', 'welchen', 'welcher', 'welches', 'wem',
             'wen', 'wenig', 'wenige', 'weniger', 'wenigstens', 'wenn', 'wenngleich', 'wer', 'werde', 'werden',
             'werdet', 'weshalb', 'wessen', 'wichtig', 'wie', 'wieder', 'wieso', 'wieviel', 'wiewohl', 'will', 'willst',
             'wir', 'wird', 'wirklich', 'wirst', 'wo', 'wodurch', 'wogegen', 'woher', 'wohin', 'wohingegen', 'wohl',
             'wohlweislich', 'womit', 'woraufhin', 'woraus', 'worin', 'wurde', 'wurden', 'während', 'währenddessen',
             'wär', 'wäre', 'wären', 'würde', 'würden', 'z.B.', 'zahlreich', 'zB', 'zeitweise', 'zu', 'zudem', 'zuerst',
             'zufolge', 'zugleich', 'zuletzt', 'zum', 'zumal', 'zur', 'zurück', 'zusammen', 'zuviel', 'zwar',
             'zwischen', 'ähnlich', 'übel', 'über', 'überall', 'überallhin', 'überdies', 'übermorgen', 'übrig',
             'übrigens', 'zweiten', 'reference', 'zwei', 'zweitens', 'zweiter', 'wirksame', 'zwangsl', 'zuver',
             'zustim', 'zunehmend', 'zusehends', 'zwingend', 'zumindest', 'zweite', 'zusam', 'zweij', 'report',
             'Prüfbericht', 'tung', 'hierbei', 'jedermann', 'tel', 'könnte', 'ehrlich', 'wegen', 'jedermanns', 'n',
             'offen', 'guter', 'niemandem', 'gern', 'sache', 'richtig', 'darf', 'sechste', 'siebenter', 'f', 'h',
             'dürft', 'genug', 'sechsten', 'u', 'neuntes', 'niemanden', 'sah', 'i', 'großer', 'große', 'jahren',
             'später', 'vier', 'en', 'rechtes', 'gott', 'ag', 'v', 'c', 'mochten', 'achte', 'achten', 'ganz', 'rechten',
             'dritter', 'viertes', 'gedurft', 'mochte', 'dermassen', 'dritte', 'mögt', 'daselbst', 'ging', 'gehabt',
             'grosses', 'schlecht', 'siebenten', 'mag', 'eigene', 'fünfter', 'zehn', 'wollte', 'teil', 'zehnten',
             'statt', 'jahre', 'leicht', 'infolgedessen', 'dritten', 'gegenüber', 'gerade', 'neun', 'macht', 'zwanzig',
             'weniges', 'na', 'durfte', 'erste', 't', 'gekannt', 'vierter', 'sechster', 'kleine', 'sa', 'leide',
             'vierte', 'vielem', 'lieber', 'gross', 'gutes', 'l', 'q', 'heisst', 'eigen', 'z', 'hoch', 'wollt',
             'siebentes', 'gemusst', 'großen', 'vierten', 'mittel', 'tage', 'zunächst', 'habt', 'dürfen', 'zehnte',
             'her', 'd.h', 'ei', 'dementsprechend', 'vergangenen', 'neunten', 'endlich', 'j', 'ende', 'tagen',
             'währenddem', 'm', 'mögen', 'drittes', 'menschen', 'grosse', 'ersten', 'b', 'd', 'gesagt', 'beispiel',
             'dahinter', 'eigener', 'z.b', 'gemacht', 'konnte', 's', 'magst', 'morgen', 'großes', 'allgemeinen', 'fünf',
             'worden', 'wahr?', 'überhaupt', 'konnten', 'neunter', 'kurz', 'dasein', 'dazwischen', 'diejenigen',
             'fünfte', 'müsst', 'gewollt', 'gut', 'grossen', 'mensch', 'zehntes', 'demgemäß', 'seien', 'zehnter',
             'jemandem', 'sieben', 'tun', 'acht', 'sechs', 'darfst', 'k', 'zwölf', 'fünften', 'bekannt', 'und?',
             'demzufolge', 'lang', 'geworden', 'achter', 'sei', 'jahr', 'machte', 'solang', 'geschweige', 'grosser',
             'o', 'dank', 'zweites', 'groß', 'wollten', 'wollen', 'sechstes', 'rechte', 'erstes', 'g', 'möchte', 'mann',
             'tag', 'p', 'neue', 'sagte', 'ach', 'los', 'geht', 'r', 'satt', 'ohne', 'Schluss', 'sagt', 'gehen',
             'einander', 'möglich', 'gewesen', 'weit', 'rund', 'zeit', 'w', 'rechter', 'mahn', 'lange', 'heute',
             'achtes', 'gibt', 'durften', 'Ernst', 'erster', 'recht', 'drei', 'gekonnt', 'neuen', 'y', 'e', 'siebente',
             'demgegenüber', 'uhr', 'Ordnung', 'tat', 'früher', 'ei,', 'wart', 'neunte', 'gute', 'fünftes', 'elf',
             'dermaßen', 'besten', 'gemocht', 'tritt', 'jemanden', 'x', 'demgemäss', 'au', 'a'])
        tokens_without_sw = [word for word in text_tokens if not word in stop_words]
        return tokens_without_sw

    def removeDuplicateTokens(self, text_tokens):
        """Function that removes the duplicate tokens from the preprocessed tokenize text of the document.

        Parameters:
        text_tokens (list): preprocessed tokenize text

        Returns:
        list: return preprocessed tokenize text without duplicate words
       """

        text_tokens = list(dict.fromkeys(text_tokens))  # removing duplicate enteries
        regexp = re.compile(r"(.)\1")
        tokentosentence = ''
        count = 0
        sentencetoken = 0
        text_tokens_array = []
        for word in text_tokens:
            match = re.search(regexp, word)
            if ((len(word) < 20 and len(word) > 3)):
                if (not (match)):
                    #word = self.lemmatizer.lemmatize(word)
                    tokentosentence = tokentosentence + ' ' + str(word)
                    count = count + 1
                    if count == 1:
                        if (sentencetoken < 5000):
                            text_tokens_array.append(tokentosentence)
                            tokentosentence = ''
                            count = 0
                        else:
                            return text_tokens_array
                        sentencetoken = sentencetoken + 1
        return text_tokens_array