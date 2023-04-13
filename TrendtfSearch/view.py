from flask import render_template

class SearchView:

    def __init__(self, config):
        self.config = config
        
    @staticmethod
    def display_search_results(query, results, page, total_pages, took, total_hits, error_occured):
        """
        Display search results in HTML template.
        """
        
        if total_pages and not error_occured > 0:
            return render_template('search.html', q=query, 
                                hits=results, page=page, total_pages=total_pages, 
                                took=took, total_hits=total_hits, error_occured=error_occured)
        else:
            return render_template('search.html', q=query, hits=results, page=page,
                                total_pages=1, took=took, total_hits=0, error_occured=error_occured)