from pyngrok import ngrok
import os
from dotenv import load_dotenv

load_dotenv()

# Configura o Authtoken do seu .env
ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))

# Abre um túnel para a porta padrão do Streamlit (8501)
public_url = ngrok.connect(8501)
print(f"🚀 Dashboard Online em: {public_url}")
