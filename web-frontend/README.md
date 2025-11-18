# Agro Auto-Resolve Frontend (Demo Modernizado)

Este é um frontend React moderno (Vite + Material-UI) com dados mock para o desafio "Auto-resolve Service Desk para Agroindústria e Agricultura".

## 🚀 Funcionalidades
- **Dashboard Principal**: Lista de chamados com agentes, runbooks e detalhes interativos.
- **Simulação de Chat**: Conversas mockadas como nos exemplos do desafio (WhatsApp/Teams).
- **Dashboard de Métricas**: KPIs como redução de chamados, tempo de resposta, acurácia, ranking de sintomas.
- **Mapa de Talhões**: Mapa interativo com Leaflet mostrando talhões com marcadores e popups (alertas ativos).
- **Transparência Total**: Logs de passos de cada agente em cada chamado.
- **Navegação**: React Router para múltiplas páginas.

## 🧠 Agentes Demonstrados
- **FieldSense** (Intent): Classifica solicitações.
- **FarmOps** (Info Collector): Coleta dados faltantes.
- **AgroBrain** (Knowledge): Busca em bases de conhecimento.
- **RunbookMaster** (Decision): Decide automação ou escalamento.
- **ExplainIt** (Transparency): Explica cada passo.

## ⚙️ Runbooks Mock
- RB-01: Gerar relatório de praga (Seguro).
- RB-02: Abertura de OS urgente (Crítico).
- RB-03: Consulta de estoque (Seguro).
- RB-04: Pré-preenchimento de ART (Crítico).

## 📊 Métricas Mock
- Redução de chamados: 65%
- Tempo médio resolução: 12 min
- Acurácia classificação: 92%
- Escalados: 8%

## 🗺️ Mapa de Talhões
- Integrado com Leaflet (OpenStreetMap tiles).
- Marcadores para cada talhão com popup mostrando ID, cultura e status.
- Alertas visuais: Normal (verde), Praga/Manutenção (amarelo/vermelho).
- Pronto para integração com GPS real ou APIs de clima.

## 💻 Como rodar (PowerShell — Windows)
1. Entrar na pasta: `cd e:\projects\HackathonMicrosoftNov2025\web-frontend`
2. Instalar: `npm install`
3. Desenvolver: `npm run dev` (abre em http://localhost:5173)
4. Build: `npm run build && npm run preview`

## 🎨 Design
- Tema Material-UI verde-agrícola.
- Layout responsivo com Drawer lateral.
- Cards, Chips, Progress Bars para visualização rica.

## 🔧 Próximos Passos Sugeridos
- Integrar APIs reais (telemetria, ERP, clima).
- Adicionar autenticação (roles: operador, agrônomo, admin).
- Upload de imagens reais para diagnóstico.
- Notificações push para alertas.
- Integração com WhatsApp API para chats reais.
- Persistência com backend (Node.js/Express ou Azure Functions).
- Melhorar mapa: clusters, heatmaps para pragas, integração com sensores IoT.

## 📁 Estrutura
- `src/App.jsx`: Rotas e tema.
- `src/components/`: Dashboard, Chat, Metrics, MapView, TicketCard.
- `src/mockData.js`: Dados mock (tickets, agentes, métricas, talhões).
- `public/images/`: Placeholders de imagens.

---

Powered by React + Vite + Material-UI. Demo completo para o desafio Hackathon Microsoft Nov 2025.

