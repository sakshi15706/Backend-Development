# Unit 1 (P-6): Server-Side Rendering with EJS and Jinja2

## Aim
Render HTML on the server by combining templates with data, using EJS (Node.js/Express) and Jinja2 (Python/Flask).

## Part A: EJS (Node.js)
```bash
cd "unit-1(P-6)/ejs-app"
npm install
npm start          # http://localhost:3000
```

## Part B: Jinja2 (Flask)
```bash
cd "unit-1(P-6)/jinja-app"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py      # http://localhost:5001
```

## Concepts compared
| Idea | EJS | Jinja2 |
|---|---|---|
| Print a value | `<%= name %>` | `{{ name }}` |
| Loop | `<% items.forEach(...) %>` | `{% for item in items %}` |
| Condition | `<% if (x) { %>` | `{% if x %}` |
| Include / reuse | `<%- include('partials/header') %>` | `{% extends "base.html" %}` |
