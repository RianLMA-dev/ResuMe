from app.services.gmail import GmailAuthError
from app.services.gmail_sync import GmailSyncResult
from app.services.scheduled_sync import (
    EXIT_AUTH,
    EXIT_ERROR,
    EXIT_OK,
    PAUSE_BETWEEN_BATCHES,
    RATE_LIMIT_WAIT,
    run_scheduled_sync,
)


def result(checked=1, saved=1, discarded=0, remaining=0, stopped=False):
    return GmailSyncResult(
        checked=checked,
        saved=saved,
        discarded=discarded,
        remaining=remaining,
        stopped_by_error=stopped,
    )


def make_sync(items):
    queue = iter(items)

    def sync(db):
        item = next(queue)
        if isinstance(item, Exception):
            raise item
        return item

    return sync


def test_processa_ate_a_fila_acabar():
    sleeps = []
    code = run_scheduled_sync(
        None, sync=make_sync([result(remaining=1), result(remaining=0)]), sleep=sleeps.append
    )
    assert code == EXIT_OK
    assert sleeps == [PAUSE_BETWEEN_BATCHES]


def test_sem_emails_novos_termina_sem_esperar():
    sleeps = []
    code = run_scheduled_sync(
        None, sync=make_sync([result(checked=0, saved=0)]), sleep=sleeps.append
    )
    assert code == EXIT_OK
    assert sleeps == []


def test_espera_e_tenta_de_novo_quando_a_ia_falha():
    sleeps = []
    failing = result(checked=0, saved=0, remaining=1, stopped=True)
    code = run_scheduled_sync(
        None, sync=make_sync([failing, result(remaining=0)]), sleep=sleeps.append
    )
    assert code == EXIT_OK
    assert sleeps == [RATE_LIMIT_WAIT]


def test_desiste_depois_de_varias_falhas_seguidas():
    failing = result(checked=0, saved=0, remaining=1, stopped=True)
    code = run_scheduled_sync(None, sync=make_sync([failing] * 5), sleep=lambda seconds: None)
    assert code == EXIT_ERROR


def test_autorizacao_expirada_retorna_codigo_proprio():
    code = run_scheduled_sync(
        None, sync=make_sync([GmailAuthError("expirou")]), sleep=lambda seconds: None
    )
    assert code == EXIT_AUTH


def test_respeita_o_teto_por_execucao():
    sleeps = []
    always_more = [result(remaining=50)] * 100
    code = run_scheduled_sync(None, sync=make_sync(always_more), sleep=sleeps.append)
    assert code == EXIT_OK
    assert len(sleeps) == 20  # 20 e-mails, 1 por lote