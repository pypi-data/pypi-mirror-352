import argparse
from .core import create_project, confirm_app

def main():
    print("======================================")
    print("\U0001F680 Bienvenue dans Django Carch CLI \U0001F680")
    print("======================================\n")

    project_name = input("🔧 Entrez le nom du projet Django : ")
    apps = confirm_app()

    print("\n📆 Nom du projet :", project_name)
    print("📁 Applications à générer :", ", ".join(apps) if apps else "Aucune")

    create_project(project_name, apps)

if __name__ == "__main__":
    main()
