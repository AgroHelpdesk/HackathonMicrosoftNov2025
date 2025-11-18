import React from 'react'
import { Card, CardContent, Typography, Chip, Box, Stack, Avatar, Divider, useTheme } from '@mui/material'
import { WhatsApp, Business } from '@mui/icons-material'

export default function TicketCard({ ticket, onOpen }) {
  const theme = useTheme()
  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved': return theme.palette.success.main
      case 'escalated': return theme.palette.error.main
      default: return theme.palette.warning.main
    }
  }
  const getStatusBg = (status) => {
    switch (status) {
      case 'resolved': return `${theme.palette.success.light}20`
      case 'escalated': return `${theme.palette.error.light}20`
      default: return `${theme.palette.warning.light}20`
    }
  }
  const getChannelIcon = (channel) => {
    switch (channel) {
      case 'WhatsApp': return '💬'
      case 'ERP': return '🏢'
      default: return '📨'
    }
  }
  const getTypeEmoji = (type) => {
    if (type.includes('Diagnosis')) return '🔍'
    if (type.includes('Failure')) return '⚙️'
    if (type.includes('Stock')) return '📦'
    return '🎫'
  }
  return (
    <Card
      sx={{
        mb: { xs: 2, sm: 3 },
        cursor: 'pointer',
        border: `1px solid ${theme.palette.divider}`,
        background: getStatusBg(ticket.status),
        boxShadow: '0 8px 24px rgba(44, 95, 111, 0.08)',
        transition: 'all 0.2s ease',
        '&:hover': {
          background: getStatusBg(ticket.status),
          boxShadow: '0 16px 40px rgba(44, 95, 111, 0.12)',
          transform: 'translateY(-2px)'
        }
      }}
      onClick={onOpen}
    >
      <CardContent sx={{ pb: { xs: 1, sm: 1.5 }, px: { xs: 2, sm: 3 } }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center" justifyContent="space-between">
          <Stack direction="row" spacing={2} alignItems="center">
            <Avatar sx={{ bgcolor: getStatusColor(ticket.status), color: '#fff', width: 44, height: 44, fontWeight: 700 }}>
              {getTypeEmoji(ticket.type)}
            </Avatar>
            <Box sx={{ minWidth: 0 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: getStatusColor(ticket.status), fontSize: { xs: '0.95rem', sm: '1.05rem' } }}>
                {ticket.id}
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 500, mt: 0.5, fontSize: { xs: '0.8rem', sm: '0.875rem' }, color: 'text.secondary' }}>
                {ticket.summary}
              </Typography>
            </Box>
          </Stack>
          <Chip
            label={ticket.status === 'resolved' ? '✓ OK' : ticket.status === 'escalated' ? '⚠ ESC' : '⏳'}
            size="small"
            sx={{ fontWeight: 600, fontSize: { xs: '0.7rem', sm: '0.75rem' }, backgroundColor: getStatusBg(ticket.status), color: getStatusColor(ticket.status) }}
          />
        </Stack>
        <Divider sx={{ my: 1.5, borderColor: 'rgba(44,95,111,0.12)' }} />
        <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
          <Chip
            label={`📍 ${ticket.location}`}
            size="small"
            sx={{ backgroundColor: 'rgba(27, 94, 32, 0.08)', color: theme.palette.text.secondary, fontWeight: 500, borderRadius: 1 }}
          />
          <Chip
            label={`🌱 ${ticket.crop}`}
            size="small"
            sx={{ backgroundColor: 'rgba(27, 94, 32, 0.08)', color: theme.palette.text.secondary, fontWeight: 500, borderRadius: 1 }}
          />
          <Chip
            label={`${getChannelIcon(ticket.channel)} ${ticket.channel}`}
            size="small"
            sx={{ backgroundColor: 'rgba(27, 94, 32, 0.08)', color: theme.palette.text.secondary, fontWeight: 500, borderRadius: 1 }}
          />
        </Stack>
      </CardContent>
    </Card>
  )
}

