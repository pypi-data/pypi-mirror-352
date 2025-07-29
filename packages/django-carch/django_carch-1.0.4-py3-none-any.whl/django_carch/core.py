import os
import subprocess
from pathlib import Path
from importlib.resources import files

def prompt(text):
    try:
        return input(text)
    except KeyboardInterrupt:
        print("\n\u274c Interruption.")
        exit(1)

def confirm_app():
    apps = []
    while True:
        print("\n👊 Entrez le nom d'une application (ou tapez 'build' pour lancer la création) :")
        user_input = prompt("> ")
        if user_input.lower() == "build":
            break
        confirm = prompt(f"✅ Confirmez-vous ce nom ({user_input}) ? (Y/N) : ")
        if confirm.lower() == "y":
            apps.append(user_input)
            print(f"✅ Application '{user_input}' ajoutée.")
        else:
            print("❌ Nom rejeté. Veuillez le ressaisir.")
    return apps

def install_dependencies():
    subprocess.run(["python3", "-m", "venv", ".venv"])
    subprocess.run(["bash", "-c", "source .venv/bin/activate && pip install --upgrade pip"])
    subprocess.run(["bash", "-c", "source .venv/bin/activate && pip install django djangorestframework djangorestframework-simplejwt drf-yasg drf-spectacular phonenumbers python-dotenv psycopg2-binary coverage sentry-sdk watchdog flower pre-commit django-redis"])

def generate_env_file():
    Path(".env").write_text("""SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=vtc_db
DB_USER=vtc_user
DB_PASSWORD=vtc_password
DB_HOST=localhost
DB_PORT=5432
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=sender_id
FIREBASE_APP_ID=your_app_id
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890
""")



def generate_documentation(project_name):
    content = files("django_carch").joinpath("bootstrap.md").read_text()
    content = content.replace("$PROJECT_NAME", project_name)
    Path("README.md").write_text(content)

def create_project(project_name, apps):
    print(f"📁 Création du projet : {project_name}")
    install_dependencies()
    subprocess.run(["django-admin", "startproject", project_name])
    os.chdir(f"{project_name}/{project_name}")

    for path in ["management/commands", "services", "shared", "utils", "tests"]:
        os.makedirs(path, exist_ok=True)
        Path(f"{path}/__init__.py").touch()

    os.chdir("..")

    for app in apps:
        subprocess.run(["python", "manage.py", "startapp", app])
        build_app_structure(app)

    generate_env_file()
    generate_documentation(project_name)
    Path(".gitignore").write_text("__pycache__/\n*.py[cod]\n*.env\n*.log\n.vscode/\n.idea/\n/static/\ndb.sqlite3\n")

    print(f"\n🎉 Projet Django {project_name} généré avec succès !")
    print("📖 Documentation générée dans README.md")

def build_app_structure(app_name):
    dirs = [
        "admin", "dtos", "infrastructure", "migrations", "models", "services",
        "signals", "validators", "types",
        "helpers/types", "helpers/utils",
        "core/exceptions", "core/use_cases", "core/types",
        "tests/integration", "tests/unit",
        "api/v1/access_policy", "api/v1/filters", "api/v1/serializers",
        "api/v1/urls", "api/v1/views"
    ]
    for d in dirs:
        path = os.path.join(app_name, d)
        os.makedirs(path, exist_ok=True)
        Path(os.path.join(path, "__init__.py")).touch()