import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  Box, Paper, Typography, TextField, Button, List, ListItem, ListItemText, Avatar, Divider
} from '@mui/material'
import { Send } from '@mui/icons-material'
import { colors, spacing, borderRadius, shadows, gradients, typography, components } from '../theme/designSystem'

const mockConversations = {
  'T-001': [
    { sender: 'user', text: 'I found some caterpillars in plot 22. Can you see what it is?', ts: '2025-11-14T08:00:00' },
    { sender: 'agent', text: 'Sure, can you send me a photo?', ts: '2025-11-14T08:01:00' },
    { sender: 'user', text: '[Photo sent]', ts: '2025-11-14T08:02:00' },
    { sender: 'agent', text: 'I analyzed the photo and identified Helicoverpa armigera caterpillar. Since your crop is at V5 stage and the weather allows inspection, I recommend monitoring 3 more points in the plot. Here is the automatic report with current risk and suggested locations to check. I also notified agronomist Maria, who will review the case.', ts: '2025-11-14T08:05:00' }
  ],
  'T-002': [
    { sender: 'user', text: 'My harvester is vibrating strongly in plot 12.', ts: '2025-11-14T06:00:00' },
    { sender: 'agent', text: 'Understood. I will check your machine now.', ts: '2025-11-14T06:01:00' },
    { sender: 'agent', text: 'Carlos, I checked the telemetry of CH670-02 and confirmed vibration above the limit. This may indicate wear or something stuck in the rotor. For safety, stop the machine now. I activated mechanic João Lima, who has already received your location and failure data. I will notify when he is on the way.', ts: '2025-11-14T06:05:00' }
  ]
}

export default function Chat({ ticketId: propTicketId, compact = false }) {
  const { ticketId: paramTicketId } = useParams()
  const ticketId = propTicketId || paramTicketId
  const [messages, setMessages] = useState(mockConversations[ticketId] || [])
  const [newMessage, setNewMessage] = useState('')

  const handleSend = () => {
    if (newMessage.trim()) {
      setMessages([...messages, { sender: 'user', text: newMessage, ts: new Date().toISOString() }])
      setNewMessage('')
      // Mock agent response
      setTimeout(() => {
        setMessages(prev => [...prev, {
          sender: 'agent',
          text: 'Thank you for the information. I am processing with the agents...',
          ts: new Date().toISOString()
        }])
      }, 2000)
    }
  }

  return (
    <Box sx={{ maxWidth: { xs: '100%', md: 900 }, mx: 'auto', px: { xs: spacing[2], sm: spacing[4] } }}>
      <Box sx={{ mb: { xs: spacing[4], sm: spacing[6] } }}>
        <Typography variant="h4" sx={{ fontWeight: typography.fontWeight.bold, mb: spacing[1], fontSize: { xs: typography.fontSize['2xl'], sm: typography.fontSize['3xl'] }, display: 'flex', alignItems: 'center', gap: spacing[2] }}>
          💬 Chat Simulation — {ticketId}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Conversation with the client and real-time analysis by agents
        </Typography>
      </Box>

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
                  fontSize: { xs: typography.fontSize.sm, sm: typography.fontSize.base },
                  flexShrink: 0
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
                  <Typography variant="body2" sx={{ fontSize: { xs: typography.fontSize.sm, sm: typography.fontSize.base } }}>{msg.text}</Typography>
                  <Typography variant="caption" sx={{
                    display: 'block',
                    mt: spacing[1],
                    opacity: 0.7,
                    fontSize: { xs: typography.fontSize.xs, sm: '0.75rem' }
                  }}>
                    {new Date(msg.ts).toLocaleTimeString()}
                  </Typography>
                </Paper>
              </Box>
            </ListItem>
          ))}
        </List>
      </Paper>
      <Box sx={{ display: 'flex', gap: spacing[2], flexDirection: { xs: 'column', sm: 'row' } }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: borderRadius.base,
              '&:hover fieldset': { borderColor: colors.primary.light },
              '&.Mui-focused fieldset': { borderColor: colors.primary.main }
            }
          }}
        />
        <Button
          variant="contained"
          endIcon={<Send />}
          onClick={handleSend}
          sx={{
            background: gradients.primary,
            borderRadius: borderRadius.base,
            fontWeight: typography.fontWeight.medium,
            minWidth: { xs: '100%', sm: 'auto' },
            mt: { xs: spacing[2], sm: 0 },
            boxShadow: shadows.button,
            '&:hover': {
              background: gradients.primary,
              boxShadow: shadows.md
            }
          }}
        >
          Send
        </Button>
      </Box>
    </Box>
  )
}