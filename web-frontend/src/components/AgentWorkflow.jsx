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
  useMediaQuery,
  Button
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
  HourglassEmpty,
  PlayArrow,
  RestartAlt
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'
import { api } from '../services/api'

const AGENT_DEFINITIONS = [
  {
    id: 'field-sense',
    name: 'FieldSense',
    role: 'Intent Agent',
    description: 'Identifies the client\'s intention',
    icon: CloudUpload,
    paletteKey: 'fieldSense',
    duration: 2.5
  },
  {
    id: 'farm-ops',
    name: 'FarmOps',
    role: 'Info Collector',
    description: 'Collects additional information',
    icon: Info,
    paletteKey: 'harvestAI',
    duration: 3.8
  },
  {
    id: 'agro-brain',
    name: 'AgroBrain',
    role: 'Knowledge Agent',
    description: 'Analyzes agricultural data and knowledge',
    icon: Psychology,
    paletteKey: 'agroIntel',
    duration: 0
  },
  {
    id: 'runbook-master',
    name: 'RunbookMaster',
    role: 'Decision Agent',
    description: 'Executes runbooks and makes decisions',
    icon: Assignment,
    paletteKey: 'decision',
    duration: 0
  },
  {
    id: 'explain-it',
    name: 'ExplainIt',
    role: 'Transparency Agent',
    description: 'Explains decisions and next steps',
    icon: Lightbulb,
    paletteKey: 'alert',
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
  const [workflowState, setWorkflowState] = useState(null)
  const [animatingAgent, setAnimatingAgent] = useState(null)
  const [simulating, setSimulating] = useState(false)

  // Poll for workflow state
  useEffect(() => {
    const fetchState = async () => {
      try {
        const state = await api.getWorkflowState('T-001')
        setWorkflowState(state)

        // Determine animating agent
        const current = state.agents.find(a => a.status === 'in-progress')
        setAnimatingAgent(current ? current.id : null)
      } catch (error) {
        console.error("Error fetching workflow state:", error)
      }
    }

    fetchState()
    const interval = setInterval(fetchState, 1000)
    return () => clearInterval(interval)
  }, [])

  const handleAdvance = async () => {
    await api.advanceWorkflow('T-001')
  }

  const handleReset = async () => {
    await api.resetWorkflow('T-001')
  }

  const handleSimulate = async () => {
    try {
      setSimulating(true)
      await api.startSimulation('T-001')
    } catch (error) {
      console.error('Error starting workflow simulation:', error)
    } finally {
      setSimulating(false)
    }
  }

  const agentsWithStatus = useMemo(() => {
    if (!workflowState) return AGENT_DEFINITIONS.map(a => ({ ...a, status: 'pending', durationSeconds: 0 }))

    return AGENT_DEFINITIONS.map(def => {
      const stateAgent = workflowState.agents.find(a => a.id === def.id)
      const now = Date.now()
      let durationSeconds = 0

      if (stateAgent) {
        if (stateAgent.status === 'completed' && stateAgent.duration_ms) {
          durationSeconds = stateAgent.duration_ms / 1000
        } else if (stateAgent.status === 'in-progress' && stateAgent.started_at) {
          const started = new Date(stateAgent.started_at).getTime()
          durationSeconds = Math.max(0, (now - started) / 1000)
        }
      }

      return {
        ...def,
        status: stateAgent ? stateAgent.status : 'pending',
        durationSeconds,
        color: theme.palette.agents?.[def.paletteKey] || theme.palette.secondary.main
      }
    })
  }, [workflowState, theme])

  const activeStepIndex = useMemo(() => {
    const inProgress = agentsWithStatus.findIndex(agent => agent.status === 'in-progress')
    if (inProgress >= 0) return inProgress
    const pending = agentsWithStatus.findIndex(agent => agent.status === 'pending')
    const fallback = pending >= 0 ? pending : agentsWithStatus.length
    return Math.max(0, fallback)
  }, [agentsWithStatus])

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
      <Box sx={{ mb: { xs: 3, md: 4 }, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            Real-Time Agent Workflow
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Granular control of autonomous agents acting on ticket T-001
          </Typography>
        </Box>
        <Stack direction="row" spacing={2}>
          <Button variant="outlined" startIcon={<RestartAlt />} onClick={handleReset}>
            Reset
          </Button>
          {/* <Button
            variant="contained"
            color="success"
            startIcon={<PlayArrow />}
            onClick={handleSimulate}
            disabled={simulating}
          >
            {simulating ? 'Simulating...' : 'Simulate Workflow'}
          </Button> */}
          <Button variant="contained" startIcon={<HourglassEmpty />} onClick={handleAdvance}>
            Next Step
          </Button>
        </Stack>
      </Box>

      <Grid container spacing={{ xs: 2, md: 3 }}>
        <Grid item xs={12}>
          <Card
            sx={{
              border: `1px solid ${theme.palette.divider}`,
              background: 'rgba(255, 255, 255, 0.7)',
              backdropFilter: 'blur(20px)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.05)'
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
                        backgroundColor: 'rgba(255,255,255,0.5)'
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
                    backgroundColor: 'rgba(255,255,255,0.4)',
                    borderRadius: 3,
                    border: `1px dashed ${theme.palette.divider}`
                  }}
                >
                  {agentsWithStatus.map(agent => {
                    const StepIcon = agent.icon
                    const currentStatus = statusStyles[agent.status]
                    return (
                      <Step key={agent.id} completed={agent.status === 'completed'}>
                        <StepLabel
                          icon={
                            <motion.div
                              animate={{
                                scale: animatingAgent === agent.id ? [1, 1.1, 1] : 1,
                                boxShadow: animatingAgent === agent.id ? `0 0 0 8px ${agent.color}30` : 'none'
                              }}
                              transition={{ duration: 1.5, repeat: Infinity }}
                            >
                              <Avatar
                                sx={{
                                  width: { xs: 44, md: 52 },
                                  height: { xs: 44, md: 52 },
                                  bgcolor: agent.color,
                                  color: '#fff',
                                  transition: 'all 0.3s ease'
                                }}
                              >
                                <StepIcon />
                              </Avatar>
                            </motion.div>
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
            <AnimatePresence>
              {agentsWithStatus.map(agent => {
                const StatusIcon = statusStyles[agent.status].icon
                return (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={agent.id}>
                    <motion.div
                      layout
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Paper
                        sx={{
                          p: 2,
                          height: '100%',
                          border: `1px solid ${theme.palette.divider}`,
                          background: animatingAgent === agent.id
                            ? 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,250,245,0.9) 100%)'
                            : 'rgba(255,255,255,0.6)',
                          backdropFilter: 'blur(10px)',
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
                            {agent.durationSeconds > 0
                              ? `${agent.durationSeconds.toFixed(1)}s`
                              : agent.status === 'in-progress'
                                ? 'Processing...'
                                : 'Waiting'}
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
                    </motion.div>
                  </Grid>
                )
              })}
            </AnimatePresence>
          </Grid>
        </Grid>

        <Grid item xs={12}>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
            Real-time activity history
          </Typography>
          <TableContainer component={Paper} sx={{ borderRadius: 3, border: `1px solid ${theme.palette.divider}`, background: 'rgba(255,255,255,0.5)', backdropFilter: 'blur(10px)' }}>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ backgroundColor: 'rgba(0,0,0,0.02)' }}>
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
                    <TableRow key={`${row.timestamp}-${row.agent}`} sx={{ '&:hover': { backgroundColor: 'rgba(0,0,0,0.02)' } }}>
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
          <Card sx={{ border: `1px solid ${theme.palette.divider}`, backgroundColor: 'rgba(248, 251, 249, 0.8)', backdropFilter: 'blur(10px)' }}>
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
