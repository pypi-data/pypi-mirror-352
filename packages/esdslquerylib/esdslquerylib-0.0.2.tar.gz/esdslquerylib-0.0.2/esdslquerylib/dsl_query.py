from .model import ElasticSearchModel

class DslQuery:
    def __init__(self, es_model:ElasticSearchModel):
        self.field_mapping = es_model.get_field_list()

    def get_bool_query(self, must = None, must_not = None, should = None):
        bq = {}

        if must != None:
            bq['must'] = must
        
        if must_not != None:
            bq['must_not'] = must_not
        
        if should != None:
            bq['should'] = should

        return {
            "bool":bq
        }

    def get_match_all_query(self):
        return {
            "match_all":{}
        }

    def get_dsl_query(self, query, source, size = 1000):
        return {
            "query":query,
            "size":size,
            "_source":source
        }
    
    def _get_keyword_if_text(self, field):
        for f in self.field_mapping:
            if f.get('name') == field:
                if f.get('keyword'):
                    return f"{field}.{f.get('keyword').get('name')}" 
        return field
        
    def get_term_query(self, field, value):
        field = self._get_keyword_if_text(field)
        return {
            "term":{
                field:value
            }
        }
    
    def get_exists_query(self, field):
        return {
            "exists":{
                "field":field
            }
        }
    
    def get_terms_query(self, field, value):
        return {
            "terms": {
                field:value
            }
        }
    
    def get_prefix_query(self, field, value):
        field = self._get_keyword_if_text(field)
        return {
            "prefix":{ # only work for keyword, text, wildcard. # tried, seems text not working and keyword sub field works
                field:value
            }
        }
    
    def get_wildcard_query(self, field, value):
        return {
            "wildcard":{ # only work for keyword, text, wildcard. # tried, works for text
                field:{
                    "value":value
                }
            }
        }
    
    def get_range_query(self, field, operator, value):
        '''
        operator: gt, gte, lt, lte
        '''
        return {
            "range":{
                field:{
                    operator:value
                }
            }
        }
    
    def get_not_query(self, query):
        return self.get_bool_query(must_not = [query])
    
    def get_multi_not_query(self, queries):
        return self.get_bool_query(must_not = queries)

    def get_field_clause(self, field, condition, value):
        if condition == 'eq':
            return self.get_term_query(field,value)
        elif condition == '!eq':
            return self.get_not_query(self.get_term_query(field,value))
        elif condition == 'exists':
            if value == True:
                return self.get_exists_query(field)
            else:
                return self.get_not_query(self.get_exists_query(field))
        elif condition == 'in':
            return self.get_terms_query(field,value)
        elif condition == '!in':
            return self.get_not_query(self.get_terms_query(field, value))
        elif condition == 'prefix':
            return self.get_prefix_query(field,value)
        elif condition == 'like':
            return self.get_wildcard_query(field,value)
        elif condition == 'gt':
            return self.get_range_query(field,'gt',value)
        elif condition == 'gte':
            return self.get_range_query(field,'gte',value)
        elif condition == 'lt':
            return self.get_range_query(field,'lt',value)
        elif condition == 'lte':
            return self.get_range_query(field,'lte',value)