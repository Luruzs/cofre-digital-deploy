# cofre-digital-deploy
from flask import Flask, jsonify 
import os 
import logging 
app = Flask(__name__) 
 
•	Configurando logging (importante para máscaras) 
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__) 
@app.route('/') 
def home(): 
    return jsonify({ 
        "message": " Cofre Digital Online!", 
        "environment": os.getenv('ENVIRONMENT', 'unknown'), 
        "version": os.getenv('APP_VERSION', '1.0.0') 
 
    }) 
@app.route('/database') 
def database_info(): 
 
•	Simulando conexão com banco (usando segredos) 
    db_host = os.getenv('DB_HOST', 'localhost') 
    db_user = os.getenv('DB_USER', 'user') 
    db_password = os.getenv('DB_PASSWORD', 'SENHA_NAO_CONFIGURADA')
   
     Atenção! Nunca logar senhas reais!  
    logger.info(f"Conectando ao banco: {db_host} com usuário: {db_user}") 
 
    Nunca façam isso: #logger.info(f"Senha: {db_password}")      
    return jsonify({  
        "status": "connected" if db_password != 'SENHA_NAO_CONFIGURADA' else "not_configured", 
        "host": db_host, 
        "user": db_user,
        "password_configured": db_password != 'SENHA_NAO_CONFIGURADA' 
    }) 
@app.route('/api-key') 
def api_key_info(): 
 
•	Simulando uso de API key externa  
    api_key = os.getenv('EXTERNAL_API_KEY', 'KEY_NAO_CONFIGURADA') 
   
o	Mascarando a chave nos logs  
    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****" 
    logger.info(f"Usando API Key: {masked_key}") 
    return jsonify({ 
        "api_configured": api_key != 'KEY_NAO_CONFIGURADA', 
        "key_preview": masked_key
    }) 
if __name__ == '__main__': 
    port = int(os.getenv('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port, debug=False)
 
 
•	Criando requirements:  
#app/requirements.txt 
 
Flask==2.3.3 
gunicorn==21.2.0

Parte 3: Containerizando com segurança (o cofre portátil) 
Vamos criar um container image que pode ser usado em qualquer ambiente:  

1.	Dockerfile seguro:  
# docker/Dockerfile - Nosso "cofre portátil" 
 
FROM python:3.11-slim  
# Criando usuário não-root (segurança) 
RUN useradd --create-home --shell /bin/bash appuser
 
# Definindo diretório de trabalho 
WORKDIR /app 
 
•	Copiando requirements primeiro (cache do Docker)  
COPY app/requirements.txt . 
 
•	Instalando dependências  
RUN pip install --no-cache-dir -r requirements.txt 
 
•	Copiando código da aplicação  
COPY app/ .
 
•	Mudando para usuário não-root  
USER appuser 
 
•	Expondo porta (configurável via variável)  
EXPOSE ${PORT:-5000} 
 
•	Comando de inicialização  
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"] 
 
2.	Docker compose para desenvolvimento:  
# docker-compose.yml - Para testes locais  
version: '3.8'  
services:  
  app:  
    build:  
      context: .  
      dockerfile: docker/Dockerfile 
    ports:  
      - "5000:5000" 
    environment:  
      - ENVIRONMENT=development 
      - APP_VERSION=1.0.0  
      - DB_HOST=localhost  
      - DB_USER=dev_user  
      - DB_PASSWORD=dev_password_123 
      - EXTERNAL_API_KEY=dev_key_abcd1234efgh5678  
      - PORT=5000  
    volumes: 
      - ./app:/app
 
