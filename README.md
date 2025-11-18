# Hackathon Microsoft Nov 2025 - Help Desk para Agricultura

## Descrição

Este projeto é uma **Central Inteligente de Atendimento Agrícola** com Múltiplos Agentes e Automação Segura, desenvolvida para o Hackathon Microsoft. Ele visa resolver chamados repetitivos em agroindústrias, cooperativas e fazendas corporativas através de agentes inteligentes baseados em IA.

### Problema
Grandes agroindústrias, cooperativas e fazendas corporativas possuem centenas de chamados repetitivos diariamente, como:
- “Minha plantadeira está com falha no sensor, e agora?”
- “Preciso de um laudo agronômico urgente.”
- “O estoque de fertilizantes está baixo.”
- “Quero saber qual praga está atacando meu milho.”

### Solução
Uma plataforma que utiliza agentes de IA para automatizar o atendimento, coletar informações e resolver problemas de forma segura e eficiente.

## Agentes da Solução

1. **Intent Agent** – Identificação da Solicitação  
   Analisa mensagem, foto, áudio ou texto e classifica:  
   - Diagnóstico de campo  
   - Equipamento agrícola  
   - Estoque de insumos  
   - Laudos/ART  
   - Conformidade com a Legislação  
   - Clima e irrigação  
   - Financeiro / comercial da cooperativa  
   - Licenças Ambientais  

2. **Info Collector Agent** – Coletor de Informações Faltantes  
   Pede detalhes automaticamente: talhão, cultura, idade da planta, foto da folha/colmo/solo, etc.

3. **Resolver Agent** – Agente Resolvidos  
   Resolve automaticamente consultas simples usando bases de conhecimento e dados históricos.

4. **Escalation Agent** – Agente de Escalação  
   Escala para humanos quando necessário, com contexto completo.

5. **Feedback Agent** – Agente de Feedback  
   Coleta feedback para melhorar o sistema.

## Estrutura do Projeto

- `challenge.txt`: Descrição completa do desafio.
- `dataset/`: Datasets em CSV fornecidos para o projeto.
  - `agrofitprodutostecnicos.csv`
  - `basedeconhecimentoMAPA.csv`
  - `sipeagrofertilizante.csv`
  - `sipeagroqualidadevegetal.csv`
- `web-frontend/`: Aplicação frontend em React (usando Vite) para o painel de controle.
  - Inclui componentes como Dashboard, Chat, MapView, etc.
- `backend/`: (A ser implementado) Backend em Python utilizando Azure Services (Blob Storage, Functions, etc.).

## Instalação e Configuração

### Pré-requisitos
- Node.js (para o frontend)
- Python (para o backend)
- Conta Azure (para serviços na nuvem)

### Frontend
1. Navegue para a pasta `web-frontend/`:
   ```
   cd web-frontend
   ```
2. Instale as dependências:
   ```
   npm install
   ```
3. Execute o servidor de desenvolvimento:
   ```
   npm run dev
   ```
4. Acesse `http://localhost:5173` no navegador.

### Backend
O backend ainda não está implementado. Planeja-se usar:
- Azure Blob Storage para armazenar os datasets.
- Azure Functions para APIs em Python.
- Pandas para processamento de dados.

Para implementar:
1. Crie uma Azure Function App.
2. Configure Blob Storage e faça upload dos CSVs.
3. Implemente funções para consumir os dados via API.

## Uso

1. No frontend, visualize tickets ativos no Dashboard.
2. Selecione um ticket para ver detalhes e histórico de agentes.
3. Use o chat para interagir com clientes.
4. Resolva ou escale tickets conforme necessário.

## Tecnologias Utilizadas

- **Frontend**: React, Material-UI, Vite
- **Backend**: Python, Azure Functions, Azure Blob Storage
- **Dados**: Pandas, CSV
- **IA**: Agentes baseados em modelos de IA (a implementar)

## Contribuição

1. Fork o repositório.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`).
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`).
4. Push para a branch (`git push origin feature/nova-feature`).
5. Abra um Pull Request.

## Licença

Este projeto é para fins educacionais no Hackathon Microsoft. Consulte os termos do hackathon para uso.

## Contato

Para dúvidas, entre em contato com a equipe do projeto.