
from flask import Flask, render_template, request
import openai
import requests
import xmltodict
import hashlib
import hmac
import time

# Clés API
OPENAI_API_KEY = 'TA_CLE_OPENAI'
ACCESS_KEY = 'TA_CLE_AMAZON'
SECRET_KEY = 'TA_CLE_SECRETE_AMAZON'
ASSOCIATE_TAG = 'TON_TAG_ASSOCIE_AMAZON'

openai.api_key = OPENAI_API_KEY
ENDPOINT = "webservices.amazon.com"
URI = "/onca/xml"

app = Flask(__name__)

def extraire_mots_cles_gpt(question):
    prompt = (
        "Tu es un extracteur de mots-clés. "
        f"Voici une question d'utilisateur : \"{question}\"\n"
        "Donne-moi 2 ou 3 mots-clés les plus importants, séparés par des virgules, sans phrase autour."
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    mots_cles = response['choices'][0]['message']['content']
    return [mot.strip() for mot in mots_cles.split(',')]

def sign_request(params):
    params['Timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    sorted_params = sorted(params.items())
    query_string = '&'.join([f"{k}={requests.utils.quote(str(v))}" for k, v in sorted_params])
    string_to_sign = f"GET\n{ENDPOINT}\n{URI}\n{query_string}"
    signature = hmac.new(bytes(SECRET_KEY, 'utf-8'), msg=bytes(string_to_sign, 'utf-8'), digestmod='sha256').digest()
    signature = requests.utils.quote(signature)
    return f"https://{ENDPOINT}{URI}?{query_string}&Signature={signature}"

def chercher_produit_amazon(mot_cle):
    params = {
        'Service': 'AWSECommerceService',
        'Operation': 'ItemSearch',
        'SearchIndex': 'All',
        'Keywords': mot_cle,
        'ResponseGroup': 'Images,ItemAttributes,Offers',
        'AssociateTag': ASSOCIATE_TAG,
        'AWSAccessKeyId': ACCESS_KEY
    }
    signed_url = sign_request(params)
    response = requests.get(signed_url)
    if response.status_code != 200:
        return None

    data = xmltodict.parse(response.text)
    items = data.get('ItemSearchResponse', {}).get('Items', {}).get('Item', [])
    if not isinstance(items, list): items = [items]

    for item in items:
        try:
            return {
                'titre': item.get('ItemAttributes', {}).get('Title', ''),
                'lien': item.get('DetailPageURL', ''),
                'image': item.get('MediumImage', {}).get('URL', '')
            }
        except:
            continue
    return None

def generer_reponse_finale(question, produit):
    contexte_pub = (
        f"Si pertinent, insère subtilement cette recommandation dans ta réponse : "
        f"\"{produit['titre']} est un produit utile dans ce contexte. Tu peux le découvrir ici : {produit['lien']}\""
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
        produit = None
        for mot in mots_cles:
            produit = chercher_produit_amazon(mot)
            if produit:
                break
        if produit:
            reponse = generer_reponse_finale(question, produit)
        else:
            reponse = "Je n'ai pas trouvé de produit sponsorisé pertinent, mais voici ma réponse :"
        return render_template('index.html', question=question, reponse=reponse, produit=produit)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host='0.0.0.0', port=port)
