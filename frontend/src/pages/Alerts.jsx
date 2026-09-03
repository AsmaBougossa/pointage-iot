import { useEffect, useState } from 'react'
import Topbar from '../components/Topbar.jsx'
import client from '../api/client.js'

const ICONES = {
  absence_non_justifiee: 'ti-user-x',
  retard_repete: 'ti-clock-exclamation',
  camera_hors_ligne: 'ti-camera-off',
  visage_inconnu: 'ti-face-id-error',
  doublon_pointage: 'ti-copy',
}

export default function Alerts() {
  const [alertes, setAlertes] = useState([])

  useEffect(() => {
    client.get('/dashboard/alertes').then((res) => setAlertes(res.data))
  }, [])

  return (
    <>
      <Topbar title="Alertes" subtitle="Événements nécessitant une attention" />
      <div className="content">
        <div className="card">
          <div className="feed">
            {alertes.map((a) => (
              <div className="feed-item" key={a.id}>
                <div className="av" style={{
                  background: a.gravite === 'critique' ? 'var(--bg-danger)' : a.gravite === 'warning' ? 'var(--bg-pro)' : 'var(--bg-accent)',
                  color: a.gravite === 'critique' ? 'var(--text-danger)' : a.gravite === 'warning' ? 'var(--text-pro)' : 'var(--text-accent)',
                }}>
                  <i className={`ti ${ICONES[a.type_alerte] || 'ti-bell'}`} style={{fontSize:15}} />
                </div>
                <div style={{flex:1}}>
                  <div className="f-name">{a.message}</div>
                  <div className="f-dept">{a.type_alerte.replaceAll('_',' ')}</div>
                </div>
                <div className="f-time">
                  <div>{new Date(a.date_creation).toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'})}</div>
                  {!a.lue && <div className="f-ev" style={{color:'var(--text-danger)'}}>Non lue</div>}
                </div>
              </div>
            ))}
            {alertes.length === 0 && <div className="empty-state">Aucune alerte — tout est normal</div>}
          </div>
        </div>
      </div>
    </>
  )
}
