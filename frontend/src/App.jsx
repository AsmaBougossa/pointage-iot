import { Routes, Route, Navigate } from 'react-router-dom'
import AppShell from './components/AppShell.jsx'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import LiveFeed from './pages/LiveFeed.jsx'
import Pointages from './pages/Pointages.jsx'
import Employees from './pages/Employees.jsx'
import Cameras from './pages/Cameras.jsx'
import Alerts from './pages/Alerts.jsx'
import Reports from './pages/Reports.jsx'
import TestsAuto from './pages/TestsAuto.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<AppShell />}>
        <Route index element={<Dashboard />} />
        <Route path="flux-direct" element={<LiveFeed />} />
        <Route path="pointages" element={<Pointages />} />
        <Route path="employes" element={<Employees />} />
        <Route path="cameras" element={<Cameras />} />
        <Route path="alertes" element={<Alerts />} />
        <Route path="rapports" element={<Reports />} />
        <Route path="tests" element={<TestsAuto />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
