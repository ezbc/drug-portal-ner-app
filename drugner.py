import spacy

class DrugNER:

    def __init__(self, model_name, model_path):
    
        self.model_name = model_name
        self.model_path = model_path
        self.model = None

    def evaluate(self, text):
    
        # lazy load model
        if self.model is None:
          self.model = spacy.load(self.model_path)
    
        doc = self.model(text)
        entities = []
        for ent in doc.ents:
          entities.append({
            'text': ent.text,
            'start_char': ent.start_char,
            'end_char': ent.end_char,
            'label': ent.label_
          })
        return {
          'entities': entities
        }
