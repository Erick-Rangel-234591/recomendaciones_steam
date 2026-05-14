python 3.14

---

python -m venv venv

venv/Scripts/Activate

pip install -r requirements.txt

---

crear archivo .env en raiz del proyecto y meter esto:

STEAM_API_KEY=PegaTuClaveDe32CaracteresAqui

se obtiene de aqui: https://steamcommunity.com/dev/apikey

---

uvicorn backend.main:app --reload
