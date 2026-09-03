import { useEffect, useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'

const NAV = [
  { section: 'Principal', items: [
    { to: '/', icon: 'ti-layout-dashboard', label: 'Dashboard' },
    { to: '/flux-direct', icon: 'ti-radio', label: 'Flux en direct' },
    { to: '/pointages', icon: 'ti-clipboard-list', label: 'Pointages' },
  ]},
  { section: 'Gestion', items: [
    { to: '/employes', icon: 'ti-users', label: 'Employés' },
    { to: '/cameras', icon: 'ti-camera', label: 'Caméras IoT' },
    { to: '/alertes', icon: 'ti-bell', label: 'Alertes', badgeKey: 'alertes' },
  ]},
  { section: 'Analyse', items: [
    { to: '/rapports', icon: 'ti-chart-bar', label: 'Rapports' },
    { to: '/tests', icon: 'ti-flask', label: 'Tests auto.' },
  ]},
]

export default function AppShell() {
  const [horloge, setHorloge] = useState(new Date())

  useEffect(() => {
    const id = setInterval(() => setHorloge(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="s-logo">
          <div className="s-logo-icon"><i className="ti ti-wifi" style={{fontSize:18,color:'var(--text-accent)'}} /></div>
          <div>
            <div className="s-logo-text">IoT Pointage</div>
            <div className="s-logo-sub">Système intelligent</div>
          </div>
        </div>
        <nav className="s-nav">
          {NAV.map((groupe) => (
            <div key={groupe.section}>
              <div className="s-sec">{groupe.section}</div>
              {groupe.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) => `s-item${isActive ? ' active' : ''}`}
                >
                  <i className={`ti ${item.icon}`} />
                  {item.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <div className="s-foot">
          <div style={{fontSize:11,color:'var(--text-secondary)'}}><span className="dot-green" />Serveur actif</div>
          <div style={{fontSize:10,color:'var(--text-muted)',marginTop:2,fontFamily:'var(--font-mono)'}}>localhost:5000</div>
        </div>
      </aside>

      <main className="main">
        <Outlet context={{ horloge }} />
      </main>
    </div>
  )
}
