import { useEffect, useState } from 'react'
import Topbar from '../components/Topbar.jsx'
import client from '../api/client.js'

const COULEURS_AVATAR = ['success', 'accent', 'danger', 'pro']

function couleurPour(nom) {
  let somme = 0
  for (const c of nom) somme += c.charCodeAt(0)
  return COULEURS_AVATAR[somme % COULEURS_AVATAR.length]
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [activite, setActivite] = useState([])
  const [hebdo, setHebdo] = useState([])
  const [departements, setDepartements] = useState([])
  const [simulationEnCours, setSimulationEnCours] = useState(false)

  async function chargerDonnees() {
    const [s, a, h, d] = await Promise.all([
      client.get('/dashboard/statistiques'),
      client.get('/dashboard/activite-recente'),
      client.get('/dashboard/presence-hebdomadaire'),
      client.get('/dashboard/presence-departements'),
    ])
    setStats(s.data)
    setActivite(a.data)
    setHebdo(h.data)
    setDepartements(d.data)
  }

  useEffect(() => { chargerDonnees() }, [])

  async function simuler() {
    setSimulationEnCours(true)
    try {
      await client.post('/reconnaissance/simuler')
      await chargerDonnees()
    } finally {
      setSimulationEnCours(false)
    }
  }

  return (
    <>
      <Topbar title="Dashboard" subtitle="Vue d'ensemble du système de pointage IoT">
        <button className="btn-sm" onClick={simuler} disabled={simulationEnCours}>
          {simulationEnCours ? 'Analyse...' : 'Simuler reconnaissance'}
        </button>
        <button className="btn-sm btn-acc" onClick={() => (window.location.href = '/employes')}>+ Employé</button>
      </Topbar>

      <div className="content">
        {stats && (
          <div className="stats">
            <div className="stat">
              <div className="stat-top">
                <div className="stat-icon" style={{background:'var(--bg-accent)'}}><i className="ti ti-users" style={{color:'var(--text-accent)',fontSize:17}} /></div>
                <span className="stat-badge" style={{background:'var(--bg-accent)',color:'var(--text-accent)'}}>Total</span>
              </div>
              <div className="stat-val">{stats.total_employes}</div>
              <div className="stat-lbl">Employés enregistrés</div>
            </div>
            <div className="stat">
              <div className="stat-top">
                <div className="stat-icon" style={{background:'var(--bg-success)'}}><i className="ti ti-check" style={{color:'var(--text-success)',fontSize:17}} /></div>
                <span className="stat-badge" style={{background:'var(--bg-success)',color:'var(--text-success)'}}>{stats.taux_presence}%</span>
              </div>
              <div className="stat-val">{stats.presents_aujourdhui}</div>
              <div className="stat-lbl">Présents aujourd'hui</div>
            </div>
            <div className="stat">
              <div className="stat-top">
                <div className="stat-icon" style={{background:'var(--bg-danger)'}}><i className="ti ti-x" style={{color:'var(--text-danger)',fontSize:17}} /></div>
                <span className="stat-badge" style={{background:'var(--bg-danger)',color:'var(--text-danger)'}}>Aujourd'hui</span>
              </div>
              <div className="stat-val">{stats.absents_aujourdhui}</div>
              <div className="stat-lbl">Absents</div>
            </div>
            <div className="stat">
              <div className="stat-top">
                <div className="stat-icon" style={{background:'var(--bg-pro)'}}><i className="ti ti-camera" style={{color:'var(--text-pro)',fontSize:17}} /></div>
                <span className="stat-badge" style={{background:'var(--bg-pro)',color:'var(--text-pro)'}}>/ {stats.cameras_total}</span>
              </div>
              <div className="stat-val">{stats.cameras_en_ligne}</div>
              <div className="stat-lbl">Caméras en ligne</div>
            </div>
          </div>
        )}

        <div className="grid2">
          <div className="card">
            <div className="card-h">
              <span className="card-title">Activité récente</span>
              <div style={{display:'flex',alignItems:'center',gap:5,fontSize:10,color:'var(--text-success)'}}><div className="live-dot" />LIVE</div>
            </div>
            <div className="feed">
              {activite.length === 0 && <div className="empty-state">Aucun pointage pour le moment</div>}
              {activite.map((p) => {
                const couleur = p.employe ? couleurPour(p.employe.nom) : 'danger'
                return (
                  <div className="feed-item" key={p.id}>
                    <div className="av" style={{background:`var(--bg-${couleur})`,color:`var(--text-${couleur})`}}>{p.employe?.initiales}</div>
                    <div style={{flex:1}}>
                      <div className="f-name">{p.employe?.nom_complet}</div>
                      <div className="f-dept">{p.employe?.departement} · {p.camera || '—'}</div>
                    </div>
                    <div className="f-time">
                      <div>{p.heure}</div>
                      <div className="f-ev" style={{color: p.statut === 'retard' ? 'var(--text-danger)' : 'var(--text-success)'}}>
                        {p.type_evenement === 'entree' ? 'Entrée' : 'Sortie'} {p.score_confiance}%
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          <div className="card">
            <div className="card-h">
              <span className="card-title">Présence 7 derniers jours</span>
              <select style={{fontSize:11,padding:'3px 6px',background:'var(--surface-0)',border:'0.5px solid var(--border)',borderRadius:'var(--radius)',color:'var(--text-secondary)'}}>
                <option>7 jours</option>
              </select>
            </div>
            <div className="chart-area">
              <div className="bars">
                {hebdo.map((jour) => (
                  <div className="bar-g" key={jour.date}>
                    <div className="bar-w">
                      <div className="bar" style={{height:`${jour.pourcentage_presence}%`,background:'var(--fill-accent)',opacity:.8}} />
                      <div className="bar" style={{height:`${100 - jour.pourcentage_presence}%`,background:'var(--bg-danger)'}} />
                    </div>
                    <div className="bar-l">{jour.label}</div>
                  </div>
                ))}
              </div>
              <div style={{display:'flex',gap:14,justifyContent:'center',fontSize:10,color:'var(--text-muted)'}}>
                <span style={{display:'flex',alignItems:'center',gap:4}}><span style={{width:10,height:8,background:'var(--fill-accent)',borderRadius:2,display:'inline-block'}} />Présents</span>
                <span style={{display:'flex',alignItems:'center',gap:4}}><span style={{width:10,height:8,background:'var(--bg-danger)',borderRadius:2,display:'inline-block'}} />Absents</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-h"><span className="card-title">Présence par département</span></div>
          {departements.map((d) => (
            <div className="dept-row" key={d.id}>
              <div className="dept-nm">{d.nom}</div>
              <div className="dept-bar"><div className="dept-fill" style={{width:`${d.taux_presence}%`,background:'var(--fill-accent)'}} /></div>
              <div className="dept-pct">{d.taux_presence}%</div>
              <div style={{fontSize:10,color:'var(--text-muted)',width:50,textAlign:'right'}}>{d.presents_aujourdhui}/{d.effectif_total}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}
