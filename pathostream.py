import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    
from flask_migrate import Migrate
from app import create_app, db
from app.models import Case, User, Role, Permission, PCU_Lookup, Task

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission, Case=Case, PCU_lookup=PCU_Lookup, Task=Task)

