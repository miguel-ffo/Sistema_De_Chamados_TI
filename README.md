# 📌 Sistema de Chamados para Suportes de TI

## 🚀 Configuração do Ambiente

Siga os passos abaixo para configurar e executar o projeto localmente.

---

### 1️⃣ Criar ambiente virtual
```bash
python -m venv venv
```

### 2️⃣ Ativar ambiente virtual
- **Windows**
```bash
venv\Scripts\activate
```
- **Linux/Mac**
```bash
source venv/bin/activate
```

### 3️⃣ Instalar dependências
```bash
pip install -r requirements.txt
```

### 4️⃣ Acessar a pasta do backend
```bash
cd backend
```

### 5️⃣ Criar e aplicar migrações do banco de dados
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6️⃣ Popular o banco de dados com dados iniciais
```bash
python manage.py shell -c "exec(open('popular_dados.py', encoding='utf-8').read())"
```

---

## ⚙️ Configuração do arquivo `.env`

1. Crie o arquivo `.env` na raiz do projeto.
2. Copie o conteúdo do arquivo `.env.example`.
3. Edite as chaves conforme necessário.

---

## 👤 Criar usuário administrador
```bash
python manage.py createsuperuser
```

---

## ▶️ Executar o servidor
```bash
python manage.py runserver
```

Após executar, o sistema estará disponível em:
```
http://127.0.0.1:8000
```
