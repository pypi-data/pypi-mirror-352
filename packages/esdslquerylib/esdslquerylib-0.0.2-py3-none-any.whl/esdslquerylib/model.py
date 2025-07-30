from abc import ABC
from enum import Enum
from typing import Type, Union


class ElasticSearchModel(ABC):
    MAX_NESTED_DEPTH = 10

    @classmethod
    def get_field_list(cls, depth = 0):
        if depth > cls.MAX_NESTED_DEPTH:
            return []
        
        fields = {k:v for k,v in vars(cls).items() if type(v) == Field}

        searchable_data_types = [DataType.text, DataType.date, DataType.integer, DataType.long, DataType.boolean]
        field_list = []
        for k in fields:
            nested_fields = []
            field_name = k
            field_label = k
            field_type = None
            field_searchable = True
            keyword = fields.get(k).get_keyword()
            for p in fields.get(k).properties:
                if type(p) == DataType:
                    field_type = p.value
                    field_searchable = p in searchable_data_types
                elif type(p) == NestedObject:
                    nested_object = p.get_object() 
                    if nested_object is not None:
                        nested_fields = nested_object.get_field_list(depth = depth + 1)
                elif type(p) == Name:
                    field_name = p.name
            
            if field_type == DataType.nested.value:
                for nf in nested_fields:
                    field_list.append({
                        **nf,
                        'name':field_name + '.' + nf.get('name'),
                        'label':field_label + '.' + nf.get('label')
                    })
            else:
                field_list.append({
                    'name': field_name,
                    'label': field_label,
                    'type': field_type,
                    'searchable': field_searchable,
                    'keyword': keyword
                })

        for f in field_list:
            l = f.get('name')
            if '.' in l:
                last_dot_index = l.rfind(".")
                left_part = l[:last_dot_index]
                right_part = l[last_dot_index:]
                abbr = left_part[:3]
                f['label'] = f"{abbr}{ '.' * l.count('.') if len(left_part) > len(abbr) else ''}{right_part}"


        return field_list

class Field:
    def __init__(self, *field_properties):
        self.properties = field_properties

    def get_keyword(self):
        if not hasattr(self, '_keyword'):
            default_keyword = None
            explicit_keyword = None
            has_explicit_keyword = False
            
            for p in self.properties:
                if p == DataType.text:
                    default_keyword = TextKeyword().get_dict()
                elif type(p) == TextKeyword:
                    has_explicit_keyword = True
                    explicit_keyword = p.get_dict()
            self._keyword = explicit_keyword  if has_explicit_keyword else default_keyword
        return self._keyword

class DataType(Enum):
    text = 'text'
    date = 'date'
    double = 'double'
    integer = 'integer'
    long = 'long'
    nested = 'nested'
    boolean = 'boolean'
    object = 'object'
    ip = 'ip'

class NestedObject:
    def __init__(self, cls:Type[ElasticSearchModel]):
        self._cls = cls

    def get_object(self) -> Union[Type[ElasticSearchModel], None]:
        if not hasattr(self, '_o'):
            o = None
            if isinstance(self._cls, type):
                if issubclass(self._cls, ElasticSearchModel):
                    o = self._cls
            self._o = o
        return self._o
    
class TextKeyword:
    def __init__(self, keyword = True):
        self.keyword = keyword
        if keyword:
            self.name = 'keyword'
            self.ignore_above = 256

    def get_dict(self):
        return {'name':self.name, 'ignore_above':self.ignore_above} if self.keyword else None

class Name:
    def __init__(self, name):
        self.name = name