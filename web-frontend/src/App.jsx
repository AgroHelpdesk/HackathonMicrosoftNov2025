import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { AuthenticatedTemplate, UnauthenticatedTemplate, useMsal } from "@azure/msal-react"
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Avatar,
  useTheme as useMuiTheme,
  useMediaQuery,
  Container,
  Paper
} from '@mui/material'
import { Menu as MenuIcon } from '@mui/icons-material'
import Dashboard from './components/Dashboard'
import Chat from './components/Chat'
import Metrics from './components/Metrics'
import MapView from './components/MapView'
import AgentWorkflow from './components/AgentWorkflow'
import Sidebar from './components/Sidebar'
import { SignInButton } from './components/Auth/SignInButton'
import { SignOutButton } from './components/Auth/SignOutButton'
import theme from './theme/theme'

function AppShell() {
  const muiTheme = useMuiTheme()
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('md'))
  const [mobileOpen, setMobileOpen] = useState(false)
  const { accounts } = useMsal()

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  return (
    <Router>
      <Box sx={{ display: 'flex', minHeight: '100vh', background: 'linear-gradient(180deg, #f7f9fc 0%, #eef2f7 100%)' }}>
        <AppBar position="fixed" color="transparent" elevation={0} sx={{ borderBottom: '1px solid rgba(44, 62, 80, 0.1)' }}>
          <Toolbar sx={{ py: 1.5, px: { xs: 2, md: 3 } }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Box sx={{ fontSize: '1.9rem', fontWeight: 'bold' }}>🌿</Box>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>AgriFlow AI</Typography>
                {!isMobile && (
                  <Typography variant="caption" sx={{ letterSpacing: '0.05em', color: 'text.secondary' }}>
                    Intelligent Farm
                  </Typography>
                )}
              </Box>
            </Box>
            <Box sx={{ flexGrow: 1 }} />
            {!isMobile && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box>
                  <Typography variant="caption" sx={{ textTransform: 'uppercase', color: 'text.secondary' }}>
                    Location
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>Hangemot</Typography>
                </Box>
                <Box sx={{ width: 1, height: 32, bgcolor: 'divider', borderRadius: 1 }} />
                <Box>
                  <Typography variant="caption" sx={{ textTransform: 'uppercase', color: 'text.secondary' }}>
                    User
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {accounts[0] ? accounts[0].name : 'User'}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main', width: 40, height: 40, fontWeight: 600 }}>
                  {accounts[0] ? accounts[0].name.charAt(0) : 'U'}
                </Avatar>
                <SignOutButton />
              </Box>
            )}
          </Toolbar>
        </AppBar>
        <Sidebar mobileOpen={mobileOpen} handleDrawerToggle={handleDrawerToggle} />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            px: { xs: 2, md: 4 },
            py: { xs: 2, md: 4 },
            position: 'relative'
          }}
        >
          <Toolbar />
          <Box
            sx={{
              maxWidth: '1400px',
              mx: 'auto',
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              gap: { xs: 2, md: 3 }
            }}
          >
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/chat/:ticketId" element={<Chat />} />
              <Route path="/metrics" element={<Metrics />} />
              <Route path="/map" element={<MapView />} />
              <Route path="/workflow" element={<AgentWorkflow />} />
            </Routes>
          </Box>
        </Box>
      </Box>
    </Router>
  )
}

function LoginScreen() {
  return (
    <Box sx={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
    }}>
      <Container maxWidth="sm">
        <Paper elevation={3} sx={{ p: 4, textAlign: 'center', borderRadius: 2 }}>
          <Box sx={{ fontSize: '4rem', mb: 2 }}>🌿</Box>
          <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
            AgriFlow AI
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph sx={{ mb: 4 }}>
            Intelligent Farm Management System
          </Typography>
          <SignInButton />
        </Paper>
      </Container>
    </Box>
  )
}

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthenticatedTemplate>
        <AppShell />
      </AuthenticatedTemplate>
      <UnauthenticatedTemplate>
        <LoginScreen />
      </UnauthenticatedTemplate>
    </ThemeProvider>
  )
}
