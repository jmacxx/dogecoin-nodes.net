from app import app, db
from app.models import Inventory

@app.shell_context_processor
def make_shell_context():
	return {'db': db, 'Inventory': Inventory}


