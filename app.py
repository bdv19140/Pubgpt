
from flask import Flask, render_template, request
import openai
import os

# ClÃ©s API (uniquement OpenAI dans cette version)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Produits sponsorisÃ©s fictifs
produits_test = [
    {
        "keywords": ["sommeil", "stress", "dormir"],
        "titre": "Tisane Bio RelaxZen",
        "lien": "https://exemple.com/produit/tisane-relaxzen",
        "image": "https://via.placeholder.com/100?text=RelaxZen"
    },
    {
        "keywords": ["concentration", "travail", "focus"],
        "titre": "ComplÃ©ment FocusPro",
        "lien": "https://exemple.com/produit/focuspro",
        "image": "https://via.placeholder.com/100?text=FocusPro"
    },
    {
        "keywords": ["digestion", "ventre", "repas"],
        "titre": "Infusion DigestZen",
        "lien": "https://exemple.com/produit/digestzen",
        "image": "https://via.placeholder.com/100?text=DigestZen"
    }
]

def extraire_mots_cles_gpt(question):
    prompt = (
        "Tu es un extracteur de mots-clÃ©s. "
        f"Voici une question d'utilisateur : \"{question}\"\n"
        "Donne-moi 2 ou 3 mots-clÃ©s les plus importants, sÃ©parÃ©s par des virgules, sans phrase autour."
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    mots_cles = response['choices'][0]['message']['content']
    return [mot.strip().lower() for mot in mots_cles.split(',')]

def trouver_produit_correspondant(mots_cles):
    for produit in produits_test:
        if any(mot in produit["keywords"] for mot in mots_cles):
            return produit
    return produits_test[0]  # fallback si rien ne matche

def generer_reponse_finale(question, produit):
    contexte_pub = (
        f"Si pertinent, insÃ¨re subtilement cette recommandation dans ta rÃ©ponse : "
        f"\"{produit['titre']} est un produit utile dans ce contexte. Tu peux le dÃ©couvrir ici : {produit['lien']}\""
    )
    prompt = f"{contexte_pub}\n\nVoici la question utilisateur : {question}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response['choices'][0]['message']['content']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        question = request.form['question']
        mots_cles = extraire_mots_cles_gpt(question)
        produit = trouver_produit_correspondant(mots_cles)
        reponse = generer_reponse_finale(question, produit)
        return render_template('index.html', question=question, reponse=reponse, produit=produit)
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host='0.0.0.0', port=port)
