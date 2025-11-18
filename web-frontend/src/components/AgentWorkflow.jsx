import React, { useState, useEffect, useMemo } from 'react'
import {
  Container,
  Card,
  CardContent,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  Grid,
  Avatar,
  Chip,
  LinearProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Stack,
  Divider,
  useTheme,
  useMediaQuery
} from '@mui/material'
import {
  CloudUpload,
  Info,
  Psychology,
  CheckCircle,
  Assignment,
  Lightbulb,
  Visibility,
  Timer,
  CheckCircleOutline,
  HourglassEmpty
} from '@mui/icons-material'

const AGENT_STEPS = [
  {
    id: 'field-sense',
    name: 'FieldSense',
    role: 'Intent Agent',
    description: 'Identifies the client\'s intention',
    icon: CloudUpload,
    paletteKey: 'fieldSense',
    status: 'completed',
    duration: 2.5
  },
  {
    id: 'farm-ops',
    name: 'FarmOps',
    role: 'Info Collector',
    description: 'Collects additional information',
    icon: Info,
    paletteKey: 'harvestAI',
    status: 'completed',
    duration: 3.8
  },
  {
    id: 'agro-brain',
    name: 'AgroBrain',
    role: 'Knowledge Agent',
    description: 'Analyzes agricultural data and knowledge',
    icon: Psychology,
    paletteKey: 'agroIntel',
    status: 'in-progress',
    duration: 0
  },
  {
    id: 'runbook-master',
    name: 'RunbookMaster',
    role: 'Decision Agent',
    description: 'Executes runbooks and makes decisions',
    icon: Assignment,
    paletteKey: 'decision',
    status: 'pending',
    duration: 0
  },
  {
    id: 'explain-it',
    name: 'ExplainIt',
    role: 'Transparency Agent',
    description: 'Explains decisions and next steps',
    icon: Lightbulb,
    paletteKey: 'alert',
    status: 'pending',
    duration: 0
  }
]

const WORKFLOW_ACTIVITY = [
  { timestamp: '08:05:12', agent: 'FieldSense', action: 'Image analysis', result: 'Pest detected', icon: CloudUpload },
  { timestamp: '08:05:45', agent: 'FarmOps', action: 'Context collection', result: 'V5, Soybean, Plot 22', icon: Info },
  { timestamp: '08:06:10', agent: 'AgroBrain', action: 'Knowledge analysis', result: 'Alternaria - Fungicide recommended', icon: Psychology },
  { timestamp: '08:06:45', agent: 'RunbookMaster', action: 'Action execution', result: 'Work order created', icon: Assignment },
  { timestamp: '08:07:20', agent: 'ExplainIt', action: 'Response generation', result: 'Client notified', icon: Lightbulb }
]

const WORKFLOW_SUMMARY = [
{ label: 'Current call', value: 'T-001 · Soybean pest' },
{ label: 'Total time', value: '7.8 seconds' },
{ label: 'Model confidence', value: '92% · High' }
]

export default function AgentWorkflow() {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  const [animatingAgent, setAnimatingAgent] = useState(null)

  const agentsWithTheme = useMemo(
    () =>
      AGENT_STEPS.map(agent => ({
        ...agent,
        color: theme.palette.agents?.[agent.paletteKey] || agent.color || theme.palette.secondary.main
      })),
    [theme]
  )

  const activeStepIndex = useMemo(() => {
    const inProgress = agentsWithTheme.findIndex(agent => agent.status === 'in-progress')
    if (inProgress >= 0) return inProgress
    const pending = agentsWithTheme.findIndex(agent => agent.status === 'pending')
    const fallback = pending >= 0 ? pending : agentsWithTheme.length - 1
    return Math.max(0, fallback)
  }, [agentsWithTheme])

  useEffect(() => {
    const interval = setInterval(() => {
      setAnimatingAgent(prev => {
        const interactiveAgents = AGENT_STEPS.filter(agent => agent.status !== 'pending').map(agent => agent.id)
        const currentIndex = interactiveAgents.indexOf(prev)
        const nextIndex = (currentIndex + 1) % interactiveAgents.length
        return interactiveAgents[nextIndex]
      })
    }, 2200)

    return () => clearInterval(interval)
  }, [])

  const statusStyles = {
    completed: {
      label: 'Completed',
      icon: CheckCircle,
      chipColor: theme.palette.success.main,
      text: theme.palette.success.dark,
      background: `${theme.palette.success.light}20`
    },
    'in-progress': {
      label: 'In progress',
      icon: HourglassEmpty,
      chipColor: theme.palette.warning.main,
      text: theme.palette.warning.dark,
      background: `${theme.palette.warning.main}15`
    },
    pending: {
      label: 'Pending',
      icon: Visibility,
      chipColor: theme.palette.info.main,
      text: theme.palette.info.dark,
      background: `${theme.palette.info.light}10`
    }
  }

  return (
    <Container maxWidth="xl" sx={{ py: { xs: 3, md: 4 } }}>
      <Box sx={{ mb: { xs: 3, md: 4 } }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Real-Time Agent Workflow
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Granular control of autonomous agents acting on ticket T-001
        </Typography>
      </Box>

      <Grid container spacing={{ xs: 2, md: 3 }}>
        <Grid item xs={12}>
          <Card
            sx={{
              border: `1px solid ${theme.palette.divider}`,
              background: 'linear-gradient(135deg, rgba(95,167,119,0.08) 0%, rgba(44,95,111,0.06) 100%)',
              boxShadow: '0 16px 40px rgba(44, 95, 111, 0.08)'
            }}
          >
            <CardContent sx={{ p: { xs: 3, md: 4 } }}>
              <Stack direction={{ xs: 'column', md: 'row' }} spacing={3} alignItems="center" justifyContent="space-between">
                <Box sx={{ flex: 1 }}>
                  <Typography variant="overline" color="text.secondary">
                    Intelligent sequence
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 700, mt: 0.5 }}>
                    Agro AI Orchestration
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Coordinated flow between intent, knowledge, decision and response agents.
                  </Typography>
                </Box>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ xs: 'flex-start', sm: 'center' }}>
                  {WORKFLOW_SUMMARY.map(item => (
                    <Box
                      key={item.label}
                      sx={{
                        px: 2.5,
                        py: 1.5,
                        borderRadius: 3,
                        border: `1px solid ${theme.palette.divider}`,
                        backgroundColor: 'rgba(255,255,255,0.9)'
                      }}
                    >
                      <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        {item.label}
                      </Typography>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {item.value}
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </Stack>

              <Box sx={{ mt: 3 }}>
                <Stepper
                  activeStep={activeStepIndex}
                  alternativeLabel={!isMobile}
                  orientation={isMobile ? 'vertical' : 'horizontal'}
                  sx={{
                    p: { xs: 1, sm: 2 },
                    backgroundColor: 'rgba(255,255,255,0.6)',
                    borderRadius: 3,
                    border: `1px dashed ${theme.palette.divider}`
                  }}
                >
                  {agentsWithTheme.map(agent => {
                    const StepIcon = agent.icon
                    const currentStatus = statusStyles[agent.status]
                    return (
                      <Step key={agent.id} completed={agent.status === 'completed'}>
                        <StepLabel
                          icon={
                            <Avatar
                              sx={{
                                width: { xs: 44, md: 52 },
                                height: { xs: 44, md: 52 },
                                bgcolor: agent.color,
                                color: '#fff',
                                boxShadow: animatingAgent === agent.id ? '0 0 0 8px rgba(95,167,119,0.15)' : 'none',
                                transition: 'all 0.3s ease'
                              }}
                            >
                              <StepIcon />
                            </Avatar>
                          }
                          sx={{
                            '& .MuiStepLabel-label': {
                              fontWeight: 600,
                              mt: 1,
                              fontSize: '0.9rem'
                            }
                          }}
                        >
                          <Stack spacing={0.5} alignItems={isMobile ? 'flex-start' : 'center'}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                              {agent.name}
                            </Typography>
                            <Chip
                              size="small"
                              label={currentStatus?.label}
                              sx={{
                                backgroundColor: currentStatus?.background,
                                color: currentStatus?.text,
                                fontWeight: 600
                              }}
                            />
                          </Stack>
                        </StepLabel>
                      </Step>
                    )
                  })}
                </Stepper>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
            Detailed agent status
          </Typography>
          <Grid container spacing={2}>
            {agentsWithTheme.map(agent => {
              const StatusIcon = statusStyles[agent.status].icon
              return (
                <Grid item xs={12} sm={6} md={4} lg={3} key={agent.id}>
                  <Paper
                    sx={{
                      p: 2,
                      height: '100%',
                      border: `1px solid ${theme.palette.divider}`,
                      background: 'linear-gradient(135deg, #fff 0%, #f8fbf9 100%)',
                      transition: 'all 200ms ease',
                      transform: animatingAgent === agent.id ? 'translateY(-3px)' : 'translateY(0)',
                      boxShadow: animatingAgent === agent.id ? theme.shadows[6] : theme.shadows[1]
                    }}
                  >
                    <Stack direction="row" spacing={2} alignItems="center">
                      <Avatar sx={{ bgcolor: agent.color, width: 48, height: 48 }}>
                        <agent.icon />
                      </Avatar>
                      <Box flex={1}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {agent.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {agent.role}
                        </Typography>
                      </Box>
                      <StatusIcon sx={{ color: statusStyles[agent.status].chipColor }} />
                    </Stack>

                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                      {agent.description}
                    </Typography>

                    <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mt: 2 }}>
                      <Timer sx={{ fontSize: '1rem', color: agent.color }} />
                      <Typography variant="caption" sx={{ fontWeight: 600 }}>
                        {agent.duration > 0 ? `${agent.duration.toFixed(1)}s` : agent.status === 'in-progress' ? 'In progress...' : 'Waiting in queue'}
                      </Typography>
                    </Stack>

                    {agent.status === 'in-progress' && (
                      <LinearProgress
                        sx={{
                          mt: 2,
                          height: 6,
                          borderRadius: 999,
                          backgroundColor: `${agent.color}30`,
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 999,
                            backgroundColor: agent.color
                          }
                        }}
                      />
                    )}
                  </Paper>
                </Grid>
              )
            })}
          </Grid>
        </Grid>

        <Grid item xs={12}>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
            Real-time activity history
          </Typography>
          <TableContainer component={Paper} sx={{ borderRadius: 3, border: `1px solid ${theme.palette.divider}` }}>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ backgroundColor: '#F1F4F8' }}>
                  <TableCell>Time</TableCell>
                  <TableCell>Agent</TableCell>
                  <TableCell>Executed action</TableCell>
                  <TableCell>Result</TableCell>
                  <TableCell align="center">Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {WORKFLOW_ACTIVITY.map(row => {
                  const AgentIcon = row.icon
                  return (
                    <TableRow key={`${row.timestamp}-${row.agent}`} sx={{ '&:hover': { backgroundColor: '#F8FBF9' } }}>
                      <TableCell>
                        <Chip label={row.timestamp} size="small" sx={{ fontWeight: 600 }} />
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <AgentIcon sx={{ color: theme.palette.primary.dark }} />
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {row.agent}
                          </Typography>
                        </Stack>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{row.action}</Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={row.result}
                          sx={{
                            backgroundColor: 'rgba(95,167,119,0.12)',
                            color: theme.palette.secondary.dark,
                            borderRadius: 2
                          }}
                        />
                      </TableCell>
                      <TableCell align="center">
                        <CheckCircleOutline sx={{ color: theme.palette.success.main }} />
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>

        <Grid item xs={12}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}`, backgroundColor: '#F8FBF9' }}>
            <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
              <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="overline" color="text.secondary">
                    Final result
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700, mt: 0.5 }}>
                    Ticket resolved without human intervention
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                    Total time 7.8s · Confidence 92% · Client notified via WhatsApp
                  </Typography>
                </Box>
                <Divider flexItem orientation={isMobile ? 'horizontal' : 'vertical'} sx={{ borderColor: theme.palette.divider }} />
                <Stack direction="row" spacing={1}>
                  <Chip icon={<CheckCircle />} label="Runbook executed" color="success" variant="outlined" />
                  <Chip icon={<Lightbulb />} label="Insights saved" color="warning" variant="outlined" />
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  )
}
