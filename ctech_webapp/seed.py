from dotenv import load_dotenv
load_dotenv()

from werkzeug.security import generate_password_hash
import mysql.connector
import os

from werkzeug.security import generate_password_hash
import mysql.connector
import os
conn=mysql.connector.connect(host=os.getenv('DB_HOST','localhost'),port=int(os.getenv('DB_PORT','3306')),user=os.getenv('DB_USER','root'),password=os.getenv('DB_PASSWORD','root'),database=os.getenv('DB_NAME','ctech'))
cur=conn.cursor()
cur.execute("UPDATE users SET password_hash=%s WHERE email='admin@ctech.com'", (generate_password_hash('123456'),))
conn.commit(); cur.close(); conn.close()
print('Usuário de teste: admin@ctech.com | senha: 123456')
