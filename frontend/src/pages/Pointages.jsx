import { useEffect, useState } from 'react'
import Topbar from '../components/Topbar.jsx'
import client from '../api/client.js'

export default function Pointages() {
  const [pointages, setPointages] = useState([])
  const [date, setDate] = useState('')
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)

  function charger() {
    client.get('/pointages', { params: { date: date || undefined, page } }).then((res) => {
      setPointages(res.data.pointages)
      setPages(res.data.pages || 1)
    })
  }

  useEffect(() => { charger() }, [date, page])

  return (
    <>
      <Topbar title="Pointages" subtitle="Historique des entrées / sorties détectées">
        <input
          type="date"
          value={date}
          onChange={(e) => { setDate(e.target.value); setPage(1) }}
          className="btn-sm"
          style={{colorScheme:'dark'}}
        />
      </Topbar>
      <div className="content">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Employé</th>
                <th>Département</th>
                <th>Caméra</th>
                <th>Type</th>
                <th>Heure</th>
                <th>Score</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {pointages.map((p) => (
                <tr key={p.id}>
                  <td style={{color:'var(--text-primary)',fontWeight:500}}>{p.employe?.nom_complet}</td>
                  <td>{p.employe?.departement}</td>
                  <td>{p.camera || '—'}</td>
                  <td>{p.type_evenement === 'entree' ? 'Entrée' : 'Sortie'}</td>
                  <td style={{fontFamily:'var(--font-mono)'}}>{p.heure}</td>
                  <td style={{fontFamily:'var(--font-mono)'}}>{p.score_confiance ? `${p.score_confiance}%` : '—'}</td>
                  <td>
                    <span className="pill" style={{
                      background: p.statut === 'retard' ? 'var(--bg-danger)' : p.statut === 'anticipe' ? 'var(--bg-pro)' : 'var(--bg-success)',
                      color: p.statut === 'retard' ? 'var(--text-danger)' : p.statut === 'anticipe' ? 'var(--text-pro)' : 'var(--text-success)',
                    }}>
                      {p.statut === 'retard' ? 'Retard' : p.statut === 'anticipe' ? 'Anticipé' : 'À l\'heure'}
                    </span>
                  </td>
                </tr>
              ))}
              {pointages.length === 0 && (
                <tr><td colSpan={7}><div className="empty-state">Aucun pointage trouvé</div></td></tr>
              )}
            </tbody>
          </table>
        </div>
        {pages > 1 && (
          <div style={{display:'flex',gap:8,justifyContent:'center',marginTop:14}}>
            <button className="btn-sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Précédent</button>
            <span style={{fontSize:12,color:'var(--text-secondary)',alignSelf:'center'}}>Page {page} / {pages}</span>
            <button className="btn-sm" disabled={page >= pages} onClick={() => setPage((p) => p + 1)}>Suivant</button>
          </div>
        )}
      </div>
    </>
  )
}
