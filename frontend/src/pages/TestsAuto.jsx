import { useEffect, useState } from 'react'
import Topbar from '../components/Topbar.jsx'
import client from '../api/client.js'

export default function TestsAuto() {
  const [historique, setHistorique] = useState([])
  const [enCours, setEnCours] = useState(false)
  const [derniereSortie, setDerniereSortie] = useState('')

  function charger() {
    client.get('/tests/historique').then((res) => setHistorique(res.data))
  }
  useEffect(() => { charger() }, [])

  async function lancerTests() {
    setEnCours(true)
    try {
      const res = await client.post('/tests/executer')
      setDerniereSortie(res.data.sortie_brute)
      charger()
    } finally {
      setEnCours(false)
    }
  }

  return (
    <>
      <Topbar title="Tests automatisés" subtitle="Stratégie de test pytest — validation continue du système">
        <button className="btn-sm btn-acc" onClick={lancerTests} disabled={enCours}>
          {enCours ? 'Exécution...' : 'Lancer la suite pytest'}
        </button>
      </Topbar>
      <div className="content">
        <div className="table-wrap" style={{marginBottom:12}}>
          <table>
            <thead>
              <tr><th>Suite</th><th>Total</th><th>Réussis</th><th>Échoués</th><th>Taux</th><th>Durée</th><th>Date</th></tr>
            </thead>
            <tbody>
              {historique.map((r) => (
                <tr key={r.id}>
                  <td style={{color:'var(--text-primary)'}}>{r.nom_suite}</td>
                  <td>{r.nb_total}</td>
                  <td style={{color:'var(--text-success)'}}>{r.nb_reussis}</td>
                  <td style={{color:'var(--text-danger)'}}>{r.nb_echoues}</td>
                  <td>
                    <span className="pill" style={{background: r.taux_reussite === 100 ? 'var(--bg-success)' : 'var(--bg-danger)', color: r.taux_reussite === 100 ? 'var(--text-success)' : 'var(--text-danger)'}}>
                      {r.taux_reussite}%
                    </span>
                  </td>
                  <td style={{fontFamily:'var(--font-mono)'}}>{r.duree_secondes}s</td>
                  <td>{new Date(r.date_execution).toLocaleString('fr-FR')}</td>
                </tr>
              ))}
              {historique.length === 0 && <tr><td colSpan={7}><div className="empty-state">Aucune exécution — lancez la suite pytest</div></td></tr>}
            </tbody>
          </table>
        </div>

        {derniereSortie && (
          <div className="card">
            <div className="card-h"><span className="card-title">Sortie de la dernière exécution</span></div>
            <pre style={{padding:16,fontSize:11,color:'var(--text-secondary)',fontFamily:'var(--font-mono)',whiteSpace:'pre-wrap',maxHeight:300,overflow:'auto'}}>
              {derniereSortie}
            </pre>
          </div>
        )}
      </div>
    </>
  )
}
