import React, { useState, useEffect } from 'react'
import {
  Grid, Card, CardContent, CardActions, Button, Chip, Typography, Box, List, ListItem, ListItemText, Divider, Container, Stack, Stepper, Step, StepLabel, Avatar
} from '@mui/material'
import { CheckCircle, HourglassEmpty, Visibility, Chat, Sms, Web } from '@mui/icons-material'
import { api } from '../services/api'
import TicketCard from './TicketCard'
import ChatComponent from './Chat'

export default function Dashboard() {
  const [tickets, setTickets] = useState([])
  const [selected, setSelected] = useState(null)
  const [channelMetrics, setChannelMetrics] = useState({
    web: 0,
    acs_chat: 0,
    sms: 0
  })

  useEffect(() => {
    api.getTickets().then(data => {
      setTickets(data)
      // Calculate channel metrics
      const metrics = data.reduce((acc, ticket) => {
        const channel = ticket.channel || 'web'
        acc[channel] = (acc[channel] || 0) + 1
        return acc
      }, { web: 0, acs_chat: 0, sms: 0 })
      setChannelMetrics(metrics)
    })
  }, [])

  const DASHBOARD_STEPS = [
    { id: 'open', label: 'Open', value: tickets.filter(t => t.status === 'open').length, color: 'warning', icon: HourglassEmpty },
    { id: 'resolved', label: 'Resolved', value: tickets.filter(t => t.status === 'resolved').length, color: 'success', icon: CheckCircle },
    { id: 'escalated', label: 'Escalated', value: tickets.filter(t => t.status === 'escalated').length, color: 'error', icon: Visibility }
  ]

  const CHANNEL_STATS = [
    { id: 'web', label: 'Web', value: channelMetrics.web, icon: Web, color: '#1976d2' },
    { id: 'acs_chat', label: 'ACS Chat', value: channelMetrics.acs_chat, icon: Chat, color: '#2e7d32' },
    { id: 'sms', label: 'SMS', value: channelMetrics.sms, icon: Sms, color: '#f57c00' }
  ]

  function resolveTicket(id, action) {
    setTickets(prev => prev.map(t => t.id === id ? { ...t, status: action } : t))
  }

  return (
    <Box>
      <Box sx={{ mb: { xs: 2, sm: 3 } }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5, fontSize: { xs: '1.75rem', sm: '2.125rem' } }}>
          Control Panel
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Visualize and manage all tickets in real time
        </Typography>
      </Box>

      <Grid container spacing={{ xs: 2, sm: 3 }}>
        {/* Multi-Channel Statistics */}
        <Grid item xs={12}>
          <Card sx={{ background: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)' }}>
            <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, fontSize: { xs: '1.1rem', sm: '1.25rem' } }}>
                📡 Multi-Channel Overview
              </Typography>
              <Grid container spacing={2}>
                {CHANNEL_STATS.map(channel => (
                  <Grid item xs={12} sm={4} key={channel.id}>
                    <Box sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 2,
                      p: 2,
                      bgcolor: 'rgba(255, 255, 255, 0.8)',
                      borderRadius: 2,
                      border: '1px solid rgba(0,0,0,0.1)'
                    }}>
                      <Avatar sx={{ bgcolor: channel.color, width: 48, height: 48 }}>
                        <channel.icon />
                      </Avatar>
                      <Box>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                          {channel.label}
                        </Typography>
                        <Typography variant="h5" sx={{ fontWeight: 700 }}>
                          {channel.value}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={7}>
          <Card sx={{ background: 'linear-gradient(135deg, #ffffff 0%, #f1f8e9 100%)' }}>
            <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                <Typography variant="h5" sx={{ fontWeight: 700, flex: 1, fontSize: { xs: '1.25rem', sm: '1.5rem' } }}>
                  🎫 Active Tickets
                </Typography>
                <Chip
                  label={`${tickets.filter(t => t.status === 'open').length} open`}
                  color="warning"
                  size="small"
                />
              </Box>
              {/* Gráfico estilo AgentWorkflow */}
              <Box sx={{ mb: 3 }}>
                <Stepper
                  activeStep={0}
                  alternativeLabel
                  sx={{ background: 'rgba(255,255,255,0.6)', borderRadius: 3, border: '1px dashed #e0e0e0', p: 2 }}
                >
                  {DASHBOARD_STEPS.map(step => (
                    <Step key={step.id} completed={step.id === 'resolved'}>
                      <StepLabel
                        icon={
                          <Avatar sx={{ bgcolor: step.color === 'success' ? '#2e7d32' : step.color === 'warning' ? '#fbc02d' : '#d32f2f', color: '#fff', width: 44, height: 44 }}>
                            <step.icon />
                          </Avatar>
                        }
                        sx={{ '& .MuiStepLabel-label': { fontWeight: 600, mt: 1, fontSize: '0.9rem' } }}
                      >
                        <Stack spacing={0.5} alignItems="center">
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {step.label}
                          </Typography>
                          <Chip
                            size="small"
                            label={step.value}
                            sx={{ backgroundColor: step.color === 'success' ? '#e8f5e9' : step.color === 'warning' ? '#fffde7' : '#ffebee', color: step.color === 'success' ? '#2e7d32' : step.color === 'warning' ? '#fbc02d' : '#d32f2f', fontWeight: 600 }}
                          />
                        </Stack>
                      </StepLabel>
                    </Step>
                  ))}
                </Stepper>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {tickets.map(t => (
                  <TicketCard key={t.id} ticket={t} onOpen={() => setSelected(t)} />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={5}>
          <Card sx={{ background: 'linear-gradient(135deg, #ffffff 0%, #f1f8e9 100%)', height: 'fit-content' }}>
            <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, fontSize: { xs: '1.25rem', sm: '1.5rem' } }}>
                ℹ️ Details
              </Typography>
              {selected ? (
                <Box>
                  <Box sx={{ mb: 2, pb: 2, borderBottom: '2px solid rgba(27, 94, 32, 0.1)' }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1b5e20' }}>
                      {selected.id}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                      {selected.summary}
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 1.5 }}>
                    <Typography variant="caption" sx={{ fontWeight: 600, color: '#558b2f' }}>TYPE</Typography>
                    <Typography variant="body2">{selected.type}</Typography>
                  </Box>

                  <Box sx={{ mb: 1.5 }}>
                    <Typography variant="caption" sx={{ fontWeight: 600, color: '#558b2f' }}>STATUS</Typography>
                    <Box sx={{ mt: 0.5 }}>
                      <Chip
                        label={selected.status === 'resolved' ? '✓ Resolved' : selected.status === 'escalated' ? '⚠ Escalated' : '⏳ Open'}
                        color={selected.status === 'resolved' ? 'success' : 'warning'}
                        variant="filled"
                      />
                    </Box>
                  </Box>

                  <Box sx={{ mb: 1.5 }}>
                    <Typography variant="caption" sx={{ fontWeight: 600, color: '#558b2f' }}>LOCATION</Typography>
                    <Typography variant="body2">📍 {selected.location}</Typography>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ fontWeight: 600, color: '#558b2f' }}>CROP</Typography>
                    <Typography variant="body2">🌱 {selected.crop}</Typography>
                  </Box>

                  <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, pt: 1, borderTop: '2px solid rgba(27, 94, 32, 0.1)' }}>
                    Agent History
                  </Typography>
                  <List dense>
                    {selected.steps.map((s, i) => (
                      <ListItem key={i} sx={{ py: 0.5 }}>
                        <ListItemText
                          primary={`🤖 ${s.agent}`}
                          secondary={s.text}
                          primaryTypographyProps={{ sx: { fontSize: '0.8rem', fontWeight: 600 } }}
                          secondaryTypographyProps={{ sx: { fontSize: '0.75rem', mt: 0.25 } }}
                        />
                        <Typography variant="caption" sx={{ minWidth: 60, textAlign: 'right', color: '#999' }}>
                          {new Date(s.ts).toLocaleTimeString()}
                        </Typography>
                      </ListItem>
                    ))}
                  </List>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, pt: 1, borderTop: '2px solid rgba(27, 94, 32, 0.1)' }}>
                    💬 Chat with Client
                  </Typography>
                  <Box sx={{ maxHeight: 700, overflow: 'auto', border: '1px solid #e0e0e0', borderRadius: 2, p: 1 }}>
                    <ChatComponent ticketId={selected.id} compact={true} />
                  </Box>
                  <CardActions sx={{ justifyContent: 'flex-end', pt: 2, px: 0 }}>
                    <Button
                      size="small"
                      variant="contained"
                      sx={{ background: '#2e7d32' }}
                      onClick={() => resolveTicket(selected.id, 'resolved')}
                    >
                      ✓ Resolved
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      sx={{ borderColor: '#f57c00', color: '#f57c00' }}
                      onClick={() => resolveTicket(selected.id, 'escalated')}
                    >
                      ⚠ Escalate
                    </Button>
                  </CardActions>
                </Box>
              ) : (
                <Box sx={{ p: { xs: 2, sm: 3 }, textAlign: 'center', color: '#999' }}>
                  <Typography variant="body2">
                    👈 Select a ticket to see details
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}
