"""Mede o classificador e o extrator em evals/dataset.jsonl (e-mails sintéticos).

Uso (dentro de backend/):
    python -m evals.run_eval                 # tudo
    python -m evals.run_eval --limit 10      # só os 10 primeiros
    python -m evals.run_eval --sleep 15      # pausa entre e-mails (limite por minuto do Gemini)
    python -m evals.run_eval --ids s29,s30   # só estes casos

Gasta chamadas reais ao Gemini. Casos 'ambiguous' são reportados à parte, fora da nota.
"""
import argparse
import json
import time
from pathlib import Path

from app.agents.classifier import classify_email
from app.agents.extractor import extract_application
from app.schemas import EmailInput
from evals.metrics import classifier_scores, extraction_scores, pct

DATASET = Path(__file__).parent / "dataset.jsonl"
LAST_RUN = Path(__file__).parent / "last_run.json"


def load_cases() -> list[dict]:
    return [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sleep", type=float, default=12.0)
    parser.add_argument("--ids", default=None, help="só estes casos, separados por vírgula (ex.: s29,s30)")
    args = parser.parse_args()

    cases = load_cases()
    if args.ids:
        wanted = {i.strip() for i in args.ids.split(",")}
        cases = [c for c in cases if c["id"] in wanted]
    cases = cases[: args.limit]
    class_pairs, class_errors, ambiguous, extraction_rows, details = [], [], [], [], []

    for index, case in enumerate(cases, start=1):
        email = EmailInput(raw_text=case["text"])
        classification = classify_email(email)
        predicted_job = classification.is_job_related
        record = {"id": case["id"], "predicted_job": predicted_job, "reason": classification.reason}

        if case.get("ambiguous"):
            ambiguous.append((case, predicted_job))
        else:
            class_pairs.append((case["is_job"], predicted_job))
            if case["is_job"] != predicted_job:
                class_errors.append((case, predicted_job, classification.reason))

        if predicted_job and case.get("is_job") and not case.get("verify"):
            application = extract_application(email)
            predicted = {
                "status": application.status.value,
                "company": application.company_name,
                "title": application.job_title,
            }
            expected = {k: case.get(k) for k in ("status", "company", "title")}
            extraction_rows.append({"expected": expected, "predicted": predicted})
            record["predicted"] = predicted
            record["expected"] = expected

        details.append(record)
        print(f"[{index}/{len(cases)}] {case['id']} -> {'vaga' if predicted_job else 'descartado'}")
        time.sleep(args.sleep)

    scores = classifier_scores(class_pairs)
    print("\n=== Classificador (vaga ou não) ===")
    print(f"Acerto: {pct(scores['accuracy'])}  Precisão: {pct(scores['precision'])}  Recall: {pct(scores['recall'])}")
    print(f"Verdadeiros+: {scores['tp']}  Falsos+: {scores['fp']}  Falsos-: {scores['fn']}  Verdadeiros-: {scores['tn']}")

    if extraction_rows:
        ext = extraction_scores(extraction_rows)
        print("\n=== Extrator (só e-mails conferidos) ===")
        for field, label in (("status", "Status"), ("company", "Empresa"), ("title", "Cargo")):
            r = ext[field]
            print(f"{label}: {pct(r['accuracy'])} ({r['hits']}/{r['total']})")
    else:
        print("\nNenhum e-mail de vaga nesta seleção, então o extrator não entrou na nota.")

    if ambiguous:
        print("\n=== Ambíguos (fora da nota) ===")
        for case, predicted in ambiguous:
            print(f"{case['id']}: previsto {'vaga' if predicted else 'descartado'} - {case.get('why')}")

    if class_errors:
        print("\n=== Erros do classificador ===")
        for case, predicted, reason in class_errors:
            print(f"{case['id']}: esperado {'vaga' if case['is_job'] else 'não-vaga'}, previu {'vaga' if predicted else 'não-vaga'}. Motivo do modelo: {reason}")

    LAST_RUN.write_text(json.dumps(details, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
