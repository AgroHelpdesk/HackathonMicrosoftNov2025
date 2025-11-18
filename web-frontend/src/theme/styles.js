/**
 * AgriFlow AI - CSS Utilities
 * Classes utilitárias para uso direto nos componentes
 */

import { css } from '@emotion/react'
import designSystem from './designSystem'

const { colors, spacing, borderRadius, shadows, transitions } = designSystem

// ============================================
// LAYOUT UTILITIES
// ============================================

export const flexCenter = css`
  display: flex;
  justify-content: center;
  align-items: center;
`

export const flexBetween = css`
  display: flex;
  justify-content: space-between;
  align-items: center;
`

export const flexColumn = css`
  display: flex;
  flex-direction: column;
`

export const gridCenter = css`
  display: grid;
  place-items: center;
`

// ============================================
// CARD STYLES
// ============================================

export const cardBase = css`
  background: ${colors.background.paper};
  border-radius: ${borderRadius.lg};
  box-shadow: ${shadows.card};
  border: 1px solid ${colors.border.light};
  padding: ${spacing[6]};
  transition: ${transitions.all};

  &:hover {
    box-shadow: ${shadows.cardHover};
    transform: translateY(-2px);
  }
`

export const cardGradient = css`
  ${cardBase}
  background: linear-gradient(135deg, #FFFFFF 0%, #F5F7FA 100%);
`

// ============================================
// WORKFLOW CIRCLE (Agent Status)
// ============================================

export const workflowCircle = (color, size = 'md') => css`
  width: ${designSystem.components.workflowCircle.size[size]};
  height: ${designSystem.components.workflowCircle.size[size]};
  border-radius: ${borderRadius.full};
  background: ${colors.background.paper};
  border: 3px solid ${color};
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: ${shadows.base};
  transition: ${transitions.all};
  position: relative;

  &:hover {
    transform: scale(1.1);
    box-shadow: ${shadows.md};
  }

  svg, .icon {
    font-size: ${designSystem.components.workflowCircle.iconSize[size]};
    color: ${color};
  }
`

export const workflowCircleActive = (color, size = 'md') => css`
  ${workflowCircle(color, size)}
  background: ${color};
  
  svg, .icon {
    color: ${colors.text.light};
  }

  &::after {
    content: '';
    position: absolute;
    top: -4px;
    right: -4px;
    width: 12px;
    height: 12px;
    background: ${colors.status.success};
    border-radius: ${borderRadius.full};
    border: 2px solid ${colors.background.paper};
  }
`

// ============================================
// SIDEBAR STYLES
// ============================================

export const sidebarItem = css`
  display: flex;
  align-items: center;
  padding: ${spacing[3]} ${spacing[4]};
  border-radius: ${borderRadius.base};
  color: ${colors.text.light};
  text-decoration: none;
  transition: ${transitions.all};
  margin: ${spacing[1]} ${spacing[2]};
  cursor: pointer;

  &:hover {
    background: ${colors.background.sidebarHover};
  }

  &.active {
    background: ${colors.primary.main};
    box-shadow: ${shadows.button};
  }

  svg, .icon {
    margin-right: ${spacing[3]};
    font-size: ${designSystem.components.sidebar.iconSize};
  }
`

export const sidebarDivider = css`
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: ${spacing[4]} ${spacing[2]};
`

// ============================================
// BADGE STYLES
// ============================================

export const statusBadge = (status) => {
  const statusColors = {
    success: colors.status.success,
    warning: colors.status.warning,
    error: colors.status.error,
    info: colors.status.info,
    pending: colors.status.pending
  }

  return css`
    display: inline-flex;
    align-items: center;
    padding: ${spacing[1]} ${spacing[3]};
    border-radius: ${borderRadius.full};
    background: ${statusColors[status] || colors.status.info}15;
    color: ${statusColors[status] || colors.status.info};
    font-size: ${designSystem.typography.fontSize.xs};
    font-weight: ${designSystem.typography.fontWeight.semibold};
    text-transform: uppercase;
    letter-spacing: 0.05em;
  `
}

// ============================================
// BUTTON STYLES
// ============================================

export const buttonPrimary = css`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: ${spacing[3]} ${spacing[6]};
  background: ${designSystem.gradients.primary};
  color: ${colors.text.light};
  border: none;
  border-radius: ${borderRadius.base};
  font-weight: ${designSystem.typography.fontWeight.medium};
  font-size: ${designSystem.typography.fontSize.sm};
  cursor: pointer;
  transition: ${transitions.all};
  box-shadow: ${shadows.button};

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${shadows.md};
    filter: brightness(1.1);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`

export const buttonSecondary = css`
  ${buttonPrimary}
  background: ${designSystem.gradients.secondary};
`

export const buttonOutline = css`
  ${buttonPrimary}
  background: transparent;
  color: ${colors.primary.main};
  border: 2px solid ${colors.primary.main};
  box-shadow: none;

  &:hover {
    background: ${colors.primary.main};
    color: ${colors.text.light};
  }
`

// ============================================
// INPUT STYLES
// ============================================

export const inputBase = css`
  width: 100%;
  height: ${designSystem.components.input.height};
  padding: ${designSystem.components.input.padding};
  border: 1px solid ${colors.border.light};
  border-radius: ${designSystem.components.input.radius};
  font-size: ${designSystem.typography.fontSize.sm};
  transition: ${transitions.all};
  background: ${colors.background.paper};

  &:hover {
    border-color: ${colors.border.medium};
  }

  &:focus {
    outline: none;
    border-color: ${colors.primary.main};
    box-shadow: 0 0 0 3px ${colors.primary.main}15;
  }

  &::placeholder {
    color: ${colors.text.muted};
  }

  &:disabled {
    background: ${colors.background.default};
    cursor: not-allowed;
  }
`

// ============================================
// TABLE STYLES
// ============================================

export const tableContainer = css`
  width: 100%;
  overflow-x: auto;
  border-radius: ${borderRadius.lg};
  box-shadow: ${shadows.card};
  border: 1px solid ${colors.border.light};
`

export const tableHeader = css`
  background: ${colors.background.default};
  color: ${colors.text.secondary};
  font-weight: ${designSystem.typography.fontWeight.semibold};
  font-size: ${designSystem.typography.fontSize.xs};
  text-transform: uppercase;
  letter-spacing: 0.05em;
`

export const tableRow = css`
  height: ${designSystem.components.table.rowHeight};
  border-bottom: 1px solid ${colors.border.light};
  transition: ${transitions.colors};

  &:hover {
    background: ${colors.primary.main}08;
  }

  &:last-child {
    border-bottom: none;
  }
`

// ============================================
// LOADING & ANIMATIONS
// ============================================

export const spinner = css`
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  width: 40px;
  height: 40px;
  border: 4px solid ${colors.border.light};
  border-top-color: ${colors.primary.main};
  border-radius: ${borderRadius.full};
  animation: spin 800ms linear infinite;
`

export const pulse = css`
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
`

export const fadeIn = css`
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  animation: fadeIn 400ms ease-out;
`

// ============================================
// SCROLLBAR CUSTOM
// ============================================

export const customScrollbar = css`
  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  &::-webkit-scrollbar-track {
    background: ${colors.background.default};
    border-radius: ${borderRadius.base};
  }

  &::-webkit-scrollbar-thumb {
    background: ${colors.border.medium};
    border-radius: ${borderRadius.base};

    &:hover {
      background: ${colors.border.dark};
    }
  }
`

// ============================================
// TEXT UTILITIES
// ============================================

export const textTruncate = css`
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`

export const textClamp = (lines = 2) => css`
  display: -webkit-box;
  -webkit-line-clamp: ${lines};
  -webkit-box-orient: vertical;
  overflow: hidden;
`

// ============================================
// GLASSMORPHISM EFFECT
// ============================================

export const glassEffect = css`
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: ${shadows.lg};
`

// ============================================
// EXPORT ALL
// ============================================

const styles = {
  // Layout
  flexCenter,
  flexBetween,
  flexColumn,
  gridCenter,
  
  // Cards
  cardBase,
  cardGradient,
  
  // Workflow
  workflowCircle,
  workflowCircleActive,
  
  // Sidebar
  sidebarItem,
  sidebarDivider,
  
  // Badge
  statusBadge,
  
  // Buttons
  buttonPrimary,
  buttonSecondary,
  buttonOutline,
  
  // Inputs
  inputBase,
  
  // Table
  tableContainer,
  tableHeader,
  tableRow,
  
  // Animations
  spinner,
  pulse,
  fadeIn,
  
  // Utilities
  customScrollbar,
  textTruncate,
  textClamp,
  glassEffect
}

export default styles
