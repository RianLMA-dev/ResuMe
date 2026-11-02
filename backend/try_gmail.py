from app.services.gmail import authorize, get_message, get_service, list_message_ids

authorize()  # na primeira vez, abre o navegador
service = get_service()

ids = list_message_ids(service, "Vagas", max_results=5)
print(f"{len(ids)} e-mail(s) com o rótulo 'Vagas':")
for message_id in ids:
    message = get_message(service, message_id)
    print(f"- {message['subject'][:80]} ({len(message['text'])} caracteres)")