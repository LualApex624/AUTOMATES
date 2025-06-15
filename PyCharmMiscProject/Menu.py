from script import *


def afficher_menu():
    print("\n--- Menu Principal ---")
    print("1. Afficher l'automate")
    print("2. Vérifier les propriétés de l'automate")
    print("3. Standardiser l'automate")
    print("4. Déterminiser et compléter l'automate")
    print("5. Créer l'automate complémentaire")
    print("6. Reconnaître un mot")
    print("7. Minimiser l'automate")
    print("8. Quitter")

def menu_principal():
    # Lecture de l'automate à partir du fichier
    num_automate = input("Entrez le numéro du fichier contenant l'automate : ").strip()
    try:
        nom_fichier = f"automate/automate{num_automate}.txt"
        automate = lire_automate(nom_fichier)
        print("\nAutomate lu avec succès.")
    except Exception as e:
        print(f"\nErreur lors de la lecture du fichier : {e}")
        return

    while True:
        afficher_menu()
        choix = input("Choisissez une option (1-8): ").strip()

        if choix == "1":
            print("\nAffichage de l'automate :")
            afficher_automate(automate)

        elif choix == "2":
            print("\nVérification des propriétés de l'automate :")
            verifier_automate(automate)

        elif choix == "3":
            print("\nStandardisation de l'automate :")
            automate = standardiser(automate)

        elif choix == "4":
            print("\nDéterminisation et complétion de l'automate :")
            automate = determiniser_et_completer(automate)

        elif choix == "5":
            print("\nCréation de l'automate complémentaire :")
            automate = creer_automate_complementaire(automate, debug=True)
            print("\nAutomate complémentaire créé :")
            afficher_automate(automate)


        elif choix == "6":
            print("\nReconnaissance de mot :")
            while True:
                mot = input("Entrez le mot à reconnaître ou 'end' pour arrêter : ").strip()
                if mot == "end":
                    print("Fin de la reconnaissance de mots.")
                    break
                else:
                    reconnaitre_mot(automate, mot)  # Appel de la fonction avec le mot saisi

        elif choix == "7":
            print("\nMinimisation de l'automate :")
            auto = minimiser_automate(automate)
            print("\nAutomate minimisé :")
            afficher_automate(auto)

        elif choix == "8":
            print("\nFin du programme.")
            break

        else:
            print("\nOption invalide. Veuillez choisir une option entre 1 et 8.")

# Exécution du menu principal
menu_principal()