import React, { useState, useEffect, useRef } from 'react'
import {
    Box,
    Card,
    CardContent,
    Typography,
    TextField,
    IconButton,
    Avatar,
    Chip,
    List,
    ListItem,
    Paper,
    CircularProgress,
    Divider
} from '@mui/material'
import { Send, SmartToy, Person, CheckCircle, HourglassEmpty } from '@mui/icons-material'

/**
 * ACS Chat Component
 * 
 * Real-time chat interface for Azure Communication Services
 * Displays agent processing flow and transparency
 */
export default function ACSChat({ threadId, onClose }) {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [agentProcessing, setAgentProcessing] = useState(null)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    // Mock initial messages
    useEffect(() => {
        setMessages([
            {
                id: '1',
                sender: 'bot',
                text: 'Olá! Sou o assistente AgriFlow AI. Como posso ajudar você hoje?',
                timestamp: new Date(),
                agentInfo: {
                    agent: 'System',
                    confidence: 1.0
                }
            }
        ])
    }, [])

    const handleSend = async () => {
        if (!input.trim()) return

        const userMessage = {
            id: Date.now().toString(),
            sender: 'user',
            text: input,
            timestamp: new Date()
        }

        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)

        try {
            // Call agents API
            const response = await fetch('/api/agents/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    user_id: 'web-user',
                    metadata: { channel: 'web', thread_id: threadId }
                })
            })

            const result = await response.json()

            if (result.success) {
                // Show agent processing
                setAgentProcessing(result.agent_history)

                // Add bot response
                const botMessage = {
                    id: (Date.now() + 1).toString(),
                    sender: 'bot',
                    text: result.explanation,
                    timestamp: new Date(),
                    agentInfo: {
                        agents: result.agent_history.map(h => h.agent_name),
                        decision: result.decision,
                        recommendations: result.recommendations,
                        processingTime: result.processing_time_ms
                    }
                }

                setTimeout(() => {
                    setMessages(prev => [...prev, botMessage])
                    setAgentProcessing(null)
                    setLoading(false)
                }, 1000)
            } else {
                throw new Error(result.error || 'Unknown error')
            }
        } catch (error) {
            console.error('Error sending message:', error)
            const errorMessage = {
                id: (Date.now() + 1).toString(),
                sender: 'bot',
                text: 'Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.',
                timestamp: new Date(),
                isError: true
            }
            setMessages(prev => [...prev, errorMessage])
            setLoading(false)
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <Card sx={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            background: 'linear-gradient(135deg, #ffffff 0%, #f1f8e9 100%)'
        }}>
            <CardContent sx={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                p: 0,
                '&:last-child': { pb: 0 }
            }}>
                {/* Header */}
                <Box sx={{
                    p: 2,
                    borderBottom: '2px solid rgba(27, 94, 32, 0.1)',
                    background: 'rgba(255, 255, 255, 0.8)'
                }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Avatar sx={{ bgcolor: '#2e7d32', width: 40, height: 40 }}>
                            <SmartToy />
                        </Avatar>
                        <Box>
                            <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1.1rem' }}>
                                AgriFlow AI Assistant
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                                Powered by Multi-Agent System
                            </Typography>
                        </Box>
                    </Box>
                </Box>

                {/* Messages */}
                <Box sx={{
                    flex: 1,
                    overflowY: 'auto',
                    p: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2
                }}>
                    {messages.map((message) => (
                        <Box
                            key={message.id}
                            sx={{
                                display: 'flex',
                                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                                gap: 1
                            }}
                        >
                            {message.sender === 'bot' && (
                                <Avatar sx={{ bgcolor: '#2e7d32', width: 32, height: 32 }}>
                                    <SmartToy sx={{ fontSize: '1rem' }} />
                                </Avatar>
                            )}

                            <Box sx={{ maxWidth: '75%' }}>
                                <Paper
                                    elevation={0}
                                    sx={{
                                        p: 1.5,
                                        bgcolor: message.sender === 'user'
                                            ? '#2e7d32'
                                            : message.isError
                                                ? '#ffebee'
                                                : '#f5f5f5',
                                        color: message.sender === 'user' ? '#fff' : '#000',
                                        borderRadius: 2,
                                        border: message.isError ? '1px solid #ef5350' : 'none'
                                    }}
                                >
                                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                        {message.text}
                                    </Typography>

                                    {/* Agent Info */}
                                    {message.agentInfo && message.sender === 'bot' && !message.isError && (
                                        <Box sx={{ mt: 1.5, pt: 1.5, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                                            <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 0.5 }}>
                                                🤖 Agents Involved:
                                            </Typography>
                                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                                {message.agentInfo.agents?.map((agent, i) => (
                                                    <Chip
                                                        key={i}
                                                        label={agent}
                                                        size="small"
                                                        sx={{ fontSize: '0.7rem', height: 20 }}
                                                    />
                                                ))}
                                            </Box>
                                            {message.agentInfo.processingTime && (
                                                <Typography variant="caption" sx={{ display: 'block', mt: 0.5, color: 'text.secondary' }}>
                                                    ⚡ Processed in {Math.round(message.agentInfo.processingTime)}ms
                                                </Typography>
                                            )}
                                        </Box>
                                    )}
                                </Paper>

                                <Typography variant="caption" sx={{ display: 'block', mt: 0.5, px: 1, color: 'text.secondary' }}>
                                    {message.timestamp.toLocaleTimeString()}
                                </Typography>
                            </Box>

                            {message.sender === 'user' && (
                                <Avatar sx={{ bgcolor: '#1976d2', width: 32, height: 32 }}>
                                    <Person sx={{ fontSize: '1rem' }} />
                                </Avatar>
                            )}
                        </Box>
                    ))}

                    {/* Agent Processing Indicator */}
                    {agentProcessing && (
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
                            <Avatar sx={{ bgcolor: '#2e7d32', width: 32, height: 32 }}>
                                <SmartToy sx={{ fontSize: '1rem' }} />
                            </Avatar>
                            <Paper
                                elevation={0}
                                sx={{
                                    p: 1.5,
                                    bgcolor: '#f5f5f5',
                                    borderRadius: 2,
                                    maxWidth: '75%'
                                }}
                            >
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <CircularProgress size={16} />
                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                        Processing...
                                    </Typography>
                                </Box>
                                <List dense sx={{ p: 0 }}>
                                    {agentProcessing.map((agent, i) => (
                                        <ListItem key={i} sx={{ px: 0, py: 0.5 }}>
                                            <CheckCircle sx={{ fontSize: '1rem', color: '#2e7d32', mr: 1 }} />
                                            <Typography variant="caption">
                                                {agent.agent_name}
                                            </Typography>
                                        </ListItem>
                                    ))}
                                </List>
                            </Paper>
                        </Box>
                    )}

                    {loading && !agentProcessing && (
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                            <Avatar sx={{ bgcolor: '#2e7d32', width: 32, height: 32 }}>
                                <SmartToy sx={{ fontSize: '1rem' }} />
                            </Avatar>
                            <Paper
                                elevation={0}
                                sx={{
                                    p: 1.5,
                                    bgcolor: '#f5f5f5',
                                    borderRadius: 2
                                }}
                            >
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <CircularProgress size={16} />
                                    <Typography variant="body2">Typing...</Typography>
                                </Box>
                            </Paper>
                        </Box>
                    )}

                    <div ref={messagesEndRef} />
                </Box>

                {/* Input */}
                <Box sx={{
                    p: 2,
                    borderTop: '2px solid rgba(27, 94, 32, 0.1)',
                    background: 'rgba(255, 255, 255, 0.8)'
                }}>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                        <TextField
                            fullWidth
                            multiline
                            maxRows={3}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Type your message..."
                            disabled={loading}
                            size="small"
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    borderRadius: 2,
                                    bgcolor: '#fff'
                                }
                            }}
                        />
                        <IconButton
                            onClick={handleSend}
                            disabled={loading || !input.trim()}
                            sx={{
                                bgcolor: '#2e7d32',
                                color: '#fff',
                                '&:hover': { bgcolor: '#1b5e20' },
                                '&:disabled': { bgcolor: '#e0e0e0' }
                            }}
                        >
                            <Send />
                        </IconButton>
                    </Box>
                </Box>
            </CardContent>
        </Card>
    )
}
