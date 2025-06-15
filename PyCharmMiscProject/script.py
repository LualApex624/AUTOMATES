
def lire_automate(nom_fichier):
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as fichier:
            lignes = fichier.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier {nom_fichier} n'existe pas.")

    # Vérification du nombre minimal de lignes
    if len(lignes) < 5:
        raise ValueError("Le fichier doit contenir au moins 5 lignes.")

    try:
        # Lecture des informations de l'automate
        nb_symboles = int(lignes[0].strip())
        nb_etats = int(lignes[1].strip())
        etats_initiaux = list(map(int, lignes[2].strip().split()[1:]))
        etats_terminaux = list(map(int, lignes[3].strip().split()[1:]))
        nb_transitions = int(lignes[4].strip())
    except (IndexError, ValueError) as e:
        raise ValueError(f"Erreur de lecture du fichier : {e}")

    # Vérification des états initiaux et terminaux
    for etat in etats_initiaux:
        if etat < 0 or etat >= nb_etats:
            raise ValueError(f"État initial invalide : {etat}")
    for etat in etats_terminaux:
        if etat < 0 or etat >= nb_etats:
            raise ValueError(f"État terminal invalide : {etat}")

    # Vérification du nombre de transitions
    if len(lignes) < 5 + nb_transitions:
        raise ValueError("Le fichier ne contient pas assez de transitions.")

    transitions = {}
    for ligne in lignes[5:5 + nb_transitions]:
        try:
            depart, symbole, arrivee = ligne.strip().split()
            depart, arrivee = int(depart), int(arrivee)
        except ValueError:
            raise ValueError(f"Format de transition invalide : {ligne}")

        # Vérification des états et symboles dans les transitions
        if depart < 0 or depart >= nb_etats:
            raise ValueError(f"État de départ invalide dans la transition : {depart} {symbole} {arrivee}")
        if arrivee < 0 or arrivee >= nb_etats:
            raise ValueError(f"État d'arrivée invalide dans la transition : {depart} {symbole} {arrivee}")
        if symbole != '€' and (len(symbole) != 1 or ord(symbole) - ord('a') < 0 or ord(symbole) - ord('a') >= nb_symboles):
            raise ValueError(f"Symbole invalide dans la transition : {symbole}")

        if (depart, symbole) not in transitions:
            transitions[(depart, symbole)] = set()
        transitions[(depart, symbole)].add(arrivee)

    return {
        'alphabet': [chr(ord('a') + i) for i in range(nb_symboles)],
        'etats': list(range(nb_etats)),
        'etats_initiaux': etats_initiaux,
        'etats_terminaux': etats_terminaux,
        'transitions': transitions
    }

def afficher_automate(automate):
    print("Alphabet:", automate['alphabet'])
    print("États:", automate['etats'])
    print("États initiaux:", automate['etats_initiaux'])
    print("États terminaux:", automate['etats_terminaux'])
    print("Transitions:")
    for (depart, symbole), arrivees in automate['transitions'].items():
        print(f"{depart} --{symbole}--> {arrivees}")

# ***************************************************************************************************************

def est_deterministe(automate):

    # Vérification des transitions
    if 'transitions' not in automate:
        raise ValueError("L'automate ne contient pas de transitions.")

    # Vérification du nombre d'états initiaux
    if 'etats_initiaux' not in automate or len(automate['etats_initiaux']) != 1:
        print("Cet automate n'a pas un unique état initial, il n'est pas déterministe")
        return False

    # Vérification des transitions pour chaque état et symbole
    for (depart, symbole), arrivees in automate['transitions'].items():
        if isinstance(arrivees, set):
            if len(arrivees) > 1:
                print("Cet automate a des états qui transitent vers plus d'un état avec le même symbole.")
                return False
        elif isinstance(arrivees, (str, int)):
            # Cas où arrivees est un état unique (chaîne ou entier)
            pass
        else:
            raise TypeError(f"Type de transition non supporté : {type(arrivees)}")

    print("Cet automate est déterministe")
    return True

def est_standard(automate):

    #si la case états initiaux est vide ou si le nombre d'états initiaux n'est pas 1 alors l'automate n'est pas standard
    if 'etats_initiaux' not in automate or len(automate['etats_initiaux']) != 1:
        print("Cet automate n'a pas 1 unique état initial, il n'est pas standard")
        return False

    etat_initial = automate['etats_initiaux'][0]
    for (depart, symbole), arrivees in automate['transitions'].items():
        if etat_initial in arrivees:
            print("Il y'a des transitions qui mènent à l'état initial de cet automate, il n'est pas standard")
            return False
    print("Cet automate est standard")
    return True

def est_complet(automate):

    incomplets = [] # pour stocker les états sans transitions

    for etat in automate['etats']:
        for symbole in automate['alphabet']:
            if (etat, symbole) not in automate['transitions']:
                incomplets.append((etat, symbole))

    if incomplets:
        print("L'automate est incomplet car les états suivants sont sans transitions :", incomplets)
        return False
    return True

def verifier_automate(automate):
    print("Déterministe :", est_deterministe(automate))
    print("Standard :", est_standard(automate))
    print("Complet :", est_complet(automate))

# **************************************************************************STANDARDISATION****

def standardiser(automate):

    import copy
    auto = copy.deepcopy(automate)  # On clone l’automate d’origine

    if est_standard(auto):
        return automate



    print("Création de l'automate standard : ")

    # Création d'un nouvel état initial
    nouvel_etat = max(auto['etats']) + 1
    auto['etats'].append(nouvel_etat)

    # Ajout du nouvel état initial
    anciens_initiaux = auto['etats_initiaux']
    auto['etats_initiaux'] = [nouvel_etat]

    # Vérifier si l'un des anciens états initiaux était terminal
    ancien_initial_est_terminal = any(etat in auto['etats_terminaux'] for etat in anciens_initiaux)

    # Si l'un des anciens états initiaux était terminal, le nouvel état initial doit également être terminal
    if ancien_initial_est_terminal:
        auto['etats_terminaux'].append(nouvel_etat)

    # Copie des transitions des anciens états initiaux vers le nouvel état initial
    for etat in anciens_initiaux:
        for symbole in auto['alphabet']:
            if (etat, symbole) in auto['transitions']:
                # Ajouter la transition du nouvel état initial vers les états d'arrivée des anciens états initiaux
                if (nouvel_etat, symbole) not in auto['transitions']:
                    auto['transitions'][(nouvel_etat, symbole)] = set()
                auto['transitions'][(nouvel_etat, symbole)].update(auto['transitions'][(etat, symbole)])

    afficher_automate(auto)
    return automate

# ********************************************************************************************

def fermeture_epsilon(automate, etats):

    fermeture = set(etats)
    pile = list(etats)
    while pile:
        etat = pile.pop()
        if (etat, '€') in automate['transitions']:
            for etat_arrivee in automate['transitions'][(etat, '€')]:
                if etat_arrivee not in fermeture:
                    fermeture.add(etat_arrivee)
                    pile.append(etat_arrivee)
    return fermeture

def contient_epsilon_transitions(automate):

    for (depart, symbole), arrivees in automate['transitions'].items():
        if symbole == '€':
            return True
    return False

def determiniser_automate_epsilon(automate):

    if est_deterministe(automate):
        print("L'automate est déjà déterministe")
        return automate

    print("L'automate n'est pas déterministe, création de l'automate déterministe : ")

    alphabet = automate['alphabet']
    transitions = automate['transitions']

    etats_afd = {}  # Dictionnaire {tuple etats : nom_etat}
    transitions_afd = {}

    # Initialisation de l'état initial (fermeture epsilon de l'état initial)
    etat_initial = tuple(sorted(fermeture_epsilon(automate, set(automate['etats_initiaux']))))
    nom_etat_initial = '_'.join(map(str, etat_initial))  # Nom de l'état initial
    etats_afd[etat_initial] = nom_etat_initial
    file = [etat_initial]

    while file:
        etat_courant = file.pop(0)
        nom_etat_courant = etats_afd[etat_courant]  # Récupérer le nom de l'état courant

        for symbole in alphabet:
            if symbole == '€':
                continue  # On ignore les transitions epsilon dans la déterminisation

            # Calculer les états atteignables avec le symbole courant
            etats_atteignables = set()
            for etat in etat_courant:
                if (etat, symbole) in transitions:
                    etats_atteignables.update(transitions[(etat, symbole)])

            # Calculer la fermeture epsilon des états atteignables
            etats_atteignables = fermeture_epsilon(automate, etats_atteignables)

            if not etats_atteignables:
                continue  # Pas de transition pour ce symbole

            # Créer un nouvel état (tuple trié pour l'unicité)
            nouvel_etat = tuple(sorted(etats_atteignables))

            # Si ce nouvel état n'a pas encore été vu, l'ajouter à la file
            if nouvel_etat not in etats_afd:
                nom_nouvel_etat = '_'.join(map(str, nouvel_etat))
                etats_afd[nouvel_etat] = nom_nouvel_etat
                file.append(nouvel_etat)

            # Ajouter la transition dans l'automate déterministe
            transitions_afd[(nom_etat_courant, symbole)] = etats_afd[nouvel_etat]

    # Identifier les états terminaux
    etats_terminaux_afd = {etats_afd[etat] for etat in etats_afd if any(e in automate['etats_terminaux'] for e in etat)}

    return {
        'alphabet': alphabet,
        'etats': set(etats_afd.values()),  # Retourner les noms des états
        'etats_initiaux': {etats_afd[etat_initial]},  # Le premier état a toujours le nom initial
        'etats_terminaux': etats_terminaux_afd,
        'transitions': transitions_afd
    }

# ***********************************************************************************************

def determiniser_automate(automate):
    if est_deterministe(automate):
        print("L'automate est déjà déterministe")
        return automate

    print("L'automate n'est pas déterministe, création de l'automate déterministe : ")

    alphabet = automate['alphabet']
    transitions = automate['transitions']

    etats_afd = {}  # Dictionnaire {tuple etats : nom_etat}
    transitions_afd = {}

    # Initialisation de l'état initial
    etat_initial = tuple(sorted(automate['etats_initiaux']))
    nom_etat_initial = '_'.join(map(str, etat_initial))  # Nom de l'état initial
    etats_afd[etat_initial] = nom_etat_initial
    file = [etat_initial]

    while file:
        etat_courant = file.pop(0)
        nom_etat_courant = etats_afd[etat_courant]  # Récupérer le nom de l'état courant

        for symbole in alphabet:
            etats_atteignables = set()
            for etat in etat_courant:
                if (etat, symbole) in transitions:
                    etats_atteignables.update(transitions[(etat, symbole)])

            # Si aucun état n'est atteint, on ignore cette transition (pas d'état puits ici)
            if not etats_atteignables:
                continue  # Pas de transition pour ce symbole, on passe au suivant

            # Créer un nouvel état (tuple trié pour l'unicité)
            nouvel_etat = tuple(sorted(etats_atteignables))

            # Si ce nouvel état n'a pas encore été vu, l'ajouter à la file
            if nouvel_etat not in etats_afd:
                nom_nouvel_etat = '_'.join(map(str, nouvel_etat))
                etats_afd[nouvel_etat] = nom_nouvel_etat
                file.append(nouvel_etat)

            # Ajouter la transition dans l'automate déterministe
            transitions_afd[(nom_etat_courant, symbole)] = etats_afd[nouvel_etat]

    # Identifier les états terminaux
    etats_terminaux_afd = {etats_afd[etat] for etat in etats_afd if any(e in automate['etats_terminaux'] for e in etat)}

    return {
        'alphabet': alphabet,
        'etats': set(etats_afd.values()),  # Retourner les noms des états
        'etats_initiaux': {etats_afd[etat_initial]},  # Le premier état a toujours le nom initial
        'etats_terminaux': etats_terminaux_afd,
        'transitions': transitions_afd
    }

def completer_automate(automate, debug=False):


    if not est_deterministe(automate):
        reponse = input("Cet automate n'est pas déterministe voulez-vous vraiment le completer? (ok/non) : ").strip().lower()

        if reponse != 'ok':
            print("Completion annulée")
            return automate



    # Vérifier si l'automate est déjà complet
    if est_complet(automate):
        if debug:
            print("L'automate est déjà complet")
        return automate

    print("Début de la complétion...")


    alphabet = automate['alphabet']
    etats = set(automate['etats'])  # utilisation d'un set pour éviter les doublons
    transitions = automate['transitions']


    try:
        etats_int = {int(e) for e in etats}  # Convertir en entiers si possible
        etat_puits = max(etats_int) + 1 if etats_int else 0  # Prend le plus grand ID disponible
    except ValueError:
        etat_puits = "puits"

        # Récupérer les transitions manquantes

    for etat, symbole in [(etat, symbole)
                          for etat in etats
                          for symbole in alphabet]:

        if (etat, symbole) not in transitions:
            transitions[(etat, symbole)] = etat_puits
            if debug:
                print(f"➕ Transition ajoutée : {etat} --({symbole})--> {etat_puits}")

    # boucler toutes les transitions des symboles sur le puit
    for symbole in alphabet:
        transitions[(etat_puits, symbole)] = etat_puits

    return {
        'alphabet': alphabet,
        'etats': etats,
        'etats_initiaux': automate['etats_initiaux'],
        'etats_terminaux': automate['etats_terminaux'],
        'transitions': transitions
    }

def determiniser_et_completer(automate):

    print("\nDébut de la déterminisation et de la complétion...")

    # Étape 1 : Vérifier si l'automate contient des transitions epsilon
    if contient_epsilon_transitions(automate):
        print("L'automate contient des transitions epsilon. Utilisation de determiniser_automate_epsilon.")
        automate_determinise = determiniser_automate_epsilon(automate)
    else:
        print("L'automate ne contient pas de transitions epsilon. Utilisation de determiniser_automate.")
        automate_determinise = determiniser_automate(automate)

    print("Automate déterminisé :")
    afficher_automate(automate_determinise)

    # Étape 2 : Complétion de l'automate déterminisé
    print("\nComplétion en cours...")
    automate_complet = completer_automate(automate_determinise, debug=True)
    print("Automate déterminisé et complet :")
    afficher_automate(automate_complet)

    return automate_complet

# ******************************************************************************************

def creer_automate_complementaire(automate, debug=False):


    # Vérification si l'automate est vide
    if not automate['etats']:
        if debug:
            print(" L'automate est vide, impossible de créer un complémentaire.")
        raise ValueError("L'automate est vide.")


    # Vérification si l'automate est déterministe et complet
    print("Complémentarisation:")
    try:

        automate = determiniser_automate(automate)



        automate = completer_automate(automate, debug)
    except Exception as e:
        raise ValueError(f"Erreur lors de la déterminisation ou de la complétion : {e}")

    # Fin de la vérification de déterminisation et de complétion
    print("création de l'automate complémentaire : ")


    # Création d'une copie de l'automate pour éviter de le modifier directement
    import copy
    automate_complementaire = copy.deepcopy(automate)



    # Fonction complémentaire écrit explicitement
    anciens_terminaux = automate['etats_terminaux']

    automate_complementaire['etats_terminaux'] = set(automate['etats']) - set(anciens_terminaux)

    if debug:
        print(f"États terminaux avant : {anciens_terminaux}")
        print(f"Nouveaux états terminaux : {automate_complementaire['etats_terminaux']}")

    return automate_complementaire

# ******************************************************************************************************

def reconnaitre_mot(automate, mot):
    # Vérification que l'automate possède un état initial unique
    if len(automate['etats_initiaux']) != 1:
        raise ValueError("L'automate doit avoir un seul état initial.")

    # Vérifier si le mot est "end" (pour quitter)
    if mot == "end":
        print("Fin de la reconnaissance de mots.")
        return True

    # Récupération de l'état initial unique
    etat_courant = next(iter(automate['etats_initiaux']))

    # Parcours du mot
    for symbole in mot:
        # Vérifier que le symbole appartient à l'alphabet de l'automate
        if symbole not in automate['alphabet']:
            print(f"❌ Symbole '{symbole}' non reconnu dans l'alphabet de l'automate.")
            return False

        # Vérifier si une transition existe pour (état_courant, symbole)
        if (etat_courant, symbole) in automate['transitions']:
            # Extraire l'état suivant (gestion des sets et des chaînes)
            arrivees = automate['transitions'][(etat_courant, symbole)]
            if isinstance(arrivees, set):
                etat_courant = next(iter(arrivees))  # Prendre le premier état du set
            else:
                etat_courant = arrivees  # Cas où arrivees est un état unique (chaîne ou entier)
        else:
            print(f"❌ Aucune transition pour ({etat_courant}, '{symbole}'). Le mot est rejeté.")
            return False

    # Vérifier si l'état final atteint est un état terminal
    if etat_courant in automate['etats_terminaux']:
        print(f"✅ Le mot '{mot}' est accepté.")
        return True
    else:
        print(f"❌ Le mot '{mot}' est rejeté (état final {etat_courant} non terminal).")
        return False

# ******************************************************************************************************

def reconnait_uniquement_mot_vide(automate):

    # Vérifier qu'il y a un seul état initial
    if len(automate['etats_initiaux']) != 1:
        return False

    # Accéder au premier élément de l'ensemble sans le convertir en liste
    etat_initial = next(iter(automate['etats_initiaux']))

    # Vérifier que l'état initial est également un état terminal
    if etat_initial not in automate['etats_terminaux']:
        return False

    # Vérifier qu'aucune transition ne part de l'état initial
    for (depart, symbole), arrivees in automate['transitions'].items():
        if depart == etat_initial:
            return False

    # Si toutes les conditions sont remplies, l'automate reconnaît uniquement le mot vide
    return True
def minimiser_automate(automate):

    import copy
    auto = copy.deepcopy(automate)  # On clone l’automate d’origine

    # Vérifier si l'automate reconnaît uniquement le mot vide
    if reconnait_uniquement_mot_vide(automate):
        print("L'automate reconnaît uniquement le mot vide. Retour d'un automate minimal.")
        return {
            'alphabet': auto['alphabet'],
            'etats': [0],  # Un seul état
            'etats_initiaux': [0],  # L'état initial
            'etats_terminaux': [0],  # L'état initial est également terminal
            'transitions': {}  # Aucune transition
        }

    # Vérifier si l'automate est déterministe et complet
    if not est_deterministe(auto):
        print("L'automate n'est pas déterministe. Déterminisation en cours...")
        auto = determiniser_automate(auto)

    if not est_complet(auto):
        print("L'automate n'est pas complet. Complétion en cours...")
        auto = completer_automate(auto)

    print("Automate minimisé...")

    # Étape 1 : Initialisation des partitions
    etats = auto['etats']
    etats_terminaux = auto['etats_terminaux']
    etats_non_terminaux = set(etats) - set(etats_terminaux)

    # Partition initiale : séparer les états terminaux et non terminaux
    P = [set(etats_terminaux), set(etats_non_terminaux)]
    W = [set(etats_terminaux)]  # Liste des groupes à traiter

    # Étape 2 : Raffinement des partitions
    while W:
        A = W.pop(0)  # Prendre un groupe à traiter
        for symbole in auto['alphabet']:
            # Trouver tous les états qui mènent à A avec ce symbole
            X = set()
            for etat in etats:
                if (etat, symbole) in auto['transitions']:
                    arrivee = auto['transitions'][(etat, symbole)]
                    if isinstance(arrivee, set):  # Si l'arrivée est un ensemble
                        arrivee = next(iter(arrivee))
                    if arrivee in A:
                        X.add(etat)

            # Diviser les groupes de P en fonction de X
            nouvelle_P = []
            for Y in P:
                inter = Y & X
                diff = Y - X
                if inter and diff:
                    nouvelle_P.append(inter)
                    nouvelle_P.append(diff)
                    if Y in W:
                        W.remove(Y)
                        W.append(inter)
                        W.append(diff)
                    else:
                        W.append(inter if len(inter) <= len(diff) else diff)
                else:
                    nouvelle_P.append(Y)
            P = nouvelle_P

    # Étape 3 : Construire le nouvel automate minimisé
    etats_minimises = {}
    transitions_minimises = {}

    # Associer chaque groupe de P à un nouvel état
    for idx, groupe in enumerate(P):
        if not groupe:  # Vérifier que le groupe n'est pas vide
            continue  # Ignorer les groupes vides
        nom_etat = f"q{idx}"
        etats_minimises[nom_etat] = groupe

    # Construire les transitions
    for nom_etat, groupe in etats_minimises.items():
        if not groupe:  # Vérifier que le groupe n'est pas vide
            continue  # Ignorer les groupes vides
        etat_repr = next(iter(groupe))  # Prendre un représentant du groupe
        for symbole in auto['alphabet']:
            if (etat_repr, symbole) in auto['transitions']:
                arrivee = auto['transitions'][(etat_repr, symbole)]
                if isinstance(arrivee, set):  # Si l'arrivée est un ensemble
                    arrivee = next(iter(arrivee))
                # Trouver le groupe contenant l'état d'arrivée
                for nom_etat_arrivee, groupe_arrivee in etats_minimises.items():
                    if arrivee in groupe_arrivee:
                        transitions_minimises[(nom_etat, symbole)] = {nom_etat_arrivee}
                        break

    # Identifier les états initiaux et terminaux minimisés
    etats_initiaux_minimises = set()
    etats_terminaux_minimises = set()

    for nom_etat, groupe in etats_minimises.items():
        if any(etat in auto['etats_initiaux'] for etat in groupe):
            etats_initiaux_minimises.add(nom_etat)
        if any(etat in auto['etats_terminaux'] for etat in groupe):
            etats_terminaux_minimises.add(nom_etat)

    # Retourner l'automate minimisé
    return {
        'alphabet': auto['alphabet'],
        'etats': list(etats_minimises.keys()),
        'etats_initiaux': list(etats_initiaux_minimises),
        'etats_terminaux': list(etats_terminaux_minimises),
        'transitions': transitions_minimises
    }




def executer_tests_et_sauvegarder_traces(nom_fichier_automate, nom_fichier_traces):
    import sys
    from io import StringIO

    # Rediriger la sortie standard vers un buffer
    old_stdout = sys.stdout
    sys.stdout = buffer = StringIO()

    try:
        # Étape 1 : Lecture de l'automate
        print(f"=== Lecture de l'automate depuis le fichier {nom_fichier_automate} ===")
        automate = lire_automate(nom_fichier_automate)
        afficher_automate(automate)

        # Étape 2 : Vérification des propriétés de l'automate
        print("\n=== Vérification des propriétés de l'automate ===")
        verifier_automate(automate)

        # Étape 3 : Standardisation si nécessaire
        print("\n=== Standardisation de l'automate ===")
        if not est_standard(automate):
            automate = standardiser(automate)
        else:
            print("L'automate est déjà standard.")

        # Étape 4 : Déterminisation et complétion
        print("\n=== Déterminisation et complétion de l'automate ===")
        automate_determinise_complet = determiniser_et_completer(automate)

        # Étape 5 : Utilisation de l'automate déterministe et complet pour la reconnaissance des mots
        print("\n=== Reconnaissance de mots avec l'automate déterministe et complet ===")
        mots_a_tester = ["","a","b","c","d","abbcd","accccccd","e","f","aaaaa","ababa","acbd","acbbbbbd","ccbdadb","abaaa","abcd","aaaba", "ba", "aab","aaaaaaaaaaaa","ababababaaab","aba","bbbb","bbaabab" "end"]
        for mot in mots_a_tester:
            if mot == "end":
                break
            print(f"\nTest du mot : {mot}")
            reconnaitre_mot(automate_determinise_complet, mot)

        # Étape 6 : Création de l'automate complémentaire
        print("\n=== Création de l'automate complémentaire ===")
        automate_complementaire = creer_automate_complementaire(automate_determinise_complet)
        afficher_automate(automate_complementaire)

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
    finally:
        # Restaurer la sortie standard
        sys.stdout = old_stdout

        # Sauvegarder les traces dans un fichier texte
        with open(nom_fichier_traces, 'w', encoding='utf-8') as fichier_traces:
            fichier_traces.write(buffer.getvalue())

        print(f"Les traces ont été sauvegardées dans le fichier {nom_fichier_traces}.")

#executer_tests_et_sauvegarder_traces("automate/automate14.txt","automate014_traces")
