import requests, re, json
from flask import Flask
from flask_cors import CORS

BASE_URL = 'https://www.dicio.com.br'

app = Flask(__name__)
CORS(app)

sizes = [
    'tres', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove', 'dez'
    ]

def get_url_suffix_for_word_size(size):
    if size > 10 and size < 20:
        return f'palavras-com-{size}-letras-10'
    
    size_as_word = sizes[size - 3]
    return f'palavras-com-{size_as_word}-letras'


def save_words_to_cache(content):
    try:
        size = content['size']
        with open(f'palavras/{size}.json', 'w') as handler:
            json.dump(content, handler, ensure_ascii=False, indent=4)
    
    except Exception as e:
        print(f"Couldn't save response: {e}")

def get_words_from_cache(size):
    try:        
        with open(f'palavras/{size}.json', 'r') as handler:
            return json.load(handler)
    
    except Exception as e:
        print(f"Couldn't get response: {e}")

def valid_size(size):
    return size < 17 and size > 0

@app.route('/list_words_by_size/<int:size>', methods=['GET'])
def words_by_size(size):
    if not valid_size(size):
        raise ValueError('Valor inválido')    
    maybe = get_words_from_cache(size)
    if maybe:
        print(f'Returning cache for {size}')
        return maybe
    print(f'Will try to fetch words for size {size}')
    fetched = fetch_words(size)
    words_obj = extract_words(fetched, size)
    save_words_to_cache(words_obj)
    return words_obj

def fetch_words(size):
    suffix = get_url_suffix_for_word_size(size)
    url = BASE_URL + f'/{suffix}/'
    print(f"Fetching '{url}'")
    resp = requests.get(url)
    return resp.text

def extract_words(content, size):
    ptn = "(?<=)[^ :]{" + str(size) + "}(?=<br\s?\/>)"
    words = re.findall(ptn, content)
    return {'size': size, 'words': words}


app.run(debug=True, port=5500, host='0.0.0.0')