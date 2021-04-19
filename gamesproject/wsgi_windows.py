#ADD THIS IN PROJECT DIRECTORY with the settings file

import os
import sys
import site
from django.core.wsgi import get_wsgi_application

PYTHON_VERSION = '.'.join(map(str, sys.version_info[:2]))

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ),'..'))
ENVIRONMENT_PATH = os.path.join(ROOT_PATH, 'environment_windows' if os.name == 'nt' else 'environment_linux')

SITE_PACKAGES_PATH = 'lib/site-packages' if os.name == 'nt' else f'lib/python{PYTHON_VERSION}/site-packages'
SITE_PACKAGES = os.path.join(ENVIRONMENT_PATH, SITE_PACKAGES_PATH)

# SITE_PACKAGES = "C:/Users/Shaklain/AppData/Roaming/Python/Python36/site-packages"
site.addsitedir(SITE_PACKAGES)

# Add the app's directory to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Replace PROJECT_NAME with your Project Name
os.environ['DJANGO_SETTINGS_MODULE'] = 'gamesproject.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gamesproject.settings")

application = get_wsgi_application()
