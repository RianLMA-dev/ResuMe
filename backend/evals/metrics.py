"""Contas da avaliação. Funções puras: não chamam IA nem rede, então são testáveis."""
import re
import unicodedata


def _norm(text: str | None) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def names_match(expected: str | list[str] | None, predicted: str | None) -> bool:
    """Compara empresa/cargo sem exigir texto idêntico: 'Radix' casa com 'Radix Engenharia'.
    Se `expected` for uma lista (ex.: cargo em português e em inglês), basta casar com uma."""
    if isinstance(expected, list):
        return any(names_match(option, predicted) for option in expected)
    e, p = _norm(expected), _norm(predicted)
    return bool(e) and bool(p) and (e in p or p in e)


def _ratio(hits: int, total: int) -> float | None:
    return hits / total if total else None


def classifier_scores(pairs: list[tuple[bool, bool]]) -> dict:
    """pairs = [(esperado, previsto), ...] onde True significa 'é processo seletivo'."""
    tp = sum(1 for e, p in pairs if e and p)
    fp = sum(1 for e, p in pairs if not e and p)
    fn = sum(1 for e, p in pairs if e and not p)
    tn = sum(1 for e, p in pairs if not e and not p)
    return {
        "total": len(pairs),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "accuracy": _ratio(tp + tn, len(pairs)),
        "precision": _ratio(tp, tp + fp),
        "recall": _ratio(tp, tp + fn),
    }


def extraction_scores(rows: list[dict]) -> dict:
    """rows = [{'expected': {...}, 'predicted': {...}}]. Só conta o campo que tem resposta esperada."""
    def status_match(expected, predicted):
        # Aceita lista quando o e-mail cabe em mais de uma etapa (ex.: "recebemos" + "em triagem").
        return predicted in expected if isinstance(expected, list) else expected == predicted

    fields = {"status": status_match, "company": names_match, "title": names_match}
    result = {}
    for field, same in fields.items():
        scored = [r for r in rows if r["expected"].get(field)]
        hits = sum(1 for r in scored if same(r["expected"][field], r["predicted"].get(field)))
        result[field] = {"hits": hits, "total": len(scored), "accuracy": _ratio(hits, len(scored))}
    return result


def pct(value: float | None) -> str:
    return "n/d" if value is None else f"{value * 100:.0f}%"
