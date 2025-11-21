import React, { useState } from 'react'
import {
    Box,
    Card,
    CardContent,
    Typography,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Chip,
    List,
    ListItem,
    ListItemText,
    Divider,
    Paper,
    Stepper,
    Step,
    StepLabel,
    StepContent,
    Avatar,
    LinearProgress
} from '@mui/material'
import {
    ExpandMore,
    Psychology,
    Agriculture,
    SmartToy,
    AutoAwesome,
    Visibility,
    CheckCircle,
    Info
} from '@mui/icons-material'

/**
 * Transparency Panel Component
 * 
 * Displays ExplainIt agent output with decision trees and transparency reports
 */
export default function TransparencyPanel({ agentHistory, decision, transparencyReport }) {
    const [expanded, setExpanded] = useState('flow')

    const handleChange = (panel) => (event, isExpanded) => {
        setExpanded(isExpanded ? panel : false)
    }

    const agentIcons = {
        'FieldSense': <Psychology />,
        'FarmOps': <Agriculture />,
        'AgroBrain': <SmartToy />,
        'RunbookMaster': <AutoAwesome />,
        'ExplainIt': <Visibility />
    }

    const agentColors = {
        'FieldSense': '#1976d2',
        'FarmOps': '#388e3c',
        'AgroBrain': '#f57c00',
        'RunbookMaster': '#7b1fa2',
        'ExplainIt': '#0288d1'
    }

    if (!agentHistory || agentHistory.length === 0) {
        return (
            <Card sx={{ background: 'linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%)' }}>
                <CardContent sx={{ p: 3, textAlign: 'center' }}>
                    <Visibility sx={{ fontSize: 48, color: '#90caf9', mb: 2 }} />
                    <Typography variant="body1" color="text.secondary">
                        No agent processing data available yet.
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                        Send a message to see the transparency report.
                    </Typography>
                </CardContent>
            </Card>
        )
    }

    return (
        <Box>
            <Box sx={{ mb: 2 }}>
                <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
                    🔍 Transparency Report
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Complete breakdown of AI decision-making process
                </Typography>
            </Box>

            {/* Agent Flow */}
            <Accordion
                expanded={expanded === 'flow'}
                onChange={handleChange('flow')}
                sx={{ mb: 2, borderRadius: 2, '&:before': { display: 'none' } }}
            >
                <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <SmartToy color="primary" />
                        <Typography sx={{ fontWeight: 600 }}>Agent Processing Flow</Typography>
                    </Box>
                </AccordionSummary>
                <AccordionDetails>
                    <Stepper orientation="vertical">
                        {agentHistory.map((agent, index) => {
                            const agentName = agent.agent_name
                            const agentData = agent.data || {}

                            return (
                                <Step key={index} active completed={agent.success}>
                                    <StepLabel
                                        StepIconComponent={() => (
                                            <Avatar
                                                sx={{
                                                    bgcolor: agentColors[agentName] || '#757575',
                                                    width: 32,
                                                    height: 32
                                                }}
                                            >
                                                {agentIcons[agentName] || <SmartToy />}
                                            </Avatar>
                                        )}
                                    >
                                        <Box>
                                            <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                                                {agentName}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                {agent.timestamp}
                                            </Typography>
                                        </Box>
                                    </StepLabel>
                                    <StepContent>
                                        <Paper elevation={0} sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                                            {/* FieldSense */}
                                            {agentName === 'FieldSense' && (
                                                <Box>
                                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                                        <strong>Intent:</strong> {agentData.intent}
                                                    </Typography>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                        <Typography variant="body2">
                                                            <strong>Confidence:</strong>
                                                        </Typography>
                                                        <LinearProgress
                                                            variant="determinate"
                                                            value={(agentData.confidence || 0) * 100}
                                                            sx={{ flex: 1, height: 6, borderRadius: 3 }}
                                                        />
                                                        <Typography variant="caption">
                                                            {Math.round((agentData.confidence || 0) * 100)}%
                                                        </Typography>
                                                    </Box>
                                                </Box>
                                            )}

                                            {/* FarmOps */}
                                            {agentName === 'FarmOps' && (
                                                <Box>
                                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                                        <strong>Context Complete:</strong>{' '}
                                                        {agentData.complete ? (
                                                            <Chip label="Yes" size="small" color="success" />
                                                        ) : (
                                                            <Chip label="No" size="small" color="warning" />
                                                        )}
                                                    </Typography>
                                                    {agentData.missing_fields && agentData.missing_fields.length > 0 && (
                                                        <Typography variant="caption" color="text.secondary">
                                                            Missing: {agentData.missing_fields.join(', ')}
                                                        </Typography>
                                                    )}
                                                </Box>
                                            )}

                                            {/* AgroBrain */}
                                            {agentName === 'AgroBrain' && (
                                                <Box>
                                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                                        <strong>Knowledge Items Found:</strong>{' '}
                                                        {agentData.metadata?.knowledge_items_found || 0}
                                                    </Typography>
                                                    {agentData.recommendations && (
                                                        <Box sx={{ mt: 1 }}>
                                                            <Typography variant="caption" sx={{ fontWeight: 600 }}>
                                                                Recommendations:
                                                            </Typography>
                                                            <List dense sx={{ pl: 2 }}>
                                                                {agentData.recommendations.slice(0, 3).map((rec, i) => (
                                                                    <ListItem key={i} sx={{ py: 0.5, px: 0 }}>
                                                                        <Typography variant="caption">• {rec}</Typography>
                                                                    </ListItem>
                                                                ))}
                                                            </List>
                                                        </Box>
                                                    )}
                                                </Box>
                                            )}

                                            {/* RunbookMaster */}
                                            {agentName === 'RunbookMaster' && (
                                                <Box>
                                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                                        <strong>Decision:</strong>{' '}
                                                        <Chip
                                                            label={agentData.decision}
                                                            size="small"
                                                            color={
                                                                agentData.decision === 'auto_execute' ? 'success' :
                                                                    agentData.decision === 'request_approval' ? 'warning' :
                                                                        'error'
                                                            }
                                                        />
                                                    </Typography>
                                                    {agentData.selected_runbook && (
                                                        <Typography variant="body2">
                                                            <strong>Runbook:</strong> {agentData.selected_runbook}
                                                        </Typography>
                                                    )}
                                                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                                                        {agentData.reason}
                                                    </Typography>
                                                </Box>
                                            )}

                                            {/* ExplainIt */}
                                            {agentName === 'ExplainIt' && (
                                                <Box>
                                                    <Typography variant="body2">
                                                        Generated complete transparency report with decision tree and audit log.
                                                    </Typography>
                                                </Box>
                                            )}
                                        </Paper>
                                    </StepContent>
                                </Step>
                            )
                        })}
                    </Stepper>
                </AccordionDetails>
            </Accordion>

            {/* Final Decision */}
            {decision && (
                <Accordion
                    expanded={expanded === 'decision'}
                    onChange={handleChange('decision')}
                    sx={{ mb: 2, borderRadius: 2, '&:before': { display: 'none' } }}
                >
                    <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <CheckCircle color="success" />
                            <Typography sx={{ fontWeight: 600 }}>Final Decision</Typography>
                        </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Box>
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary' }}>
                                    DECISION TYPE
                                </Typography>
                                <Box sx={{ mt: 0.5 }}>
                                    <Chip
                                        label={decision.decision || 'Unknown'}
                                        color={
                                            decision.decision === 'auto_execute' ? 'success' :
                                                decision.decision === 'request_approval' ? 'warning' :
                                                    'error'
                                        }
                                        sx={{ fontWeight: 600 }}
                                    />
                                </Box>
                            </Box>

                            {decision.selected_runbook && (
                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary' }}>
                                        SELECTED RUNBOOK
                                    </Typography>
                                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                                        {decision.selected_runbook}
                                    </Typography>
                                    {decision.runbook_details && (
                                        <Typography variant="caption" color="text.secondary">
                                            {decision.runbook_details.description}
                                        </Typography>
                                    )}
                                </Box>
                            )}

                            <Box>
                                <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary' }}>
                                    REASON
                                </Typography>
                                <Typography variant="body2" sx={{ mt: 0.5 }}>
                                    {decision.reason || 'No reason provided'}
                                </Typography>
                            </Box>
                        </Box>
                    </AccordionDetails>
                </Accordion>
            )}

            {/* Transparency Report */}
            {transparencyReport && (
                <Accordion
                    expanded={expanded === 'report'}
                    onChange={handleChange('report')}
                    sx={{ borderRadius: 2, '&:before': { display: 'none' } }}
                >
                    <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Info color="info" />
                            <Typography sx={{ fontWeight: 600 }}>Full Transparency Report</Typography>
                        </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                        <List dense>
                            <ListItem>
                                <ListItemText
                                    primary="Report ID"
                                    secondary={transparencyReport.report_id}
                                />
                            </ListItem>
                            <Divider />
                            <ListItem>
                                <ListItemText
                                    primary="Processing Time"
                                    secondary={`${Math.round(transparencyReport.total_processing_time_ms || 0)}ms`}
                                />
                            </ListItem>
                            <Divider />
                            <ListItem>
                                <ListItemText
                                    primary="Agents Involved"
                                    secondary={transparencyReport.agents_involved?.join(', ')}
                                />
                            </ListItem>
                            <Divider />
                            <ListItem>
                                <ListItemText
                                    primary="Automation Level"
                                    secondary={transparencyReport.automation_level}
                                />
                            </ListItem>
                            <Divider />
                            <ListItem>
                                <ListItemText
                                    primary="Timestamp"
                                    secondary={new Date(transparencyReport.timestamp).toLocaleString()}
                                />
                            </ListItem>
                        </List>
                    </AccordionDetails>
                </Accordion>
            )}
        </Box>
    )
}
