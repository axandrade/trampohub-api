from celery import shared_task


@shared_task
def notificar_nova_candidatura(vaga_titulo, candidato_id):
    """
    Task assíncrona disparada quando um candidato se candidata a uma vaga.
    Por enquanto, só loga a notificação (no futuro, pode virar e-mail/push).
    """
    print(f"[NOTIFICAÇÃO] Nova candidatura recebida para a vaga '{vaga_titulo}' "
          f"do candidato ID {candidato_id}")
    return f"Notificação enviada para vaga: {vaga_titulo}"