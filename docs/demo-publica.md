# Demonstração pública

Uma versão do ResuMe no ar, com dados fictícios, para quem quer ver o projeto sem instalar nada.
Tudo roda em planos gratuitos: a API no Render e o site no Vercel.

## Como a demonstração funciona

- **Cada visitante tem o seu espaço.** O navegador gera um identificador aleatório (guardado no
  `localStorage`) e o envia no cabeçalho `X-Demo-Session`. Na primeira visita, o back-end cria 9
  candidaturas fictícias e um currículo de exemplo para aquele visitante. Ninguém vê os dados de ninguém.
- **Os dados são descartáveis.** Uma sessão vence em 6 horas (`DEMO_SESSION_TTL_HOURS`), e o servidor
  apaga a sessão com os seus dados. Como o plano gratuito apaga o disco quando o servidor dorme, na
  prática tudo some antes disso.
- **Limites para proteger as suas chaves.** Cada análise (e-mail ou currículo) conta em três limites:
  por visitante (12 por hora), por rede (30 por hora) e global (300 por dia). Passou, a API responde 429
  com uma mensagem clara. Os valores mudam pelas variáveis `DEMO_AI_PER_SESSION_HOUR`,
  `DEMO_AI_PER_IP_HOUR` e `DEMO_AI_PER_DAY`. Há também tetos de tamanho (e-mail, vaga, currículo e PDF) e
  de cartões por visitante.
- **Sem Gmail.** As rotas do Gmail respondem 403, e o botão some do site.
- **Erros sem detalhes.** Na demonstração, mensagens de erro de provedores de IA não chegam ao visitante.
- **Aviso de privacidade.** Um aviso no topo do site diz que os dados são fictícios e que o texto é enviado
  a provedores de IA (Gemini e Groq), então ninguém deve colar dados reais.

Fora da demonstração (`DEMO_MODE` desligado), nada disso muda: o app local funciona como sempre.

## Publicar a sua própria demonstração

Você vai precisar de contas gratuitas no [Render](https://render.com) e no [Vercel](https://vercel.com),
além de uma chave do Gemini e uma do Groq **criadas só para isso**, em contas sem cartão de crédito
cadastrado. Assim, o pior caso é a demonstração parar de responder quando a cota do dia acabar.

### 1. API no Render

1. No Render, escolha **New → Blueprint** e conecte o repositório. Ele lê o `render.yaml` da raiz.
2. Quando pedir, cole `GOOGLE_API_KEY` e `GROQ_API_KEY`. Deixe `CORS_ORIGINS` em branco por enquanto.
3. Espere o primeiro build (alguns minutos). Anote o endereço do serviço, algo como
   `https://resume-demo-api.onrender.com`, e confira se `https://<endereço>/health` responde `{"status":"ok"}`.

### 2. Site no Vercel

1. No Vercel, **Add New → Project**, importe o mesmo repositório e defina **Root Directory** como `frontend`.
2. Em **Environment Variables**, crie `NEXT_PUBLIC_API_URL` com o endereço da API do passo anterior
   (sem barra no final). Essa variável é lida na hora do build.
3. Publique e anote o endereço do site, por exemplo `https://resume-demo.vercel.app`.

### 3. Ligar os dois

No Render, abra o serviço, vá em **Environment** e coloque em `CORS_ORIGINS` o endereço do site do Vercel
(sem barra no final). Salve: o serviço reinicia sozinho. Abra o site e teste.

O navegador não chama o Render direto: o site pede tudo para `/backend/...` no próprio endereço do Vercel, e o Vercel
repassa à API (`rewrites` em `frontend/next.config.mjs`). Isso evita que bloqueadores de anúncios barrem a chamada
para `onrender.com`. Por causa desse segundo proxy, o `render.yaml` define `DEMO_TRUSTED_PROXIES=2`, para os limites
por rede enxergarem o IP do visitante e não o do Vercel.

## Limites do plano gratuito

- O servidor do Render **dorme depois de 15 minutos sem acesso** e leva cerca de 1 minuto para acordar.
  O site mostra a tela "Acordando a demonstração..." durante a espera, só no primeiro acesso.
- Há 750 horas gratuitas por mês por conta, o bastante para um serviço ligado o mês inteiro.
- Um monitor externo que acesse `/health` a cada 10 minutos evita o sono, mas mantém o serviço
  consumindo horas. É opcional.
- O Vercel Hobby é para uso pessoal e sem fins comerciais, o caso de um projeto de portfólio.

## Rodar a demonstração na sua máquina

```powershell
cd backend
$env:DEMO_MODE = "true"
$env:DATABASE_URL = "sqlite:///./demo.db"
uvicorn app.main:app --port 8000
```

Em outro terminal, `npm run dev` na pasta `frontend`. Apague o `demo.db` quando quiser recomeçar.
