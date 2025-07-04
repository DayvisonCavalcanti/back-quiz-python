
# 📚 Quiz API

API completa para criação de quizzes, submissão de respostas e acompanhamento de histórico de usuários.

---

## ✅ Pré-requisitos

- Python **3.10** ou superior  
- Conta no [Supabase](https://supabase.com/) para o banco de dados  
- [Postman](https://www.postman.com/) para testar as rotas

---

## ⚙️ Configuração Inicial

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/quiz-api.git
cd quiz-api
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
```

### 3. Ative o ambiente virtual

- **Windows:**

  ```bash
  venv\Scripts\activate
  ```

- **Linux/Mac:**

  ```bash
  source venv/bin/activate
  ```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Configure o Supabase

1. Crie uma conta e projeto no [Supabase](https://supabase.com)  
2. Acesse as configurações e obtenha:
   - **URL da API**
   - **Chave de API** (`service_role`)
3. Crie o arquivo `.env` na raiz do projeto:

```env
SUPABASE_URL=sua_url_supabase
SUPABASE_KEY=sua_chave_supabase
SECRET_KEY=sua_chave_secreta_jwt  # Ex: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 6. Crie as tabelas no Supabase

Execute no editor SQL do Supabase:

```sql
-- Tabela de usuários
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Tabela de quizzes
CREATE TABLE quizzes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    creator_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de perguntas
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id),
    text TEXT NOT NULL,
    options JSONB NOT NULL,
    correct_option INTEGER NOT NULL
);

-- Tabela de tentativas
CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    quiz_id UUID NOT NULL REFERENCES quizzes(id),
    score FLOAT NOT NULL,
    answers JSONB NOT NULL,
    completed_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🚀 Executando a API

```bash
uvicorn app:app --reload
```

Acesse em: [http://localhost:8000](http://localhost:8000)

---

## 🧪 Testando as Rotas com Postman

[![Run in Postman](https://run.pstmn.io/button.svg)](https://www.postman.com/)

Ou importe manualmente o arquivo: `Quiz-API.postman_collection.json`

---

## 🧭 Fluxo de Teste

### 1. Registrar administrador

```http
POST /users/register
Content-Type: application/json

{
  "email": "admin@example.com",
  "name": "Admin User",
  "password": "admin123",
  "is_admin": true
}
```

### 2. Obter token (login)

```http
POST /auth/token
Content-Type: application/json

{
  "username": "admin@example.com",
  "password": "admin123"
}
```

> Salve o token como `admin_token`.

### 3. Criar quiz com perguntas

```http
POST /quizzes/with-questions
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "title": "Quiz de Matemática",
  "description": "Teste seus conhecimentos matemáticos",
  "category": "Matemática",
  "questions": [
    {
      "text": "Quanto é 5 × 6?",
      "options": ["30", "25", "36", "35"],
      "correct_option": 0
    },
    {
      "text": "Qual é a raiz quadrada de 144?",
      "options": ["12", "14", "16", "18"],
      "correct_option": 0
    }
  ]
}
```

> Salve o `quiz_id` e os `question_id`s retornados.

### 4. Registrar usuário comum

```http
POST /users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "Regular User",
  "password": "user123",
  "is_admin": false
}
```

### 5. Obter token do usuário

```http
POST /auth/token
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "user123"
}
```

> Salve como `user_token`.

### 6. Submeter respostas

```http
POST /history/submit-quiz
Authorization: Bearer {{user_token}}
Content-Type: application/json

{
  "quiz_id": "{{quiz_id}}",
  "responses": [
    {
      "question_id": "{{question_id_1}}",
      "selected_option": 0
    },
    {
      "question_id": "{{question_id_2}}",
      "selected_option": 0
    }
  ]
}
```

### 7. Ver histórico

```http
GET /history/me
Authorization: Bearer {{user_token}}
```

---

## 📁 Estrutura do Projeto

```text
.
├── app.py                  # Ponto de entrada
├── database
│   └── supabase_client.py  # Cliente do Supabase
├── models                  # Modelos Pydantic
│   ├── user.py
│   ├── quiz.py
│   ├── question.py
│   └── history.py
├── routes                  # Rotas da API
│   ├── auth.py
│   ├── users.py
│   ├── quizzes.py
│   ├── questions.py
│   └── history.py
├── services                # Regras de negócio
│   ├── auth.py
│   ├── user.py
│   ├── quiz.py
│   ├── question.py
│   └── history.py
├── config.py               # Configurações da aplicação
├── requirements.txt        # Dependências
└── .env                    # Variáveis de ambiente
```

---

## 🔗 Rotas Disponíveis

| Método | Rota                        | Descrição                            | Autenticação |
|--------|-----------------------------|--------------------------------------|---------------|
| POST   | `/users/register`           | Registra um novo usuário             | ❌            |
| POST   | `/auth/token`               | Login e obtenção de token            | ❌            |
| GET    | `/users/me`                 | Dados do usuário autenticado         | ✅            |
| GET    | `/users/admin/me`           | Dados do admin autenticado           | ✅ (Admin)     |
| POST   | `/quizzes/with-questions`   | Cria um quiz com perguntas           | ✅ (Admin)     |
| POST   | `/questions/batch`          | Adiciona perguntas em lote           | ✅ (Admin)     |
| POST   | `/history/submit-quiz`      | Submete respostas de quiz            | ✅            |
| GET    | `/history/me`               | Visualiza histórico do usuário       | ✅            |

---

## 📦 Dependências (`requirements.txt`)

```txt
fastapi==0.110.0
uvicorn==0.29.0
supabase==2.4.1
python-jose[cryptography]==3.3.0
passlib==1.7.4
python-multipart==0.0.9
python-dotenv==1.0.1
pydantic-settings==2.2.1
```

---

## 🛠️ Solução de Problemas

- **401 Unauthorized**: Token inválido ou expirado – faça login novamente.  
- **403 Forbidden**: Permissões insuficientes – o usuário precisa ser admin.  
- **404 Not Found**: Recurso não encontrado – verifique os IDs usados.  
- **500 Internal Server Error**: Verifique os logs no terminal.

---

## 🤝 Contribuindo

1. Fork este repositório  
2. Crie uma branch: `git checkout -b feature/nome-da-feature`  
3. Commit suas mudanças: `git commit -m 'Add nova feature'`  
4. Push para sua branch: `git push origin feature/nome-da-feature`  
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais informações.
