import { useEffect, useRef, useState } from 'react'
import Topbar from '../components/Topbar.jsx'
import client from '../api/client.js'

const VIDE = { nom:'', prenom:'', email:'', telephone:'', poste:'', id_departement:'' }

export default function Employees() {
  const [employes, setEmployes] = useState([])
  const [departements, setDepartements] = useState([])
  const [modalOuvert, setModalOuvert] = useState(false)
  const [form, setForm] = useState(VIDE)
  const [photoBase64, setPhotoBase64] = useState(null)
  const fileRef = useRef(null)

  function charger() {
    client.get('/employes').then((res) => setEmployes(res.data))
    client.get('/dashboard/presence-departements').then((res) => setDepartements(res.data))
  }
  useEffect(() => { charger() }, [])

  function onPhotoChange(e) {
    const fichier = e.target.files[0]
    if (!fichier) return
    const lecteur = new FileReader()
    lecteur.onload = () => setPhotoBase64(lecteur.result)
    lecteur.readAsDataURL(fichier)
  }

  async function enregistrer(e) {
    e.preventDefault()
    await client.post('/employes', { ...form, photo_base64: photoBase64 })
    setModalOuvert(false)
    setForm(VIDE)
    setPhotoBase64(null)
    charger()
  }

  async function desactiver(id) {
    await client.delete(`/employes/${id}`)
    charger()
  }

  return (
    <>
      <Topbar title="Employés" subtitle="Gestion des profils et inscription faciale">
        <button className="btn-sm btn-acc" onClick={() => setModalOuvert(true)}>+ Employé</button>
      </Topbar>
      <div className="content">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Matricule</th><th>Nom</th><th>Département</th><th>Poste</th><th>Visage enregistré</th><th>Présent</th><th></th>
              </tr>
            </thead>
            <tbody>
              {employes.map((e) => (
                <tr key={e.id}>
                  <td style={{fontFamily:'var(--font-mono)'}}>{e.matricule}</td>
                  <td style={{color:'var(--text-primary)',fontWeight:500}}>{e.nom_complet}</td>
                  <td>{e.departement || '—'}</td>
                  <td>{e.poste || '—'}</td>
                  <td>
                    <span className="pill" style={{background: e.a_un_encodage ? 'var(--bg-success)' : 'var(--bg-danger)', color: e.a_un_encodage ? 'var(--text-success)' : 'var(--text-danger)'}}>
                      {e.a_un_encodage ? 'Oui' : 'Non'}
                    </span>
                  </td>
                  <td>
                    <span className="pill" style={{background: e.present_aujourdhui ? 'var(--bg-success)' : 'var(--bg-danger)', color: e.present_aujourdhui ? 'var(--text-success)' : 'var(--text-danger)'}}>
                      {e.present_aujourdhui ? 'Présent' : 'Absent'}
                    </span>
                  </td>
                  <td><button className="btn-sm" onClick={() => desactiver(e.id)}>Désactiver</button></td>
                </tr>
              ))}
              {employes.length === 0 && <tr><td colSpan={7}><div className="empty-state">Aucun employé enregistré</div></td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      {modalOuvert && (
        <div className="overlay" onClick={() => setModalOuvert(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Nouvel employé</h3>
            <form onSubmit={enregistrer}>
              <div className="field"><label>Prénom</label><input required value={form.prenom} onChange={(e)=>setForm({...form,prenom:e.target.value})} /></div>
              <div className="field"><label>Nom</label><input required value={form.nom} onChange={(e)=>setForm({...form,nom:e.target.value})} /></div>
              <div className="field"><label>Email</label><input type="email" value={form.email} onChange={(e)=>setForm({...form,email:e.target.value})} /></div>
              <div className="field"><label>Téléphone</label><input value={form.telephone} onChange={(e)=>setForm({...form,telephone:e.target.value})} /></div>
              <div className="field"><label>Poste</label><input value={form.poste} onChange={(e)=>setForm({...form,poste:e.target.value})} /></div>
              <div className="field">
                <label>Département</label>
                <select value={form.id_departement} onChange={(e)=>setForm({...form,id_departement:e.target.value})}>
                  <option value="">— Sélectionner —</option>
                  {departements.map((d) => <option key={d.id} value={d.id}>{d.nom}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Photo (inscription faciale)</label>
                <input type="file" accept="image/*" ref={fileRef} onChange={onPhotoChange} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-sm" onClick={() => setModalOuvert(false)}>Annuler</button>
                <button type="submit" className="btn-sm btn-acc">Enregistrer</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
