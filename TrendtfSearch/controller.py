from flask import request, render_template
from model import SearchModel
from view import SearchView
import re

class SearchController:
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.model = SearchModel(config)
        self.view = SearchView(config)
        
    def filter_query(self,query):
        """
        Filter query for language, publisher, date, and topic.
        """
        es_query_term = query
        lang_value = None
        publisher_value = None
        start_date = None
        end_date = None
        topic_value = None
        
        # Find quoted strings and replace with a unique marker
        quoted_strings = []
        def replace_quoted(match):
            quoted_strings.append(match.group(0))
            return f"__QUOTED_STRING_{len(quoted_strings) - 1}__"
        
        # Replace quoted strings with unique markers, except for the lang, publisher, date, and topic terms
        query_without_terms = re.sub(r'\b(lang|publisher|date|topic):("[^"]+"|\S+)\s*', '', query)
        query_without_terms = re.sub(r'"[^"]*"', replace_quoted, query_without_terms)
        
        # Check for language, publisher, date, and topic
        for term in re.findall(r'\b(lang|publisher|date|topic):("[^"]+"|\S+)\s*', query):
            if term[0] == 'lang':
                lang_value = term[1].strip('"')
            elif term[0] == 'publisher':
                publisher_value = term[1].strip('"')
            elif term[0] == 'date':
                date_value = term[1].strip('"')
                if '-' in date_value:
                    start_date, end_date = date_value.split('-')
                else:
                    start_date = end_date = date_value
                # Verify that start_date and end_date contain only numbers
                if not (start_date.isdigit() and end_date.isdigit()):
                    # Return None values for all fields
                    return None, None, None, None, None, None
            elif term[0] == 'topic':
                topic_value = term[1].strip('"')       
        # Replace the unique markers with their original values
        for i, quoted_string in enumerate(quoted_strings):
            query_without_terms = query_without_terms.replace(f"__QUOTED_STRING_{i}__", quoted_string)
        
        # Strip any leading/trailing whitespace and return the filtered query and values
        es_query_term = query_without_terms.strip()
        return es_query_term, lang_value, publisher_value, start_date, end_date, topic_value
    
controller = None

def init_controller(app, config):
    global controller
    controller = SearchController(app, config)
    
    @app.route('/')    
    @app.route(app.config['APPLICATION_ROOT'] + '/')
    def search():
        global controller
        """
        Handle search query and display search results.
        """
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        error_occurred = False
        if query:
            try:
                # Filter query for language, publisher, date, and topic
                es_query_term, lang_value, publisher_value, start_date, end_date, topic_value = controller.filter_query(query)
                if all(value is None for value in (es_query_term, lang_value, publisher_value, start_date, end_date, topic_value)):
                    raise Exception
                es_query = controller.model.build_es_query(es_query_term, lang_value, publisher_value, start_date, end_date, topic_value)
                es_query_full = es_query.copy()

                results, total_hits, took, total_pages = controller.model.search_es_index(es_query, es_query_full, page)
            except Exception as e:
                error_occurred = True
                results = []
                total_pages = 0
                took = 0
                total_hits = 0    
            finally:
                return controller.view.display_search_results(query, results, page, total_pages, took, total_hits, error_occurred)   
        else:
            results = []
            total_pages = 0
            took = 0
            total_hits = 0

        return controller.view.display_search_results(query, results, page, total_pages, took, total_hits, error_occurred)

        
    @app.route('/about')    
    @app.route(app.config['APPLICATION_ROOT'] + '/about')
    def about():
        return render_template('about.html')
    
    @app.route('/dataprotection')
    @app.route(app.config['APPLICATION_ROOT'] + '/dataprotection')
    def dataprotection():
        return render_template('dataprotection.html')
    
    @app.route('/imprint')
    @app.route(app.config['APPLICATION_ROOT'] + '/imprint')
    def imprint():
        return render_template('imprint.html')
