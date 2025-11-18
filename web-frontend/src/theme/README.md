# AgriFlow AI - Design System 🎨

Sistema de design completo para a aplicação AgriFlow AI, baseado no conceito "Intelligent Farm Management" com interface moderna e profissional.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura de Arquivos](#estrutura-de-arquivos)
3. [Paleta de Cores](#paleta-de-cores)
4. [Tipografia](#tipografia)
5. [Componentes](#componentes)
6. [Uso](#uso)
7. [Exemplos](#exemplos)

---

## 🎯 Visão Geral

O Design System AgriFlow AI foi criado para proporcionar:

- ✅ **Consistência visual** em toda a aplicação
- ✅ **Reutilização de componentes** e estilos
- ✅ **Manutenibilidade** facilitada do código
- ✅ **Performance otimizada** com CSS-in-JS
- ✅ **Responsividade** nativa em todos os dispositivos
- ✅ **Acessibilidade** seguindo padrões WCAG

---

## 📁 Estrutura de Arquivos

```
src/theme/
├── designSystem.js    # Sistema de design completo (tokens)
├── theme.js          # Tema Material-UI configurado
├── styles.js         # Utilitários CSS reutilizáveis
└── README.md         # Documentação (este arquivo)
```

### Arquivos Principais

#### `designSystem.js`
Contém todos os **tokens de design**:
- Cores primárias, secundárias e de status
- Tipografia (fontes, tamanhos, pesos)
- Espaçamento e layout
- Bordas e raios
- Sombras
- Transições
- Breakpoints responsivos
- Z-index
- Configurações de componentes

#### `theme.js`
Configuração do **tema Material-UI** aplicando os tokens do Design System.

#### `styles.js`
**Utilitários CSS** prontos para uso direto nos componentes usando CSS-in-JS.

---

## 🎨 Paleta de Cores

### Cores Primárias
```javascript
primary: {
  main: '#2C5F6F',        // Azul petróleo principal
  light: '#4A7C8C',       // Azul petróleo claro
  dark: '#1A3F4F',        // Azul petróleo escuro
  contrastText: '#FFFFFF'
}
```

**Uso**: Elementos principais da interface, botões primários, links importantes.

### Cores Secundárias
```javascript
secondary: {
  main: '#5FA777',        // Verde agricultura
  light: '#7FBF95',       // Verde claro
  dark: '#3F8757',        // Verde escuro
  contrastText: '#FFFFFF'
}
```

**Uso**: Ações secundárias, ênfase em elementos relacionados à agricultura.

### Cores de Status
```javascript
status: {
  success: '#5FA777',     // Verde - sucesso/completo
  warning: '#F9A825',     // Amarelo/laranja - atenção
  error: '#E57373',       // Vermelho suave - erro
  info: '#64B5F6',        // Azul claro - informação
  pending: '#FFB74D'      // Laranja - pendente
}
```

### Cores dos Agents (Workflow)
```javascript
agents: {
  fieldSense: '#F9A825',    // Amarelo/laranja
  agroIntel: '#5FA777',     // Verde
  harvestAI: '#64B5F6',     // Azul claro
  decision: '#9575CD',      // Roxo
  alert: '#E57373'          // Vermelho
}
```

### Backgrounds
```javascript
background: {
  default: '#F5F7FA',     // Cinza muito claro (fundo geral)
  paper: '#FFFFFF',       // Branco puro (cards)
  sidebar: '#3A4B5C',     // Azul escuro (sidebar)
  sidebarHover: '#4A5B6C' // Azul escuro hover
}
```

### Texto
```javascript
text: {
  primary: '#2C3E50',       // Texto principal escuro
  secondary: '#607D8B',     // Texto secundário
  disabled: '#B0BEC5',      // Texto desabilitado
  light: '#FFFFFF',         // Texto claro (sobre fundos escuros)
  muted: '#90A4AE'          // Texto suave
}
```

---

## ✍️ Tipografia

### Fontes
```javascript
fontFamily: {
  primary: '"Inter", "Segoe UI", "Roboto", -apple-system, sans-serif',
  secondary: '"SF Pro Display", "Helvetica Neue", sans-serif',
  mono: '"Fira Code", "Courier New", monospace'
}
```

### Tamanhos
```javascript
fontSize: {
  xs: '0.75rem',      // 12px
  sm: '0.875rem',     // 14px
  base: '1rem',       // 16px
  lg: '1.125rem',     // 18px
  xl: '1.25rem',      // 20px
  '2xl': '1.5rem',    // 24px
  '3xl': '1.875rem',  // 30px
  '4xl': '2.25rem',   // 36px
  '5xl': '3rem'       // 48px
}
```

### Pesos
```javascript
fontWeight: {
  light: 300,
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700
}
```

---

## 🧩 Componentes

### Workflow Circle (Agent Status)

Círculos coloridos representando status dos agentes:

```jsx
import { workflowCircle, workflowCircleActive } from './theme/styles'
import { colors } from './theme/designSystem'

// Círculo normal
<div css={workflowCircle(colors.agents.fieldSense, 'md')}>
  <Icon />
</div>

// Círculo ativo
<div css={workflowCircleActive(colors.agents.agroIntel, 'lg')}>
  <Icon />
</div>
```

**Tamanhos disponíveis**: `sm`, `md`, `lg`

### Cards

```jsx
import { cardBase, cardGradient } from './theme/styles'

// Card básico
<div css={cardBase}>
  {/* conteúdo */}
</div>

// Card com gradiente
<div css={cardGradient}>
  {/* conteúdo */}
</div>
```

### Buttons

```jsx
import { buttonPrimary, buttonSecondary, buttonOutline } from './theme/styles'

// Botão primário
<button css={buttonPrimary}>Primary Button</button>

// Botão secundário
<button css={buttonSecondary}>Secondary Button</button>

// Botão outline
<button css={buttonOutline}>Outline Button</button>
```

### Badges de Status

```jsx
import { statusBadge } from './theme/styles'

<span css={statusBadge('success')}>Success</span>
<span css={statusBadge('warning')}>Warning</span>
<span css={statusBadge('error')}>Error</span>
<span css={statusBadge('info')}>Info</span>
<span css={statusBadge('pending')}>Pending</span>
```

### Sidebar Items

```jsx
import { sidebarItem } from './theme/styles'

<a href="/dashboard" css={sidebarItem} className="active">
  <DashboardIcon />
  Dashboard
</a>
```

### Tables

```jsx
import { tableContainer, tableHeader, tableRow } from './theme/styles'

<div css={tableContainer}>
  <table>
    <thead css={tableHeader}>
      <tr>
        <th>Column 1</th>
        <th>Column 2</th>
      </tr>
    </thead>
    <tbody>
      <tr css={tableRow}>
        <td>Data 1</td>
        <td>Data 2</td>
      </tr>
    </tbody>
  </table>
</div>
```

---

## 💻 Uso

### 1. Importar o Tema Material-UI

No seu componente raiz (`App.jsx`):

```jsx
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import theme from './theme/theme'

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {/* Seu app aqui */}
    </ThemeProvider>
  )
}
```

### 2. Usar Tokens do Design System

```jsx
import designSystem from './theme/designSystem'

const { colors, spacing, borderRadius, shadows } = designSystem

const MyComponent = () => (
  <div style={{
    backgroundColor: colors.background.paper,
    padding: spacing[6],
    borderRadius: borderRadius.lg,
    boxShadow: shadows.card
  }}>
    Conteúdo
  </div>
)
```

### 3. Usar Utilitários CSS

```jsx
/** @jsxImportSource @emotion/react */
import { flexCenter, cardBase } from './theme/styles'

const MyComponent = () => (
  <div css={[flexCenter, cardBase]}>
    <h1>Centered Content in Card</h1>
  </div>
)
```

### 4. Usar Componentes Material-UI

Os componentes Material-UI já vêm estilizados automaticamente:

```jsx
import { Button, Card, CardContent, Typography } from '@mui/material'

const MyComponent = () => (
  <Card>
    <CardContent>
      <Typography variant="h5">Título</Typography>
      <Typography variant="body2">Descrição</Typography>
      <Button variant="contained" color="primary">
        Ação
      </Button>
    </CardContent>
  </Card>
)
```

---

## 📱 Responsividade

### Breakpoints

```javascript
breakpoints: {
  xs: '0px',      // Mobile
  sm: '600px',    // Tablet
  md: '960px',    // Desktop pequeno
  lg: '1280px',   // Desktop
  xl: '1920px'    // Desktop grande
}
```

### Uso com Material-UI

```jsx
import { Box } from '@mui/material'

<Box
  sx={{
    padding: { xs: 2, sm: 3, md: 4 },
    fontSize: { xs: '0.875rem', md: '1rem' }
  }}
>
  Conteúdo Responsivo
</Box>
```

---

## 🎭 Animações

### Loading Spinner

```jsx
import { spinner } from './theme/styles'

<div css={spinner} />
```

### Pulse Effect

```jsx
import { pulse } from './theme/styles'

<div css={pulse}>
  Elemento pulsante
</div>
```

### Fade In

```jsx
import { fadeIn } from './theme/styles'

<div css={fadeIn}>
  Elemento com fade in
</div>
```

---

## 🔧 Customização

### Adicionar Nova Cor

Edite `src/theme/designSystem.js`:

```javascript
export const colors = {
  // ... cores existentes
  
  custom: {
    brand: '#YOUR_COLOR',
    accent: '#YOUR_ACCENT_COLOR'
  }
}
```

### Criar Novo Utilitário

Edite `src/theme/styles.js`:

```javascript
export const myCustomStyle = css`
  /* Seus estilos aqui */
  background: ${colors.primary.main};
  padding: ${spacing[4]};
`
```

---

## 📚 Referências

- [Material-UI Documentation](https://mui.com/)
- [Emotion CSS-in-JS](https://emotion.sh/)
- [Design Tokens](https://www.designtokens.org/)

---

## 🤝 Contribuindo

Para adicionar novos componentes ou melhorias ao Design System:

1. Adicione os tokens necessários em `designSystem.js`
2. Configure o tema Material-UI em `theme.js` se aplicável
3. Crie utilitários reutilizáveis em `styles.js`
4. Documente o uso neste README

---

## 📄 Licença

Este Design System foi criado especificamente para o projeto AgriFlow AI.

---

**Desenvolvido com 💚 para AgriFlow AI - Intelligent Farm Management**
