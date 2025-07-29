import argilla as rg
from datasets import load_dataset
from typing import List, Dict, Any, Union

FIELD_TYPE_MAPPING = {
    "text": rg.TextField,
    "image": rg.ImageField,
    "chat": rg.ChatField,
    "custom": rg.CustomField,
}

QUESTION_TYPE_MAPPING = {
    "label": rg.LabelQuestion,
    "multi-label": rg.MultiLabelQuestion,
    "ranking": rg.RankingQuestion,
    "rating": rg.RatingQuestion,
    "span": rg.SpanQuestion,
    "text": rg.TextQuestion
}

class SyntheticData:
    def __init__(self, argilla_api_url: str, argilla_api_key: str):
        self.api_url = argilla_api_url
        self.api_key = argilla_api_key
        self.client = None
        self.dataset = None

    def connect(self):
        try:
            self.client = rg.Argilla(api_url=self.api_url, api_key=self.api_key)
            print("✅ Argilla client initialized.")
        except Exception as e:
            print(f"❌ Failed to connect to Argilla: {e}")
            self.client = None

    def set_dataset(self, dataset_name: str) -> Dict[str, str]:
        try:
            self.dataset = self.client.datasets(name=dataset_name)
            return {"status": "success", "message": f"Dataset '{dataset_name}' loaded."}
        except Exception as e:
            print(f"❌ Failed to load and set dataset: {e}")
            return {"status": "error", "message": str(e)}

    def build_questions(self, questions_config: List[Dict[str, Any]]) -> List[Any]:
        questions = []
        for q in questions_config:
            q_type = q.get("type")
            q_cls = QUESTION_TYPE_MAPPING.get(q_type)

            if not q_cls:
                print(f"❌ Unsupported question type: {q_type}")
                print(f"Supported question types: {QUESTION_TYPE_MAPPING.keys()}")
                print(f"If you would like to see examples of each question type, please run the following command: show_supported_question_types()")
                return []
            q_kwargs = {k: v for k, v in q.items() if k != "type"}
            questions.append(q_cls(**q_kwargs))
        return questions

    
    def build_fields(self, fields_config: List[Dict[str, Any]]) -> List[Any]:
        fields = []
        for field in fields_config:
            field_type = field.get("type")
            field_cls = FIELD_TYPE_MAPPING.get(field_type)

            if not field_cls:
                print(f"❌ Unsupported field type: {field_type}")
                print(f"Supported field types: {FIELD_TYPE_MAPPING.keys()}")
                print(f"If you would like to see examples of each field type, please run the following command: show_supported_field_types()")
                return []
            field_kwargs = {k: v for k, v in field.items() if k != "type"}
            fields.append(field_cls(**field_kwargs))
        return fields

    def create_dataset(self, dataset_name: str, fields: List[rg.Field], questions: List[Union[rg.LabelQuestion, rg.MultiLabelQuestion, rg.RankingQuestion, rg.RatingQuestion, rg.SpanQuestion, rg.TextQuestion]], metadata: List[Union[rg.TermsMetadataProperty, rg.IntegerMetadataProperty, rg.FloatMetadataProperty]] = None, vectors: List[rg.VectorField] = None) -> Dict[str, str]:
        try:
            settings = rg.Settings(
                fields=fields,
                questions=questions,
                metadata=metadata,
                vectors=vectors
            )
        except Exception as e:
            print(f"❌ Error creating settings: {e}")
            print(f"Please call the build_fields() and build_questions() functions to create the fields and questions.")
            return {"status": "error", "message": str(e)}

        if not self.client:
            print(f"❌ Client not initialized. Please call connect() first.")
            return {"status": "error", "message": "Client not initialized. Please call connect() first."}

        try:
            dataset = rg.Dataset(
                name=dataset_name,
                settings=settings,
                client=self.client,
            )
            dataset.create()
            print(f"✅ Dataset '{dataset_name}' created.")
            return {"status": "success", "message": f"Dataset '{dataset_name}' created."}
        except Exception as e:
            print(f"❌ Failed to create dataset: {e}")
            return {"status": "error", "message": str(e)}

    def show_supported_field_types():
        print("✅ Supported Argilla Field Types and Example Structures:\n")

        examples = {
            "text": {
                "type": "text",
                "name": "review_text",
                "title": "Review",
                "use_markdown": False,
                "required": True,
                "description": "The user's review of the product."
            },
            "image": {
                "type": "image",
                "name": "product_image",
                "title": "Product Image",
                "required": True,
                "description": "An image of the product being reviewed."
            },
            "chat": {
                "type": "chat",
                "name": "dialogue",
                "title": "User Conversation",
                "use_markdown": True,
                "required": True,
                "description": "The conversation between user and system."
            },
            "custom": {
                "type": "custom",
                "name": "custom_render",
                "title": "Custom HTML Field",
                "template": "<div>{{record.fields.custom_render.key}}</div>",
                "advanced_mode": False,
                "required": True,
                "description": "A custom-rendered UI field."
            }
        }

        for field_type, example in examples.items():
            print(f"--- {field_type.upper()} FIELD ---")
            for key, value in example.items():
                print(f"{key}: {value}")
            print("")

    def show_supported_question_types():
        print("✅ Supported Argilla Question Types and Example Structures:\n")

        examples = {
            "label": {
                "type": "label",
                "name": "relevance",
                "labels": ["YES", "NO"],
                "title": "Is the content relevant?",
                "description": "Choose one option.",
                "required": True,
                "visible_labels": 10
            },
            "multi-label": {
                "type": "multi-label",
                "name": "toxicity_tags",
                "labels": ["hate", "pii", "offensive"],
                "title": "What types of content are present?",
                "description": "Select all that apply.",
                "required": True,
                "visible_labels": 10
            },
            "ranking": {
                "type": "ranking",
                "name": "rank_replies",
                "values": ["reply-1", "reply-2", "reply-3"],
                "title": "Rank the following replies",
                "description": "1 = best, 3 = worst. Ties allowed.",
                "required": True
            },
            "rating": {
                "type": "rating",
                "name": "response_quality",
                "values": list(range(11)),
                "title": "Rate the response",
                "description": "0 = worst, 10 = best",
                "required": True
            },
            "span": {
                "type": "span",
                "name": "highlight_entities",
                "field": "text",
                "labels": ["PERSON", "ORG", "LOC"],
                "title": "Highlight named entities",
                "description": "Mark parts of the text.",
                "required": True,
                "allow_overlapping": False,
                "visible_labels": 10
            },
            "text": {
                "type": "text",
                "name": "feedback",
                "title": "Any comments?",
                "description": "Leave a free-text comment.",
                "required": False,
                "use_markdown": True
            }
        }

        for q_type, example in examples.items():
            print(f"--- {q_type.upper()} ---")
            for k, v in example.items():
                print(f"{k}: {v}")
            print("")

    def log_data(self, data: List[Dict[str, Union[str, int, float, list, dict]]], mapping: Dict[str, Union[str, List[str]]] = None) -> Dict[str, str]:
        if not self.dataset:
            print(f"❌ Dataset not initialized. Call set_dataset(dataset_name) first.")
            return {"status": "error", "message": "Dataset not initialized. Call set_dataset(dataset_name) first."}
        try:
            self.dataset.records.log(records=data, mapping=mapping or {})
            print(f"✅ Logged {len(data)} records to dataset '{self.dataset.name}'.")
            return {"status": "success", "message": f"Logged {len(data)} records to dataset '{self.dataset.name}'."}
        except Exception as e:
            print(f"❌ Failed to log records: {e}")
            return {"status": "error", "message": str(e)}
