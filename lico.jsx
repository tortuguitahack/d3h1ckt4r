import React, { useEffect, useState } from 'react';
import { Container, Typography, Tabs, Tab, Box, LinearProgress, Grid, Paper } from '@mui/material';
import { Bar, Pie, Doughnut } from 'react-chartjs-2';
import axios from 'axios';

// Configuración datasets ejemplo (ajustar con datos reales)
const ingresosEgresosData = {
  labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
  datasets: [
    {
      label: 'Ingresos',
      data: [45000, 52000, 48000, 56000, 60000, 62000],
      backgroundColor: 'rgba(0, 200, 83, 0.7)'
    },
    {
      label: 'Egresos',
      data: [22000, 19000, 21000, 24000, 23000, 25000],
      backgroundColor: 'rgba(244, 67, 54, 0.7)'
    }
  ]
};

const clienteSegmentosData = {
  labels: ['NUEVO', 'REGULAR', 'VIP'],
  datasets: [
    {
      label: 'Clientes',
      data: [40, 80, 30],
      backgroundColor: ['#FFD700', '#2196f3', '#4caf50']
    }
  ]
};

const pedidosEstadoData = {
  labels: ['Pendiente', 'En Proceso', 'Entregado', 'Cancelado'],
  datasets: [
    {
      label: 'Pedidos',
      data: [10, 15, 55, 5],
      backgroundColor: ['#ff9800', '#03a9f4', '#4caf50', '#f44336']
    }
  ]
};

const inventarioEjemplo = [
  { producto: 'POTOSINA ENTERA', stockActual: 60, stockMinimo: 15 },
  { producto: 'JOHNNIE WALKER BLUE LABEL', stockActual: 5, stockMinimo: 2 },
  { producto: 'MALTITA BOTELLIN', stockActual: 40, stockMinimo: 12 },
];

function TabPanel(props) {
  const { children, value, index } = props;
  return (
    <div hidden={value !== index}>
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function ProgressBar({ value, max }) {
  const percentage = (value / max) * 100;
  let color = 'primary';
  if (percentage <= 25) color = 'error';
  else if (percentage <= 50) color = 'warning';
  else color = 'success';

  return (
    <Box sx={{ width: '100%', mb: 1 }}>
      <Typography variant="body2">{`${value} / ${max}`}</Typography>
      <LinearProgress variant="determinate" value={percentage} color={color} />
    </Box>
  );
}

export default function App() {
  const [tab, setTab] = useState(0);
  // Opcional: Cargar datos reales por API
  // const [datos, setDatos] = useState(null);
  // useEffect(() => {
  //   axios.get('TU_API_O_GOOGLE_SHEETS_ENDPOINT').then(res => {
  //     setDatos(res.data);
  //   });
  // }, []);

  return (
    <Container maxWidth="xl" sx={{ bgcolor: '#121212', minHeight: '100vh', color: 'white', py: 4 }}>
      <Typography variant="h3" gutterBottom textAlign="center" sx={{ fontWeight: 'bold', color: '#0ff' }}>
        Dashboard Licorería Elite
      </Typography>

      <Tabs value={tab} onChange={(e, v) => setTab(v)} centered indicatorColor="secondary" textColor="inherit" sx={{ mb: 4 }}>
        <Tab label="Ingresos / Egresos" />
        <Tab label="Inventario" />
        <Tab label="Clientes" />
        <Tab label="Pedidos" />
        <Tab label="Pagos / Facturación" />
      </Tabs>

      {/* Ingresos / Egresos */}
      <TabPanel value={tab} index={0}>
        <Paper sx={{ p: 3, bgcolor: '#222' }}>
          <Bar data={ingresosEgresosData} options={{
            responsive: true,
            plugins: { legend: { labels: { color: '#0ff' } }, title: { display: true, text: 'Ingresos vs Egresos Mensuales', color: '#0ff' }},
            scales: { x: { ticks: { color: '#0ff' }}, y: { ticks: { color: '#0ff' }}}
          }} />
        </Paper>
      </TabPanel>

      {/* Inventario */}
      <TabPanel value={tab} index={1}>
        <Paper sx={{ p: 3, bgcolor: '#222' }}>
          <Typography variant="h6" gutterBottom>Estado de Inventario</Typography>
          {inventarioEjemplo.map(({ producto, stockActual, stockMinimo }) => (
            <Box key={producto} sx={{ mb: 2 }}>
              <Typography>{producto}</Typography>
              <ProgressBar value={stockActual} max={stockMinimo * 3} />
            </Box>
          ))}
        </Paper>
      </TabPanel>

      {/* Clientes */}
      <TabPanel value={tab} index={2}>
        <Paper sx={{ p: 3, bgcolor: '#222' }}>
          <Typography variant="h6" gutterBottom>Segmentación de Clientes</Typography>
          <Doughnut data={clienteSegmentosData} options={{
            plugins: { legend: { labels: { color: '#0ff' } } }
          }} />
        </Paper>
      </TabPanel>

      {/* Pedidos */}
      <TabPanel value={tab} index={3}>
        <Paper sx={{ p: 3, bgcolor: '#222' }}>
          <Typography variant="h6" gutterBottom>Estado de Pedidos</Typography>
          <Pie data={pedidosEstadoData} options={{
            plugins: { legend: { labels: { color: '#0ff' } } }
          }} />
        </Paper>
      </TabPanel>

      {/* Pagos / Facturación */}
      <TabPanel value={tab} index={4}>
        <Paper sx={{ p: 3, bgcolor: '#222' }}>
          <Typography variant="h6" gutterBottom>Resumen Pagos y Facturación</Typography>
          {/* Aquí podrías incluir un componente para mostrar QR pagos, últimos pagos, etc */}
          <Typography sx={{ mt: 2, color: '#0ff' }}>
            Código QR PayPal (simulación):  
          </Typography>
          <img
            alt="Código QR Pago PayPal"
            src="https://api.qrserver.com/v1/create-qr-code/?data=https://paypal.me/tu_cuenta/1234&size=150x150"
            style={{ marginTop: 10, border: '4px solid #0ff', borderRadius: 8 }}
          />
        </Paper>
      </TabPanel>
    </Container>
  );
}
