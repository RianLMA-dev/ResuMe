# Avaliação do classificador e do extrator

`dataset.jsonl` tem 53 e-mails **sintéticos**: empresas, pessoas, links e vagas são fictícios.
Eles foram escritos a partir do *formato* de e-mails reais de processos seletivos (confirmação de
candidatura, teste, entrevista, proposta, rejeição, newsletters, alertas de vagas), mas nenhum
trecho, nome ou empresa real foi copiado. Assim o repositório público não expõe histórico pessoal.

| Grupo | Casos | Para que serve |
|---|---|---|
| Processo seletivo | 37 | Mede se o extrator acerta status, empresa e cargo. Cobre os 7 status. |
| Não é processo | 12 | Mede falsos positivos (newsletter, alerta de vagas, curso, compra, rede social). |
| Ambíguos | 4 | Reportados à parte, fora da nota (abordagem de recrutador, seleção acadêmica...). |

Alguns e-mails cabem em duas etapas (ex.: "recebemos sua candidatura" + "estamos na triagem").
Nesses casos o campo `status` é uma lista com as respostas aceitas.

## Rodar

```powershell
cd backend
python -m evals.run_eval --limit 5   # teste rápido
python -m evals.run_eval             # tudo (cerca de 10 min no plano gratuito do Gemini)
```

Gasta chamadas reais ao Gemini. O resultado detalhado fica em `last_run.json` (ignorado pelo Git).

## Adicionar casos

Uma linha por e-mail em `dataset.jsonl`, com `text` (começa com `Assunto: ...`), `is_job`,
e, quando for processo, `status`, `company` e `title`. Use sempre dados fictícios.
