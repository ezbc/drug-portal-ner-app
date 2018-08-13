
import spacy

class DrugNER:

    def __init__(self, model_name, model_path):

    		self.model_name = model_name
    		self.model_path = model_path

    		self.model = spacy.load(model_path)

    def evaluate(self, text):
    		doc = self.model(text)
    		entities = []
    		for ent in doc.ents:
    				entities.append({
    					'text': ent.text,
    					'start_char': ent.start_char, 
    					'end_char': ent.end_char,
    					'label': ent.label_
    					})
    		return {'entities': entities}
