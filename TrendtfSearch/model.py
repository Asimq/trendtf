from elasticsearch import Elasticsearch

class SearchModel:
    def __init__(self, config):
        self.es = Elasticsearch([config['elasticsearch']['url']])
        self.index = config['elasticsearch']['index']
        self.results_per_page = config['results_per_page']

    def build_es_query(self, es_query_term, lang_value=None, publisher_value=None, start_date=None, end_date=None, topic_value=None):
        """
        Build Elasticsearch query based on search terms and filters.
        """
        if es_query_term and es_query_term != "":
            es_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": es_query_term,
                                    "analyzer": "standard",
                                    "fields": ["*"]
                                }
                            }
                        ]
                    }
                }
            }
        else:
            es_query = {
                "query": {
                    "bool": {
                        "must": [
                            
                        ]
                    }
                }
            }
          
        if lang_value:
            es_query["query"]["bool"]["must"].append({"match": {"language.language": lang_value}})
        if publisher_value:
            es_query["query"]["bool"]["must"].append({"match": {"publisher.publisher.keyword": publisher_value}})
        if start_date and end_date:
            es_query["query"]["bool"]["must"].append({"range": {"publicationYear.publicationYear": {"gte": int(start_date), "lte": int(end_date)}}})
        elif start_date:
            es_query["query"]["bool"]["must"].append({"match": {"publicationYear.publicationYear": int(start_date)}})
        if topic_value:
            es_query["query"]["bool"]["should"] = [
                {"match": {"titleAnnotations.resources.surfaceForm": topic_value}},
                {"match": {"titleAnnotations.resources.types": topic_value}},
                {"match": {"topicModelling.wEmbLda.topics": topic_value}},
                # {"match": {"subjects.subject.subInt": topic_value}},
                {"match": {"subjects.subject.subStr": topic_value}}
            ]
            es_query["query"]["bool"]["minimum_should_match"] = 1
        
        return es_query

    def search_es_index(self, es_query, es_query_full, page):
        """
        Search Elasticsearch index with given query and pagination parameters.
        """
        es_query["from"] = (page-1) * self.results_per_page
        es_query["size"] = self.results_per_page
        
        results = self.es.search(index=self.index, body=es_query)
        total_hits = self.es.search(index=self.index, body=es_query_full)['hits']['total']['value']
        took = results['took']
        results = results['hits']['hits']
        total_pages = (total_hits // self.results_per_page) + (1 if total_hits % self.results_per_page > 0 else 0)
        
        return results, total_hits, took, total_pages