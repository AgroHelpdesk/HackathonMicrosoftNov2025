/**
 * AgriFlow AI - Design System
 * Sistema de design baseado no conceito "Intelligent Farm Management"
 * Inspirado em interfaces modernas de agricultura inteligente
 */

// ============================================
// 1. CORES (Color Palette)
// ============================================

export const colors = {
  // Cores Primárias - Base Azul/Verde Profissional
  primary: {
    main: '#2C5F6F',        // Azul petróleo principal
    light: '#4A7C8C',       // Azul petróleo claro
    dark: '#1A3F4F',        // Azul petróleo escuro
    contrastText: '#FFFFFF'
  },
  
  // Cores Secundárias - Verde Agricultura
  secondary: {
    main: '#5FA777',        // Verde agricultura
    light: '#7FBF95',       // Verde claro
    dark: '#3F8757',        // Verde escuro
    contrastText: '#FFFFFF'
  },
  
  // Backgrounds
  background: {
    default: '#F5F7FA',     // Cinza muito claro (fundo geral)
    paper: '#FFFFFF',       // Branco puro (cards)
    sidebar: '#3A4B5C',     // Azul escuro (sidebar)
    sidebarHover: '#4A5B6C', // Azul escuro hover
    listHover: '#becadf60' // Hover para listas
  },
  
  // Status Colors - Para workflows e estados
  status: {
    success: '#5FA777',     // Verde - sucesso/completo
    warning: '#F9A825',     // Amarelo/laranja - atenção
    error: '#E57373',       // Vermelho suave - erro
    info: '#64B5F6',        // Azul claro - informação
    pending: '#FFB74D'      // Laranja - pendente
  },
  
  // Agent Workflow Colors (círculos coloridos do workflow)
  agents: {
    fieldSense: '#F9A825',    // Amarelo/laranja
    agroIntel: '#5FA777',     // Verde
    harvestAI: '#64B5F6',     // Azul claro
    decision: '#9575CD',      // Roxo
    alert: '#E57373'          // Vermelho
  },
  
  // Cores de Texto
  text: {
    primary: '#2C3E50',       // Texto principal escuro
    secondary: '#607D8B',     // Texto secundário
    disabled: '#B0BEC5',      // Texto desabilitado
    light: '#FFFFFF',         // Texto claro (sobre fundos escuros)
    muted: '#90A4AE'          // Texto suave
  },
  
  // Borders
  border: {
    light: '#E0E7EB',         // Border claro
    medium: '#B0BEC5',        // Border médio
    dark: '#607D8B'           // Border escuro
  },
  
  // Overlay & Shadows
  overlay: 'rgba(44, 62, 80, 0.5)',
  shadowLight: 'rgba(0, 0, 0, 0.05)',
  shadowMedium: 'rgba(0, 0, 0, 0.1)',
  shadowStrong: 'rgba(0, 0, 0, 0.2)'
}

// ============================================
// 2. TIPOGRAFIA (Typography)
// ============================================

export const typography = {
  fontFamily: {
    primary: '"Inter", "Segoe UI", "Roboto", -apple-system, sans-serif',
    secondary: '"SF Pro Display", "Helvetica Neue", sans-serif',
    mono: '"Fira Code", "Courier New", monospace'
  },
  
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
  },
  
  fontWeight: {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700
  },
  
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
    loose: 2
  },
  
  letterSpacing: {
    tight: '-0.02em',
    normal: '0',
    wide: '0.02em',
    wider: '0.05em'
  }
}

// ============================================
// 3. ESPAÇAMENTO (Spacing)
// ============================================

export const spacing = {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem'      // 96px
}

// ============================================
// 4. BORDAS E RAIOS (Borders & Radius)
// ============================================

export const borderRadius = {
  none: '0',
  sm: '0.25rem',    // 4px
  base: '0.5rem',   // 8px
  md: '0.75rem',    // 12px
  lg: '1rem',       // 16px
  xl: '1.5rem',     // 24px
  '2xl': '2rem',    // 32px
  full: '9999px'    // Circular
}

export const borderWidth = {
  0: '0',
  1: '1px',
  2: '2px',
  4: '4px',
  8: '8px'
}

// ============================================
// 5. SOMBRAS (Shadows)
// ============================================

export const shadows = {
  none: 'none',
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  base: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  md: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  lg: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  xl: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  '2xl': '0 35px 60px -15px rgba(0, 0, 0, 0.3)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  
  // Sombras específicas para componentes
  card: '0 2px 8px rgba(44, 62, 80, 0.08)',
  cardHover: '0 8px 24px rgba(44, 62, 80, 0.12)',
  button: '0 2px 4px rgba(44, 62, 80, 0.1)',
  dropdown: '0 4px 16px rgba(44, 62, 80, 0.15)',
  modal: '0 20px 40px rgba(44, 62, 80, 0.2)'
}

// ============================================
// 6. BREAKPOINTS (Responsive)
// ============================================

export const breakpoints = {
  xs: '0px',      // Mobile
  sm: '600px',    // Tablet
  md: '960px',    // Desktop pequeno
  lg: '1280px',   // Desktop
  xl: '1920px'    // Desktop grande
}

// ============================================
// 7. TRANSIÇÕES (Transitions)
// ============================================

export const transitions = {
  duration: {
    fastest: '100ms',
    fast: '200ms',
    base: '300ms',
    slow: '400ms',
    slowest: '500ms'
  },
  
  timing: {
    linear: 'linear',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'
  },
  
  // Transições prontas
  all: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
  colors: 'color 200ms, background-color 200ms, border-color 200ms',
  transform: 'transform 300ms cubic-bezier(0.4, 0, 0.2, 1)',
  opacity: 'opacity 200ms cubic-bezier(0.4, 0, 0.2, 1)'
}

// ============================================
// 8. Z-INDEX (Camadas)
// ============================================

export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
  notification: 1080,
  max: 9999
}

// ============================================
// 9. COMPONENTES ESPECÍFICOS
// ============================================

export const components = {
  // Sidebar
  sidebar: {
    width: '280px',
    widthCollapsed: '80px',
    background: colors.background.sidebar,
    itemHeight: '48px',
    iconSize: '24px'
  },
  
  // AppBar/Header
  appBar: {
    height: '64px',
    background: '#FFFFFF',
    shadow: shadows.sm
  },
  
  // Cards
  card: {
    padding: spacing[6],
    radius: borderRadius.lg,
    shadow: shadows.card,
    shadowHover: shadows.cardHover
  },
  
  // Buttons
  button: {
    height: {
      sm: '32px',
      md: '40px',
      lg: '48px'
    },
    padding: {
      sm: `${spacing[2]} ${spacing[4]}`,
      md: `${spacing[3]} ${spacing[6]}`,
      lg: `${spacing[4]} ${spacing[8]}`
    },
    radius: borderRadius.base,
    shadow: shadows.button
  },
  
  // Inputs
  input: {
    height: '40px',
    padding: `${spacing[2]} ${spacing[4]}`,
    radius: borderRadius.base,
    borderColor: colors.border.light
  },
  
  // Workflow Circles (Agent Status)
  workflowCircle: {
    size: {
      sm: '48px',
      md: '64px',
      lg: '80px'
    },
    iconSize: {
      sm: '24px',
      md: '32px',
      lg: '40px'
    }
  },
  
  // Activity Log Table
  table: {
    rowHeight: '56px',
    headerHeight: '48px',
    cellPadding: spacing[4]
  }
}

// ============================================
// 10. GRADIENTES
// ============================================

export const gradients = {
  primary: 'linear-gradient(135deg, #2C5F6F 0%, #4A7C8C 100%)',
  secondary: 'linear-gradient(135deg, #5FA777 0%, #7FBF95 100%)',
  success: 'linear-gradient(135deg, #5FA777 0%, #3F8757 100%)',
  card: 'linear-gradient(135deg, #FFFFFF 0%, #F5F7FA 100%)',
  sidebar: 'linear-gradient(180deg, #3A4B5C 0%, #2C3E50 100%)',
  overlay: 'linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.5) 100%)'
}

// ============================================
// 11. ÍCONES E ASSETS
// ============================================

export const icons = {
  size: {
    xs: '16px',
    sm: '20px',
    base: '24px',
    lg: '32px',
    xl: '48px'
  }
}

// ============================================
// EXPORTAÇÃO COMPLETA DO DESIGN SYSTEM
// ============================================

const designSystem = {
  colors,
  typography,
  spacing,
  borderRadius,
  borderWidth,
  shadows,
  breakpoints,
  transitions,
  zIndex,
  components,
  gradients,
  icons
}

export default designSystem
