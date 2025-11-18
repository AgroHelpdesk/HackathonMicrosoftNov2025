import { createTheme } from '@mui/material/styles'
import designSystem from './designSystem'

/**
 * AgriFlow AI - Material-UI Theme
 * Tema Material-UI baseado no Design System AgriFlow
 */

const { colors, typography, spacing, borderRadius, shadows, transitions, breakpoints } = designSystem

const theme = createTheme({
  // ============================================
  // PALETTE (Cores)
  // ============================================
  palette: {
    mode: 'light',
    primary: {
      main: colors.primary.main,
      light: colors.primary.light,
      dark: colors.primary.dark,
      contrastText: colors.primary.contrastText
    },
    secondary: {
      main: colors.secondary.main,
      light: colors.secondary.light,
      dark: colors.secondary.dark,
      contrastText: colors.secondary.contrastText
    },
    success: {
      main: colors.status.success,
      light: '#7FBF95',
      dark: '#3F8757'
    },
    warning: {
      main: colors.status.warning,
      light: '#FFB74D',
      dark: '#F57C00'
    },
    error: {
      main: colors.status.error,
      light: '#EF9A9A',
      dark: '#D32F2F'
    },
    info: {
      main: colors.status.info,
      light: '#90CAF9',
      dark: '#1976D2'
    },
    background: {
      default: colors.background.default,
      paper: colors.background.paper
    },
    text: {
      primary: colors.text.primary,
      secondary: colors.text.secondary,
      disabled: colors.text.disabled
    },
    divider: colors.border.light,
    
    // Cores customizadas adicionais
    sidebar: {
      main: colors.background.sidebar,
      hover: colors.background.sidebarHover
    },
    agents: colors.agents
  },

  // ============================================
  // TYPOGRAPHY (Tipografia)
  // ============================================
  typography: {
    fontFamily: typography.fontFamily.primary,
    
    h1: {
      fontFamily: typography.fontFamily.secondary,
      fontSize: typography.fontSize['4xl'],
      fontWeight: typography.fontWeight.bold,
      lineHeight: typography.lineHeight.tight,
      color: colors.text.primary
    },
    h2: {
      fontFamily: typography.fontFamily.secondary,
      fontSize: typography.fontSize['3xl'],
      fontWeight: typography.fontWeight.bold,
      lineHeight: typography.lineHeight.tight,
      color: colors.text.primary
    },
    h3: {
      fontFamily: typography.fontFamily.secondary,
      fontSize: typography.fontSize['2xl'],
      fontWeight: typography.fontWeight.semibold,
      lineHeight: typography.lineHeight.normal,
      color: colors.text.primary
    },
    h4: {
      fontSize: typography.fontSize.xl,
      fontWeight: typography.fontWeight.semibold,
      lineHeight: typography.lineHeight.normal,
      color: colors.text.primary
    },
    h5: {
      fontSize: typography.fontSize.lg,
      fontWeight: typography.fontWeight.medium,
      lineHeight: typography.lineHeight.normal,
      color: colors.text.primary
    },
    h6: {
      fontSize: typography.fontSize.base,
      fontWeight: typography.fontWeight.medium,
      lineHeight: typography.lineHeight.normal,
      color: colors.text.primary
    },
    subtitle1: {
      fontSize: typography.fontSize.lg,
      fontWeight: typography.fontWeight.regular,
      lineHeight: typography.lineHeight.normal,
      color: colors.text.secondary
    },
    subtitle2: {
      fontSize: typography.fontSize.sm,
      fontWeight: typography.fontWeight.medium,
      lineHeight: typography.lineHeight.normal,
      color: colors.text.secondary
    },
    body1: {
      fontSize: typography.fontSize.base,
      fontWeight: typography.fontWeight.regular,
      lineHeight: typography.lineHeight.relaxed,
      color: colors.text.primary
    },
    body2: {
      fontSize: typography.fontSize.sm,
      fontWeight: typography.fontWeight.regular,
      lineHeight: typography.lineHeight.normal,
      color: colors.text.secondary
    },
    button: {
      fontSize: typography.fontSize.sm,
      fontWeight: typography.fontWeight.medium,
      textTransform: 'none',
      letterSpacing: typography.letterSpacing.wide
    },
    caption: {
      fontSize: typography.fontSize.xs,
      fontWeight: typography.fontWeight.regular,
      lineHeight: typography.lineHeight.normal,
      color: colors.text.muted
    },
    overline: {
      fontSize: typography.fontSize.xs,
      fontWeight: typography.fontWeight.semibold,
      textTransform: 'uppercase',
      letterSpacing: typography.letterSpacing.wider,
      color: colors.text.secondary
    }
  },

  // ============================================
  // BREAKPOINTS (Responsivo)
  // ============================================
  breakpoints: {
    values: {
      xs: parseInt(breakpoints.xs),
      sm: parseInt(breakpoints.sm),
      md: parseInt(breakpoints.md),
      lg: parseInt(breakpoints.lg),
      xl: parseInt(breakpoints.xl)
    }
  },

  // ============================================
  // SPACING (Espaçamento)
  // ============================================
  spacing: 8, // Base: 8px (1 = 8px, 2 = 16px, etc.)

  // ============================================
  // SHAPE (Formas)
  // ============================================
  shape: {
    borderRadius: parseInt(borderRadius.base)
  },

  // ============================================
  // SHADOWS (Sombras)
  // ============================================
  shadows: [
    'none',
    shadows.xs,
    shadows.sm,
    shadows.base,
    shadows.base,
    shadows.md,
    shadows.md,
    shadows.md,
    shadows.lg,
    shadows.lg,
    shadows.lg,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows['2xl'],
    shadows['2xl'],
    shadows['2xl'],
    shadows['2xl'],
    shadows['2xl'],
    shadows['2xl'],
    shadows['2xl'],
    shadows['2xl'],
    shadows['2xl'],
    shadows['2xl'],
    shadows['2xl']
  ],

  // ============================================
  // COMPONENTS (Customização de Componentes)
  // ============================================
  components: {
    // AppBar
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: colors.background.paper,
          color: colors.text.primary,
          boxShadow: shadows.sm,
          borderBottom: `1px solid ${colors.border.light}`
        }
      }
    },

    // Drawer (Sidebar)
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: colors.background.sidebar,
          color: colors.text.light,
          borderRight: 'none',
          backgroundImage: designSystem.gradients.sidebar
        }
      }
    },

    // Card
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.lg,
          boxShadow: shadows.card,
          border: `1px solid ${colors.border.light}`,
          transition: transitions.all,
          '&:hover': {
            boxShadow: shadows.cardHover,
            transform: 'translateY(-2px)'
          }
        }
      }
    },

    // Button
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.base,
          textTransform: 'none',
          fontWeight: typography.fontWeight.medium,
          fontSize: typography.fontSize.sm,
          padding: `${spacing[2]} ${spacing[6]}`,
          boxShadow: 'none',
          transition: transitions.all,
          '&:hover': {
            boxShadow: shadows.button,
            transform: 'translateY(-1px)'
          }
        },
        contained: {
          '&:hover': {
            boxShadow: shadows.button
          }
        },
        containedPrimary: {
          background: designSystem.gradients.primary,
          '&:hover': {
            background: designSystem.gradients.primary,
            filter: 'brightness(1.1)'
          }
        },
        containedSecondary: {
          background: designSystem.gradients.secondary,
          '&:hover': {
            background: designSystem.gradients.secondary,
            filter: 'brightness(1.1)'
          }
        },
        outlined: {
          borderWidth: borderRadius.width,
          '&:hover': {
            borderWidth: borderRadius.width
          }
        },
        sizeSmall: {
          height: designSystem.components.button.height.sm,
          padding: designSystem.components.button.padding.sm
        },
        sizeMedium: {
          height: designSystem.components.button.height.md,
          padding: designSystem.components.button.padding.md
        },
        sizeLarge: {
          height: designSystem.components.button.height.lg,
          padding: designSystem.components.button.padding.lg
        }
      }
    },

    // TextField/Input
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: borderRadius.base,
            '& fieldset': {
              borderColor: colors.border.light
            },
            '&:hover fieldset': {
              borderColor: colors.border.medium
            },
            '&.Mui-focused fieldset': {
              borderColor: colors.primary.main
            }
          }
        }
      }
    },

    // Chip
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.base,
          fontWeight: typography.fontWeight.medium,
          fontSize: typography.fontSize.xs
        }
      }
    },

    // Paper
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.lg,
          backgroundImage: 'none',
        },
        elevation1: {
          boxShadow: shadows.sm
        },
        elevation2: {
          boxShadow: shadows.base
        },
        elevation3: {
          boxShadow: shadows.md
        }
      }
    },

    // ListItem
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.base,
          marginBottom: spacing[1],
          transition: transitions.all,
          '&:hover': {
            backgroundColor: colors.background.listHover
          }
        }
      }
    },

    // Divider
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: colors.border.light
        }
      }
    },

    // Table
    MuiTableRow: {
      styleOverrides: {
        root: {
          height: designSystem.components.table.rowHeight,
          '&:hover': {
            backgroundColor: `${colors.primary.main}08`
          }
        }
      }
    },

    MuiTableCell: {
      styleOverrides: {
        root: {
          padding: designSystem.components.table.cellPadding,
          borderColor: colors.border.light
        },
        head: {
          fontWeight: typography.fontWeight.semibold,
          backgroundColor: colors.background.default,
          color: colors.text.secondary,
          height: designSystem.components.table.headerHeight
        }
      }
    },

    // Avatar
    MuiAvatar: {
      styleOverrides: {
        root: {
          fontWeight: typography.fontWeight.medium
        }
      }
    },

    // Badge
    MuiBadge: {
      styleOverrides: {
        badge: {
          fontWeight: typography.fontWeight.semibold
        }
      }
    },

    // Tooltip
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: colors.background.sidebar,
          fontSize: typography.fontSize.xs,
          padding: `${spacing[2]} ${spacing[3]}`,
          borderRadius: borderRadius.base,
          boxShadow: shadows.dropdown
        }
      }
    }
  }
})

export default theme
