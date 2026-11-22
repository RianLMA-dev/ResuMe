"""Dados fictícios da demonstração pública. Empresas e pessoa inventadas."""

SAMPLE_CARDS = [
    ("Nimbus Dados", "Engenheiro de IA Júnior", "Inscrito", ["Python", "FastAPI", "LangGraph"], None),
    ("Aurora Sistemas", "Analista de Dados", "Inscrito", ["SQL", "Power BI"], None),
    ("Vértice Labs", "Desenvolvedor Backend", "Em Análise", ["Python", "PostgreSQL", "Docker"], None),
    ("Quasar Tech", "Engenheiro de Dados", "Em Análise", ["SQL", "Airflow", "Python"], None),
    (
        "Lumen Analytics",
        "Cientista de Dados Júnior",
        "Teste Técnico",
        ["Python", "Estatística", "Pandas"],
        "Teste até sexta-feira, 23h59",
    ),
    (
        "Órbita Software",
        "Engenheiro de Machine Learning",
        "Entrevista",
        ["Python", "PyTorch", "MLOps"],
        "Entrevista técnica na terça, 14h",
    ),
    (
        "Cobalto Cloud",
        "Desenvolvedor Full Stack",
        "Oferta",
        ["TypeScript", "Next.js", "PostgreSQL"],
        "Responder à proposta até segunda-feira",
    ),
    ("Pixel Verde", "Desenvolvedor Front-end", "Rejeitado", ["React", "TypeScript"], None),
    ("Andaime Digital", "Analista de Automação", "Inscrito", ["Python", "APIs REST"], None),
]

SAMPLE_RESUME = """ALEX ROCHA (pessoa fictícia)
Estudante de Ciência da Computação | Fortaleza, CE

RESUMO
Estudante de Ciência da Computação com foco em dados e inteligência artificial. Gosto de transformar problemas reais em pequenos produtos que funcionam de ponta a ponta.

PROJETOS
- Assistente de candidaturas: leitura de e-mails de vagas, classificação com modelos de linguagem e quadro kanban em Next.js. API em FastAPI com PostgreSQL e testes automatizados.
- Painel de vendas: coleta de dados públicos, limpeza com Pandas e dashboard interativo.
- Chatbot de FAQ para um grupo de estudos, com busca semântica sobre as anotações das aulas.

EXPERIÊNCIA
Monitor de Programação, Universidade (2025-2026)
- Apoio a 40 alunos em Python e estruturas de dados, com plantões semanais.
- Criei exercícios com correção automática em Python.

FORMAÇÃO
Bacharelado em Ciência da Computação, em andamento (previsão 2028)

HABILIDADES
Python, SQL, Git, Docker, FastAPI, Pandas, noções de TypeScript
Idiomas: português (nativo), inglês intermediário
"""
