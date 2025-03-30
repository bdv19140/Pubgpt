
# Assistant IA Sponsorisé

Ce projet est une application web construite avec **Flask** et **GPT (OpenAI)**, qui répond aux questions des utilisateurs tout en intégrant des **recommandations sponsorisées via Amazon**.

## Fonctionnalités

- Extraction automatique des mots-clés à partir des questions
- Recherche de produits sur Amazon en fonction de ces mots-clés
- Génération de réponses enrichies avec des liens affiliés
- Interface web simple et responsive

## Dépendances

Installe-les via pip :

```bash
pip install -r requirements.txt
```

## Variables d’environnement

Crée un fichier `.env` ou configure ces variables dans Render :

- `OPENAI_API_KEY` — ta clé API OpenAI
- `ACCESS_KEY` — ta clé Amazon Product Advertising
- `SECRET_KEY` — ta clé secrète Amazon
- `ASSOCIATE_TAG` — ton identifiant d'affiliation Amazon

## Lancer en local

```bash
python app.py
```

Puis ouvre [http://localhost:5000](http://localhost:5000)

## Déploiement sur Render

1. Crée un compte sur https://render.com
2. Connecte ton GitHub et sélectionne ce dépôt
3. Configure :
   - **Build command** : `pip install -r requirements.txt`
   - **Start command** : `python app.py`
   - **Environment** : Python 3.10+
4. Ajoute les variables d’environnement

## Auteurs

Créé par [Ton Nom ou Nom de projet]

---

*Ce projet combine intelligence artificielle et monétisation par affiliation. Utilisation libre avec mention de l’auteur.*
