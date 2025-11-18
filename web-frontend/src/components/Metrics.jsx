import React from 'react'
import {
  Box, Grid, Card, CardContent, Typography, LinearProgress, List, ListItem, ListItemText
} from '@mui/material'
import { TrendingDown, AccessTime, CheckCircle, Warning } from '@mui/icons-material'
import { METRICS } from '../mockData'

const metrics = [
  { title: 'Reduction of Repetitive Calls', value: `${METRICS.reduction}%`, icon: <TrendingDown />, color: 'success', progress: METRICS.reduction },
  { title: 'Average Resolution Time', value: `${METRICS.avgResolutionTime} min`, icon: <AccessTime />, color: 'primary', progress: 80 },
  { title: 'Classification Accuracy', value: `${METRICS.accuracy}%`, icon: <CheckCircle />, color: 'success', progress: METRICS.accuracy },
  { title: 'Escalated Calls', value: `${METRICS.escalated}%`, icon: <Warning />, color: 'warning', progress: METRICS.escalated }
]

export default function Metrics() {
  return (
    <Box>
      <Box sx={{ mb: { xs: 3, sm: 4 } }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Metrics Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Visualize performance and impact of automatic resolution
        </Typography>
      </Box>
      <Grid container spacing={{ xs: 2, md: 3 }}>
        {metrics.map((metric, i) => (
          <Grid item xs={12} sm={6} lg={3} key={i}>
            <Card sx={{
              border: `1px solid #e0e0e0`,
              background: 'linear-gradient(135deg, rgba(95,167,119,0.08) 0%, rgba(44,95,111,0.06) 100%)',
              boxShadow: '0 8px 24px rgba(44, 95, 111, 0.08)',
              height: 'fit-content'
            }}>
              <CardContent sx={{ p: { xs: 3, md: 4 } }}>
                <Box display="flex" alignItems="center" mb={2}>
                  <Box sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    background: metric.color === 'success' ? '#c8e6c9' : metric.color === 'warning' ? '#ffe0b2' : '#b3e5fc',
                    mr: 2
                  }}>
                    {React.cloneElement(metric.icon, { color: metric.color, sx: { fontSize: '1.5rem' } })}
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="caption" sx={{ color: '#558b2f', fontWeight: 600, fontSize: '0.8rem' }}>
                      {metric.title}
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="h3" sx={{
                  fontWeight: 700,
                  color: metric.color === 'success' ? '#1b5e20' : metric.color === 'warning' ? '#f57c00' : '#0277bd',
                  mb: 1,
                  fontSize: '2rem'
                }}>
                  {metric.value}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={metric.progress}
                  sx={{
                    mt: 1.5,
                    height: 6,
                    borderRadius: 999,
                    background: metric.color === 'success' ? '#c8e6c9' : metric.color === 'warning' ? '#ffe0b2' : '#b3e5fc',
                    '& .MuiLinearProgress-bar': {
                      background: metric.color === 'success' ? '#1b5e20' : metric.color === 'warning' ? '#f57c00' : '#0277bd',
                      borderRadius: 999
                    }
                  }}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
        <Grid item xs={12}>
          <Card sx={{ border: `1px solid #e0e0e0`, background: 'linear-gradient(135deg, rgba(95,167,119,0.08) 0%, rgba(44,95,111,0.06) 100%)', boxShadow: '0 8px 24px rgba(44, 95, 111, 0.08)' }}>
            <CardContent sx={{ p: { xs: 3, md: 4 } }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#1b5e20', fontSize: '1.15rem' }}>
                ⚙️ Symptom Ranking by Machine Type
              </Typography>
              <List sx={{ p: 0 }}>
                {METRICS.topSymptoms.map((symptom, i) => (
                  <ListItem key={i} sx={{
                    py: 1.5,
                    px: 0,
                    borderBottom: i < METRICS.topSymptoms.length - 1 ? '1px solid rgba(27, 94, 32, 0.1)' : 'none',
                    flexDirection: { xs: 'column', sm: 'row' },
                    alignItems: { xs: 'flex-start', sm: 'center' },
                    gap: 2
                  }}>
                    <Box sx={{ flex: 1, width: { xs: '100%', sm: 'auto' } }}>
                      <Typography variant="body2" sx={{ fontWeight: 600, color: '#1b5e20', fontSize: '1rem' }}>
                        {symptom.machine}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.85rem' }}>
                        {symptom.symptom}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: { xs: '100%', sm: 150 }, justifyContent: { xs: 'space-between', sm: 'flex-end' } }}>
                      <LinearProgress
                        variant="determinate"
                        value={symptom.percentage}
                        sx={{
                          flex: 1,
                          height: 6,
                          borderRadius: 999,
                          background: '#e8f5e9',
                          '& .MuiLinearProgress-bar': { background: '#f57c00', borderRadius: 999 }
                        }}
                      />
                      <Typography variant="caption" sx={{ fontWeight: 700, minWidth: 35, textAlign: 'right', color: '#f57c00', fontSize: '0.85rem' }}>
                        {symptom.percentage}%
                      </Typography>
                    </Box>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}