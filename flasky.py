import os
from app import create_app, db
from app.Models.models import User, Role
from flask_migrate import Migrate
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config_name)
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.cli.command()
def test():
    """Run the unit tests.
    From the cmd :
    (flasky) $ flask test
    """
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
