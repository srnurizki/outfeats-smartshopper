# <<<./ Import Libraries
from haystack import Pipeline, component
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from config.settings import GENERATOR_MODEL, GENERATOR_BASE_URL
from database.mongo_client import get_client, get_db, get_filter_values
from config.settings import COLORS_COLLECTION, FABRICS_COLLECTION, STYLES_COLLECTION, PATTERNS_COLLECTION, CATEGORY_COLLECTION, INTENT_COLLECTION
from typing import List
import os
import re
import json
from tools.timer import timer
from dotenv import load_dotenv

# <<<./ Load API
load_dotenv()
DEEPSEEK_API = os.getenv('DEEPSEEK_API')

# <<<./ Get Filter Values
@component
class GetColors:
    @component.output_types(colors = List[str])
    def run(self):
        return {'colors': get_filter_values(COLORS_COLLECTION)}

@component
class GetFabrics:
    @component.output_types(fabrics = List[str])
    def run(self):
        return {'fabrics': get_filter_values(FABRICS_COLLECTION)}

@component
class GetStyles:
    @component.output_types(styles = List[str])
    def run(self):
        return {'styles': get_filter_values(STYLES_COLLECTION)}

@component
class GetPatterns:
    @component.output_types(patterns = List[str])
    def run(self):
        return {'patterns': get_filter_values(PATTERNS_COLLECTION)}

@component
class GetCategories:
    @component.output_types(categories = List[str])
    def run(self):
        return {'categories': get_filter_values(CATEGORY_COLLECTION)}

@component
class GetIntents:
    @component.output_types(intents = List[str])
    def run(self):
        return {'intents': get_filter_values(INTENT_COLLECTION)}

# <<<./ Parse JSON
@component
class ParseFilterJSON:
    @component.output_types(filters=List[dict])
    def run(self, replies: List[ChatMessage]):
        text = replies[0].text
        text = re.sub(r'```json|```', '', text).strip()
        filters = json.loads(text)
        return {'filters': filters}

# <<<./ Metadata Filter Template
METADATA_FILTER_TEMPLATE = """
You are a JSON generator. Your job is to generate a MongoDB filter JSON based on the user input.

The output JSON must follow this format:
```json
{
    "operator": "AND",
    "conditions": [
        {"field": "meta.<field>", "operator": "<operator>", "value": <value>}
    ]
}
```

Available fields and valid values:

Product fields:
- meta.color — valid values: [{% for c in colors %}{{ c }}{% if not loop.last %}, {% endif %}{% endfor %}]
- meta.style — valid values: [{% for s in styles %}{{ s }}{% if not loop.last %}, {% endif %}{% endfor %}]
- meta.fabric — valid values: [{% for f in fabrics %}{{ f }}{% if not loop.last %}, {% endif %}{% endfor %}]
- meta.pattern — valid values: [{% for p in patterns %}{{ p }}{% if not loop.last %}, {% endif %}{% endfor %}]
- meta.price — numerical, operators: "<=", ">=", "=="
- meta.size — valid values: XS, S, M, L, XL, XXL, one-size, plus-size

Common information fields:
- meta.category — valid values: [{% for c in categories %}{{ c }}{% if not loop.last %}, {% endif %}{% endfor %}]
- meta.intent — valid values: [{% for i in intents %}{{ i }}{% if not loop.last %}, {% endif %}{% endfor %}]

Rules:
1. Only include fields relevant to the input
2. Use "!=" for negation
3. Nested AND/OR conditions are allowed
4. For price range, use nested AND with >= and <=
5. For price "around" a value, use value-10 and value+10
6. If no relevant fields found, return: {}
7. Only use values from the valid values list above

Examples:

1. Input: "I want a red casual dress under $30"
output:
```json
{
    "operator": "AND",
    "conditions": [
        {"field": "meta.color", "operator": "==", "value": "Red"},
        {"field": "meta.style", "operator": "==", "value": "Casual"},
        {"field": "meta.price", "operator": "<=", "value": 30}
    ]
}
```

2. Input: "Show me floral tops that are not sheer fabric"
output:
```json
{
    "operator": "AND",
    "conditions": [
        {"field": "meta.pattern", "operator": "==", "value": "Floral"},
        {"field": "meta.fabric", "operator": "!=", "value": "Sheer"}
    ]
}
```

3. Input: "I want a dress with price between $20 and $50"
output:
```json
{
    "operator": "AND",
    "conditions": [
        {"field": "meta.style", "operator": "==", "value": "Casual"},
        {
            "operator": "AND",
            "conditions": [
                {"field": "meta.price", "operator": ">=", "value": 20},
                {"field": "meta.price", "operator": "<=", "value": 50}
            ]
        }
    ]
}
```

4. Input: "I purchased some item, help canceling one of the orders"
output:
```json
{
    "operator": "AND",
    "conditions": [
        {"field": "meta.category", "operator": "==", "value": "ORDER"},
        {"field": "meta.intent", "operator": "==", "value": "cancel_order"}
    ]
}
```

5. Input: "I need assistance restoring the key of my profile"
output:
```json
{
    "operator": "AND",
    "conditions": [
        {"field": "meta.category", "operator": "==", "value": "ACCOUNT"},
        {"field": "meta.intent", "operator": "==", "value": "recover_password"}
    ]
}
```

Input: {{ input }}
output:
"""

# <<<./ Metadata Filter Pipeline
class MetaDataFilterPipeline():
    def __init__(self):
        self.template = METADATA_FILTER_TEMPLATE

        self.pipeline = Pipeline()
        self.pipeline.add_component('colors', GetColors())
        self.pipeline.add_component('fabrics', GetFabrics())
        self.pipeline.add_component('styles', GetStyles())
        self.pipeline.add_component('patterns', GetPatterns())
        self.pipeline.add_component('categories', GetCategories())
        self.pipeline.add_component('intents', GetIntents())
        self.pipeline.add_component(
            'prompt_builder', ChatPromptBuilder(
                variables = ['input', 'colors', 'fabrics', 'styles', 'patterns', 'categories', 'intents'],
                required_variables = ['input', 'colors', 'fabrics', 'styles', 'patterns', 'categories', 'intents']))
        self.pipeline.add_component('generator', OpenAIChatGenerator(
            model = GENERATOR_MODEL, api_key = Secret.from_token(DEEPSEEK_API), api_base_url = GENERATOR_BASE_URL))
        self.pipeline.add_component('parse', ParseFilterJSON())

        self.pipeline.connect('colors.colors', 'prompt_builder.colors')
        self.pipeline.connect('fabrics.fabrics', 'prompt_builder.fabrics')
        self.pipeline.connect('styles.styles', 'prompt_builder.styles')
        self.pipeline.connect('patterns.patterns', 'prompt_builder.patterns')
        self.pipeline.connect('categories.categories','prompt_builder.categories')
        self.pipeline.connect('intents.intents', 'prompt_builder.intents')
        self.pipeline.connect('prompt_builder.prompt', 'generator.messages')
        self.pipeline.connect('generator.replies', 'parse.replies')

    @timer
    def run(self, query: str):
        template = [ChatMessage.from_user(self.template)]
        res = self.pipeline.run(
            data = {
                'prompt_builder' : {
                    'input' : query,
                    'template' : template,
                }})
        return res['parse']['filters']
