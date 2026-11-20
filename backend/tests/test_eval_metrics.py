from evals.metrics import classifier_scores, extraction_scores, names_match, pct


def test_names_match_tolera_variacao():
    assert names_match("Radix", "Radix Engenharia & Software")
    assert names_match("Estágio em Dados", "estagio em dados")
    assert not names_match("Radix", "Stefanini")
    assert not names_match(None, "Radix")
    assert not names_match("Radix", "")


def test_classifier_scores():
    pairs = [(True, True), (True, False), (False, False), (False, True), (False, False)]
    scores = classifier_scores(pairs)
    assert (scores["tp"], scores["fn"], scores["tn"], scores["fp"]) == (1, 1, 2, 1)
    assert scores["accuracy"] == 3 / 5
    assert scores["precision"] == 1 / 2
    assert scores["recall"] == 1 / 2


def test_classifier_scores_sem_dados_nao_divide_por_zero():
    scores = classifier_scores([])
    assert scores["accuracy"] is None and scores["precision"] is None


def test_extraction_scores_ignora_campo_sem_esperado():
    rows = [
        {"expected": {"status": "Inscrito", "company": "Radix", "title": None},
         "predicted": {"status": "Inscrito", "company": "Radix Engenharia", "title": "Qualquer"}},
        {"expected": {"status": "Rejeitado", "company": "iFood", "title": "Estágio"},
         "predicted": {"status": "Inscrito", "company": "iFood", "title": "Programa de Estágio"}},
    ]
    result = extraction_scores(rows)
    assert result["status"] == {"hits": 1, "total": 2, "accuracy": 0.5}
    assert result["company"]["accuracy"] == 1.0
    assert result["title"]["total"] == 1 and result["title"]["hits"] == 1


def test_pct():
    assert pct(None) == "n/d"
    assert pct(0.934) == "93%"


def test_names_match_aceita_lista_de_respostas():
    expected = ["Engenheiro de Machine Learning Júnior", "Machine Learning Engineer Jr."]
    assert names_match(expected, "Machine Learning Engineer Jr.")
    assert names_match(expected, "Engenheiro de Machine Learning Júnior")
    assert not names_match(expected, "Analista de Dados")
