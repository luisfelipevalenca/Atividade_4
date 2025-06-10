# Gerenciador de Tarefas com Flask

Este projeto é uma API RESTful simples desenvolvida com Flask e SQLAlchemy para gerenciamento de tarefas com autenticação básica e por token JWT.

## Funcionalidades

- Login via autenticação básica para obter um token JWT
- Listar tarefas
- Adicionar tarefas
- Atualizar tarefas (autenticado via token)
- Marcar tarefas como pendente/concluída (autenticado via token)
- Remover tarefas (autenticado via token)

## Requisitos

- Python 3.x
- Flask
- Flask-SQLAlchemy
- PyJWT

## Instalação

```bash
pip install Flask Flask-SQLAlchemy PyJWT Werkzeug
```

## Como executar

```bash
python atividade_4.py
```

A aplicação estará disponível em `http://localhost:5000`

## Endpoints

### Autenticação

**POST /login**

Autenticação básica via `admin` / `123_base64`. Retorna token JWT.

### Tarefas

**GET /tarefas**
- Lista todas as tarefas

**POST /tarefas**
- Adiciona uma nova tarefa
- JSON: `{ "descricao": "Texto da tarefa" }`

**PUT /tarefas/<id>**
- Atualiza a descrição/status de uma tarefa
- Requer token JWT no cabeçalho

**PATCH /tarefas/<id>/pendente**
- Marca a tarefa como pendente
- Requer token JWT

**PATCH /tarefas/<id>/concluida**
- Marca a tarefa como concluída
- Requer token JWT

**DELETE /tarefas/<id>**
- Remove a tarefa
- Requer token JWT

## Banco de Dados

- Utiliza SQLite (arquivo `tarefas.db`)
- O banco é criado automaticamente na primeira execução

## Segurança

- Autenticação básica para login
- JWT para autenticação em operações protegidas


