# Plano Agente PCPE 2026

Sistema pessoal de estudos para o concurso de **Agente de Polícia da Polícia Civil de Pernambuco** (Edital nº 1 – PCPE, de 2/10/2026, banca Cebraspe).

Roda inteiro no navegador com [sql.js](https://github.com/sql-js/sql.js) (SQLite compilado para JavaScript). Não tem servidor nem login.

## O que tem

- **Edital**: 11 matérias e 112 tópicos com status (pendente → estudando → revisar → dominado), contador de revisões e registro de sessões de estudo.
- **Materiais**: legislação oficial (ALEPE e Planalto), questões, provas anteriores e busca de videoaulas por tópico.
- **TAF**: índices mínimos, plano de treino em 4 fases até 30/07/2027 e registro de marcas.
- **Agenda**: cronograma oficial do Anexo I.
- **SQL**: console para consultar o banco.

## Onde fica o progresso

O progresso fica salvo no `localStorage` do navegador. Para levar a outro aparelho ou guardar cópia, use **Baixar backup (.json)** e depois **Importar backup**. **Baixar banco (.db)** exporta o SQLite inteiro com seu progresso.

## Estrutura

```
index.html            app
data/pcpe_agente.db   banco inicial (seed)
data/schema.sql       schema
scripts/seed.py       gera o banco do zero: python3 scripts/seed.py
```

Para regenerar o banco: `cd data && python3 ../scripts/seed.py`.

## Publicar no GitHub Pages

Settings → Pages → Source: *Deploy from a branch* → Branch `main`, pasta `/ (root)`.

## Rodar localmente

```
python3 -m http.server 8000
```
e abra http://localhost:8000 (abrir o arquivo direto com `file://` não carrega o banco).
