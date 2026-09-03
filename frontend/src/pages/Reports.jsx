import { useEffect, useState } from 'react'
import Topbar from '../components/Topbar.jsx'
import client from '../api/client.js'

export default function Reports() {
  const [hebdo, setHebdo] = useState([])
  const [departements, setDepartements] = useState([])
  const [stats, setStats] = useState(null)

  useEffect(() => {
    client.get('/dashboard/presence-hebdomadaire').then((r) => setHebdo(r.data))
    client.get('/dashboard/presence-departements').then((r) => setDepartements(r.data))
    client.get('/dashboard/statistiques').then((r) => setStats(r.data))
  }, [])

  return (
    <>
      <Topbar title="Rapports" subtitle="Statistiques de présence et d'assiduité">
        <button className="btn-sm" onClick={() => window.print()}>Exporter (PDF)</button>
      </Topbar>
      <div className="content">
        {stats && (
          <div className="stats">
            <div className="stat">
              <div className="stat-val">{stats.taux_presence}%</div>
              <div className="stat-lbl">Taux de présence global</div>
            </div>
            <div className="stat">
              <div className="stat-val">{stats.total_employes}</div>
              <div className="stat-lbl">Effectif total</div>
            </div>
            <div className="stat">
              <div className="stat-val">{stats.cameras_en_ligne}/{stats.cameras_total}</div>
              <div className="stat-lbl">Caméras opérationnelles</div>
            </div>
          </div>
        )}

        <div className="card" style={{marginBottom:12}}>
          <div className="card-h"><span className="card-title">Tendance hebdomadaire</span></div>
          <div className="chart-area">
            <div className="bars">
              {hebdo.map((jour) => (
                <div className="bar-g" key={jour.date}>
                  <div className="bar-w"><div className="bar" style={{height:`${jour.pourcentage_presence}%`,background:'var(--fill-accent)'}} /></div>
                  <div className="bar-l">{jour.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-h"><span className="card-title">Assiduité par département</span></div>
          {departements.map((d) => (
            <div className="dept-row" key={d.id}>
              <div className="dept-nm">{d.nom}</div>
              <div className="dept-bar"><div className="dept-fill" style={{width:`${d.taux_presence}%`,background:'var(--fill-success)'}} /></div>
              <div className="dept-pct">{d.taux_presence}%</div>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}
