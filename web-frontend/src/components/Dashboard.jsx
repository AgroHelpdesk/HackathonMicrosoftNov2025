import React, { useState } from 'react'
import {
  Grid, Card, CardContent, CardActions, Button, Chip, Typography, Box, List, ListItem, ListItemText, Divider, Container, Stack, Stepper, Step, StepLabel, Avatar
} from '@mui/material'
import { CheckCircle, HourglassEmpty, Visibility } from '@mui/icons-material'
import { TICKETS } from '../mockData'
import TicketCard from './TicketCard'
import Chat from './Chat'

export default function Dashboard() {
  const [tickets, setTickets] = useState(TICKETS)
  const [selected, setSelected] = useState(null)

  const DASHBOARD_STEPS = [
  { id: 'open', label: 'Open', value: tickets.filter(t => t.status === 'open').length, color: 'warning', icon: HourglassEmpty },
  { id: 'resolved', label: 'Resolved', value: tickets.filter(t => t.status === 'resolved').length, color: 'success', icon: CheckCircle },
  { id: 'escalated', label: 'Escalated', value: tickets.filter(t => t.status === 'escalated').length, color: 'error', icon: Visibility }
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
        <Grid item xs={6} lg={3}>
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

        <Grid item xs={6} lg={3}>
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
                    <Chat key={selected.id} ticketId={selected.id} compact={true} />
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
