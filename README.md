# ResuMe

O nome é um trocadilho entre _resume_ (currículo) e _me_ (eu). A ideia é ter um assistente pessoal para cuidar das minhas candidaturas.

Comecei esse projeto porque, quando você se candidata a muitas vagas ao mesmo tempo, perde o controle rápido: em qual etapa cada processo está, quem já respondeu, quem recusou. E ainda tem o trabalho de adaptar o currículo para cada vaga. O ResuMe tenta resolver isso usando agentes de IA e automação.

Também é meu projeto de portfólio na trilha de AI Engineer, então está sendo construído aos poucos e o código é aberto.

## O que já funciona

### 1. Leitura e Análise de E-mails de Candidatura
Você cola o texto de um e-mail de processo seletivo e o ResuMe faz quatro coisas:
1. Troca dados pessoais (e-mail, telefone, CPF e links) por marcadores antes de mandar o texto para o modelo.
2. Decide se o e-mail é mesmo de um processo seletivo. Spam e newsletters são descartados.
3. Extrai empresa, cargo, status, requisitos e próximos passos, em um formato validado com Pydantic.
4. Salva a candidatura no PostgreSQL. Se já existir uma da mesma empresa e cargo, atualiza o status em vez de criar outra.

```mermaid
flowchart LR
    A[E-mail] --> B[Sanitização]
    B --> C{Classifier}
    C -- não é vaga --> D[Descarta]
    C -- é vaga --> E[Extractor]
    E --> F[(PostgreSQL)]
