import React, { useEffect, useRef } from 'react'
import {
  Box, Card, CardContent, Typography, Grid, Chip
} from '@mui/material'
import { LocationOn } from '@mui/icons-material'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { TALHOES } from '../mockData'

// Fix for default markers in Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

export default function MapView() {
  const mapRef = useRef(null)
  const mapInstance = useRef(null)

  useEffect(() => {
    if (mapRef.current && !mapInstance.current) {
      // Initialize map centered on Brazil (approx. -15, -55)
      mapInstance.current = L.map(mapRef.current).setView([-15, -55], 5)

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapInstance.current)

      // Add markers for plots
      TALHOES.forEach(talhao => {
        const marker = L.marker([talhao.lat, talhao.lng]).addTo(mapInstance.current)
        marker.bindPopup(`
          <b>${talhao.id}</b><br>
          Crop: ${talhao.crop}<br>
          Status: ${talhao.status}
        `)
      })
    }

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove()
        mapInstance.current = null
      }
    }
  }, [])

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
          🗺️ Plot Map
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Visualize plots and their current status
        </Typography>
      </Box>
      <Grid container spacing={{ xs: 2, md: 3 }} direction="column">
        <Grid item xs={12} lg={8}>
          <Card sx={{
            border: `1px solid #e0e0e0`,
            background: 'linear-gradient(135deg, rgba(95,167,119,0.08) 0%, rgba(44,95,111,0.06) 100%)',
            boxShadow: '0 8px 24px rgba(44, 95, 111, 0.08)'
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#1b5e20' }}>
                Interactive Map with Leaflet
              </Typography>
              <Box
                ref={mapRef}
                sx={{
                  height: { xs: 350, sm: 450, md: 550, lg: 600 },
                  width: '100%',
                  borderRadius: 3,
                  border: '2px solid rgba(27, 94, 32, 0.2)',
                  overflow: 'hidden'
                }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={3} lg={4}>
          <Card sx={{
            background: 'linear-gradient(135deg, #ffffff 0%, #f1f8e9 100%)',
            boxShadow: '0 8px 24px rgba(44, 95, 111, 0.08)',
            border: '1px solid #e0e0e0',
            height: 'fit-content'
          }}>
            <CardContent sx={{ p: { xs: 2, sm: 3 }}}>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, color: '#1b5e20', fontSize: { xs: '1.25rem', sm: '1.5rem' } }}>
                ⚠️ Active Alerts
              </Typography>
              <Box sx={{ maxHeight: { xs: 300, sm: 400, md: 500 }, overflowY: 'auto' }}>
                <Grid container spacing={2}>
                  {TALHOES.map(t => {
                    const statusConfig = {
                      'Normal': { icon: '✅', color: '#2e7d32', bg: '#c8e6c9' },
                      'Pest Alert': { icon: '🚨', color: '#f57c00', bg: '#ffe0b2' },
                      'Maintenance': { icon: '⚙️', color: '#0277bd', bg: '#b3e5fc' }
                    };
                    const config = statusConfig[t.status] || statusConfig['Normal'];
                    return (
                      <Grid item xs={12} key={t.id}>
                        <Card sx={{
                          background: 'linear-gradient(135deg, #fff 0%, #f8fbf9 100%)',
                          boxShadow: '0 4px 12px rgba(44, 95, 111, 0.08)',
                          border: '2px solid #e0e0e0',
                          transition: 'all 0.2s ease',
                          '&:hover': { boxShadow: '0 8px 24px rgba(44, 95, 111, 0.12)', transform: 'translateY(-2px)' }
                        }}>
                          <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 2, px: 2 }}>
                            <Box sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              width: 44,
                              height: 44,
                              borderRadius: '50%',
                              background: config.bg,
                              color: config.color,
                              fontSize: '1.5rem',
                              fontWeight: 700
                            }}>{config.icon}</Box>
                            <Box sx={{ flex: 1, minWidth: 0 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: config.color, fontSize: '1.05rem' }}>
                                {t.id}
                              </Typography>
                              <Typography variant="body2" sx={{ fontWeight: 500, color: 'text.secondary', fontSize: '0.9rem', mt: 0.5 }}>
                                🌱 {t.crop}
                              </Typography>
                            </Box>
                            <Chip
                              label={t.status}
                              size="small"
                              sx={{ fontWeight: 600, fontSize: '0.8rem', background: config.bg, color: config.color, px: 1.5, borderRadius: 2 }}
                            />
                          </CardContent>
                        </Card>
                      </Grid>
                    );
                  })}
                </Grid>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}