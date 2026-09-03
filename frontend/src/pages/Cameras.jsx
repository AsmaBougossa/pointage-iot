import { useEffect, useState } from 'react'
import Topbar from '../components/Topbar.jsx'
import client from '../api/client.js'

const VIDE = { code:'', nom:'', emplacement:'', adresse_ip:'', flux_url:'0' }

export default function Cameras() {
  const [cameras, setCameras] = useState([])
  const [modalOuvert, setModalOuvert] = useState(false)
  const [form, setForm] = useState(VIDE)

  function charger() {
    client.get('/cameras').then((res) => setCameras(res.data))
  }
  useEffect(() => { charger() }, [])

  async function enregistrer(e) {
    e.preventDefault()
    await client.post('/cameras', form)
    setModalOuvert(false)
    setForm(VIDE)
    charger()
  }

  async function basculerStatut(cam) {
    const nouveauStatut = cam.statut === 'en_ligne' ? 'hors_ligne' : 'en_ligne'
    await client.put(`/cameras/${cam.id}/statut`, { statut: nouveauStatut })
    charger()
  }

  return (
    <>
      <Topbar title="Caméras IoT" subtitle="Dispositifs de capture connectés au système">
        <button className="btn-sm btn-acc" onClick={() => setModalOuvert(true)}>+ Caméra</button>
      </Topbar>
      <div className="content">
        <div className="cam-grid">
          {cameras.map((cam) => (
            <div className="cam-card" key={cam.id}>
              <div className="cam-card-h">
                <div>
                  <div className="f-name">{cam.code}</div>
                  <div className="f-dept">{cam.emplacement}</div>
                </div>
                <span className="pill" style={{background: cam.statut === 'en_ligne' ? 'var(--bg-success)' : 'var(--bg-danger)', color: cam.statut === 'en_ligne' ? 'var(--text-success)' : 'var(--text-danger)'}}>
                  {cam.statut === 'en_ligne' ? 'En ligne' : 'Hors ligne'}
                </span>
              </div>
              <div style={{padding:'0 14px 14px',fontSize:11,color:'var(--text-muted)',fontFamily:'var(--font-mono)'}}>
                {cam.adresse_ip || 'IP non définie'}
              </div>
              <div style={{padding:'0 14px 14px'}}>
                <button className="btn-sm" style={{width:'100%'}} onClick={() => basculerStatut(cam)}>
                  {cam.statut === 'en_ligne' ? 'Mettre hors ligne' : 'Mettre en ligne'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {modalOuvert && (
        <div className="overlay" onClick={() => setModalOuvert(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Nouvelle caméra</h3>
            <form onSubmit={enregistrer}>
              <div className="field"><label>Code (ex: CAM-007)</label><input required value={form.code} onChange={(e)=>setForm({...form,code:e.target.value})} /></div>
              <div className="field"><label>Nom</label><input required value={form.nom} onChange={(e)=>setForm({...form,nom:e.target.value})} /></div>
              <div className="field"><label>Emplacement</label><input value={form.emplacement} onChange={(e)=>setForm({...form,emplacement:e.target.value})} /></div>
              <div className="field"><label>Adresse IP</label><input value={form.adresse_ip} onChange={(e)=>setForm({...form,adresse_ip:e.target.value})} /></div>
              <div className="field"><label>URL du flux (ou index webcam)</label><input value={form.flux_url} onChange={(e)=>setForm({...form,flux_url:e.target.value})} /></div>
              <div className="modal-actions">
                <button type="button" className="btn-sm" onClick={() => setModalOuvert(false)}>Annuler</button>
                <button type="submit" className="btn-sm btn-acc">Ajouter</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
