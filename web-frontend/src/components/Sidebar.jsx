import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Drawer, List, ListItem, ListItemText, ListItemIcon, Toolbar, Avatar, Box, Typography, Divider, Collapse, useTheme, useMediaQuery, Tooltip, IconButton
} from '@mui/material';
import {
  Dashboard as DashboardIcon, Chat as ChatIcon, BarChart as MetricsIcon, Map as MapIcon,
  BugReport, Build, Hub as WorkflowIcon, ExpandLess, ExpandMore, SmartToy, MenuBook,
  Menu as MenuIcon
} from '@mui/icons-material';
import { AGENTS, RUNBOOKS } from '../mockData';

const drawerWidth = 280;
const miniDrawerWidth = 72;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Workflow',  icon: <WorkflowIcon />, path: '/workflow' },
  { text: 'Metrics', icon: <MetricsIcon />, path: '/metrics' },
  { text: 'Map', icon: <MapIcon />, path: '/map' }
];

export default function Sidebar({ mobileOpen, handleDrawerToggle }) {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [expandAgents, setExpandAgents] = useState(true);
  const [expandRunbooks, setExpandRunbooks] = useState(false);

  const handleItemClick = (path) => {
    navigate(path);
    if (isMobile) {
      handleDrawerToggle();
    }
  };

  const drawer = (
    <>
      <Toolbar sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative', minHeight: 64 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box sx={{ fontSize: '1.9rem', fontWeight: 'bold' }}>🌿</Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, color: 'white' }}>AgriFlow AI</Typography>
            {!isMobile && (
              <Typography variant="caption" sx={{ letterSpacing: '0.05em', color: 'text.secondary' }}>
                Intelligent Farm
              </Typography>
            )}
          </Box>
        </Box>
        {mobileOpen && (
          <IconButton
            aria-label="Close navigation menu"
            onClick={handleDrawerToggle}
            sx={{ color: 'white', position: 'absolute', top: 12, right: 12, zIndex: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}
      </Toolbar>
      {/* Hamburger to close the sidebar */}
      {mobileOpen && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', px: 2, pt: 1 }}>
          <IconButton
            aria-label="Close navigation menu"
            onClick={handleDrawerToggle}
            sx={{ color: 'white', position: 'absolute', top: 12, right: 12, zIndex: 2 }}
          >
            <MenuIcon />
          </IconButton>
        </Box>
      )}
      {/* Header do Sidebar */}
      <List sx={{ px: 1 }} role="navigation" aria-label="Main menu">
        {menuItems.map((item) => (
          <Tooltip key={item.text} title={item.text} placement="right" arrow>
            <ListItem 
              button 
              onClick={() => handleItemClick(item.path)}
              sx={{
                borderRadius: '8px',
                mb: 0.5,
                justifyContent: mobileOpen ? 'flex-start' : 'center',
                px: mobileOpen ? 2 : 0,
                '&:hover': { 
                  backgroundColor: 'sidebar.hover'
                },
                transition: 'all 0.2s ease'
              }}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: mobileOpen ? 40 : 'auto', justifyContent: 'center' }}>{item.icon}</ListItemIcon>
              {mobileOpen && (
                <ListItemText 
                  primary={item.text} 
                  primaryTypographyProps={{ sx: { fontWeight: 500, fontSize: '0.875rem', color: 'white' } }}
                />
              )}
            </ListItem>
          </Tooltip>
        ))}
      </List>

      {mobileOpen && (
        <>
          <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
          
          {/* Seção de Agentes */}
          <List sx={{ px: 1 }}>
            <ListItem 
              button 
              onClick={() => setExpandAgents(!expandAgents)}
              sx={{ borderRadius: '8px', mb: 0.5, '&:hover': { backgroundColor: 'sidebar.hover' } }}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                <SmartToy />
              </ListItemIcon>
              <ListItemText 
                primary="Agents" 
                primaryTypographyProps={{ sx: { fontWeight: 600, fontSize: '0.875rem', color: "white" } }}
              />
              {expandAgents ? <ExpandLess sx={{ fontSize: '1.2rem', color: "white" }} /> : <ExpandMore sx={{ fontSize: '1.2rem', color: "white" }} />}
            </ListItem>
            
            <Collapse in={expandAgents} timeout="auto" unmountOnExit>
              {AGENTS.map(a => (
                <ListItem key={a.id} sx={{ pl: 4, py: 0.75 }}>
                  <Avatar sx={{ mr: 1.5, width: 28, height: 28, fontSize: '0.75rem', bgcolor: 'secondary.main' }}>
                    {a.name[0]}
                  </Avatar>
                  <ListItemText 
                    primary={a.name} 
                    secondary={a.role}
                    primaryTypographyProps={{ sx: { fontSize: '0.8rem', fontWeight: 500, color: 'inherit' } }}
                    secondaryTypographyProps={{ sx: { fontSize: '0.7rem', color: 'rgba(255,255,255,0.6)' } }}
                  />
                </ListItem>
              ))}
            </Collapse>
          </List>

          <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
          
          {/* Seção de Runbooks */}
          <List sx={{ px: 1 }}>
            <ListItem 
              button 
              onClick={() => setExpandRunbooks(!expandRunbooks)}
              sx={{ borderRadius: '8px', mb: 0.5, '&:hover': { backgroundColor: 'sidebar.hover' } }}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                <MenuBook />
              </ListItemIcon>
              <ListItemText 
                primary="Runbooks" 
                primaryTypographyProps={{ sx: { fontWeight: 600, fontSize: '0.875rem', color: "white" } }}
              />
              {expandRunbooks ? <ExpandLess sx={{ fontSize: '1.2rem' }} /> : <ExpandMore sx={{ fontSize: '1.2rem' }} />}
            </ListItem>
            
            <Collapse in={expandRunbooks} timeout="auto" unmountOnExit>
              {RUNBOOKS.map(r => (
                <ListItem key={r.id} sx={{ pl: 4, py: 0.75 }}>
                  <ListItemIcon sx={{ color: r.safe ? 'success.main' : 'warning.main', minWidth: 32 }}>
                    {r.safe ? <BugReport fontSize="small" /> : <Build fontSize="small" />}
                  </ListItemIcon>
                  <ListItemText 
                    primary={r.name}
                    secondary={r.safe ? '✓ Safe' : '⚠ Critical'}
                    primaryTypographyProps={{ sx: { fontSize: '0.8rem', fontWeight: 500, color: 'inherit' } }}
                    secondaryTypographyProps={{ sx: { fontSize: '0.7rem', color: 'rgba(255,255,255,0.6)' } }}
                  />
                </ListItem>
              ))}
            </Collapse>
          </List>
        </>
      )}

      {!mobileOpen && (
        <>
          <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
          
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
            <Tooltip title="Agents" placement="right" arrow>
              <IconButton sx={{ color: 'white' }}>
                <SmartToy />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Runbooks" placement="right" arrow>
              <IconButton sx={{ color: 'white' }}>
                <MenuBook />
              </IconButton>
            </Tooltip>
          </Box>
        </>
      )}
    </>
  );

  return (
    <Box component="nav">
      <Drawer
        variant={mobileOpen ? "permanent" : "temporary"}
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          width: mobileOpen ? drawerWidth : miniDrawerWidth,
          flexShrink: 0,
          zIndex: theme.zIndex.appBar - 1, // Abaixo do AppBar
          '& .MuiDrawer-paper': { 
            width: mobileOpen ? drawerWidth : miniDrawerWidth,
            boxSizing: 'border-box',
            transition: 'width 0.2s ease',
            overflowX: 'hidden'
          },
        }}
      >
        {drawer}
      </Drawer>
    </Box>
  );
}