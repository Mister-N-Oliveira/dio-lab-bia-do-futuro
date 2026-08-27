# Assets

Esta pasta é destinada a recursos visuais do seu projeto:

- Diagramas de arquitetura

Funiconamento:
 ```mermaid
flowchart TD
    A([Usuário envia mensagem no Chat]) --> B[Interface Streamlit src/app.py]
    B --> C{Classificador de Intenção e Escopo}
    C -- Fora de Escopo --> D[Recusa Educada de Escopo]
    C -- Pergunta Pessoal --> E[Leitor de Dados Locais /data]
    C -- Explicação de Produto --> F[Motor de Busca Web ao Vivo DDGS e Google]
    C -- Recomendação de Produto --> G[Filtro do Catálogo Oficial produtos_financeiros.json]
    E --> H[Geração de Resposta Grounded com Métricas]
    F --> H
    G --> H
    D --> H
    H --> I[Exibição Cronológica na Interface]
    I --> J[st.chat_input fixado no Final da Tela]
```

Como os dados são carregados:
```mermaid
flowchart LR
    A["📁 Arquivos Locais\n(/data/*.json, *.csv)"] --> B["⚡ Leitor FinanceEngine\n(Pandas / JSON)"]
    W["🌐 Busca na Web (DDGS / Google)"] --> B
    B --> C["🧩 Classificação de Intenção\n(Gastos, Produtos, Escopo, Web)"]
    C --> D["💬 Injeção no Prompt do LLM\nou Resposta Determinística"]
```
  
- Screenshots da aplicação
<img width="1665" height="900" alt="image" src="https://github.com/user-attachments/assets/8a0f09d9-338c-48b8-820d-bc76aa15137c" />

  
- Mockups de interface
<img width="1591" height="889" alt="image" src="https://github.com/user-attachments/assets/c756f921-b4c3-4455-9ba0-35461b618ab2" />

<img width="1591" height="889" alt="image" src="https://github.com/user-attachments/assets/96c17c2e-b620-485e-8514-a5635ac753ba" />

<img width="1612" height="867" alt="image" src="https://github.com/user-attachments/assets/31bbd8bb-65a5-4fd1-9aff-5b50df6f4c3f" />

<img width="1647" height="981" alt="image" src="https://github.com/user-attachments/assets/17f2180f-c5db-4885-a121-f1b0e7901c29" />



- Imagens para o README
