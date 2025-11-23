import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  Box, Paper, Typography, TextField, Button, List, ListItem, Avatar,
  CircularProgress, Alert, Chip
} from '@mui/material'
import { Send } from '@mui/icons-material'
import { colors, spacing, borderRadius, shadows, gradients, typography } from '../theme/designSystem'
import { apiClient } from '../services/apiClient'

export default function Chat({ ticketId: propTicketId, compact = false }) {
  const { ticketId: paramTicketId } = useParams()
  const ticketId = propTicketId || paramTicketId
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSend = async () => {
    if (newMessage.trim() && !loading) {
      const userMessage = newMessage.trim()
      setNewMessage('')
      setError(null)

      // Add user message immediately
      const userMsg = {
        sender: 'user',
        text: userMessage,
        ts: new Date().toISOString()
      }
      setMessages(prev => [...prev, userMsg])

      // Call backend API
      setLoading(true)
      try {
        const response = await apiClient.sendMessage(userMessage, null, ticketId)
        const formatted = apiClient.formatAgentResponse(response)

        // Add agent response
        const agentMsg = {
          sender: 'agent',
          text: formatted.message,
          ts: new Date().toISOString(),
          agents: formatted.agents,
          intent: formatted.intent,
          sources: formatted.sources,
          action: formatted.action,
          riskLevel: formatted.riskLevel
        }
        setMessages(prev => [...prev, agentMsg])
      } catch (err) {
        console.error('Error sending message:', err)
        setError(err.message || 'Failed to send message')

        // Add error message
        setMessages(prev => [...prev, {
          sender: 'agent',
          text: 'Desculpe, ocorreu um erro. Por favor, tente novamente.',
          ts: new Date().toISOString(),
          isError: true
        }])
      } finally {
        setLoading(false)
      }
    }
  }

  return (
    <Box sx={{ maxWidth: { xs: '100%', md: 900 }, mx: 'auto', px: { xs: spacing[2], sm: spacing[4] } }}>
      <Box sx={{ mb: { xs: spacing[4], sm: spacing[6] } }}>
        <Typography variant="h4" sx={{ fontWeight: typography.fontWeight.bold, mb: spacing[1], fontSize: { xs: typography.fontSize['2xl'], sm: typography.fontSize['3xl'] } }}>
          💬 Chat — {ticketId || 'New'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Powered by AI Agents (FieldSense, AgroBrain, RunbookMaster)
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: spacing[3] }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper sx={{
        height: compact ? 500 : { xs: 350, sm: 450 },
        overflow: 'auto',
        p: { xs: spacing[3], sm: spacing[4] },
        mb: spacing[4],
        background: gradients.card,
        borderRadius: borderRadius.lg,
        boxShadow: shadows.card
      }}>
        <List sx={{ p: 0 }}>
          {messages.map((msg, i) => (
            <ListItem key={i} sx={{
              justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              mb: { xs: spacing[2], sm: spacing[3] },
              p: 0,
              flexDirection: 'column',
              alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start'
            }}>
              <Box sx={{
                display: 'flex',
                alignItems: 'flex-end',
                maxWidth: { xs: '90%', sm: '75%' },
                gap: spacing[2],
                flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row'
              }}>
                <Avatar sx={{
                  bgcolor: msg.sender === 'agent' ? colors.status.success : colors.status.warning,
                  width: { xs: 28, sm: 32 },
                  height: { xs: 28, sm: 32 },
                  fontSize: { xs: typography.fontSize.sm, sm: typography.fontSize.base }
                }}>
                  {msg.sender === 'agent' ? '🤖' : '👨‍🌾'}
                </Avatar>
                <Paper sx={{
                  p: { xs: spacing[2], sm: spacing[3] },
                  bgcolor: msg.sender === 'user' ? colors.primary.main : colors.background.paper,
                  color: msg.sender === 'user' ? colors.primary.contrastText : colors.text.primary,
                  borderRadius: borderRadius.base,
                  borderLeft: msg.sender === 'agent' ? `3px solid ${colors.status.success}` : 'none',
                  maxWidth: '100%',
                  boxShadow: shadows.sm
                }}>
                  <Typography variant="body2">{msg.text}</Typography>

                  {msg.sender === 'agent' && msg.intent && (
                    <Box sx={{ mt: spacing[2], display: 'flex', gap: spacing[1], flexWrap: 'wrap' }}>
                      <Chip label={`Intent: ${msg.intent}`} size="small" color="primary" />
                      {msg.action && <Chip label={msg.action} size="small" color="secondary" />}
                    </Box>
                  )}

                  <Typography variant="caption" sx={{ display: 'block', mt: spacing[1], opacity: 0.7 }}>
                    {new Date(msg.ts).toLocaleTimeString()}
                  </Typography>
                </Paper>
              </Box>
            </ListItem>
          ))}

          {loading && (
            <ListItem sx={{ justifyContent: 'center', py: spacing[3] }}>
              <CircularProgress size={24} />
              <Typography variant="body2" sx={{ ml: spacing[2] }}>
                Processando com os agentes...
              </Typography>
            </ListItem>
          )}
        </List>
      </Paper>

      <Box sx={{ display: 'flex', gap: spacing[2], flexDirection: { xs: 'column', sm: 'row' } }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Digite sua mensagem..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          disabled={loading}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: borderRadius.base
            }
          }}
        />
        <Button
          variant="contained"
          endIcon={<Send />}
          onClick={handleSend}
          disabled={loading || !newMessage.trim()}
          sx={{
            background: gradients.primary,
            borderRadius: borderRadius.base,
            fontWeight: typography.fontWeight.medium,
            minWidth: { xs: '100%', sm: 'auto' },
            boxShadow: shadows.button
          }}
        >
          Enviar
        </Button>
      </Box>
    </Box>
  )
}