import { useEffect, useState } from 'react'
import Topbar from '../components/Topbar.jsx'
import client from '../api/client.js'

export default function LiveFeed() {
  const [cameras, setCameras] = useState([])
  const [camSelectionnee, setCamSelectionnee] = useState(null)

  useEffect(() => {
    client.get('/cameras').then((res) => {
      setCameras(res.data)
      const enLigne = res.data.find((c) => c.statut === 'en_ligne')
      setCamSelectionnee(enLigne || res.data[0] || null)
    })
  }, [])

  return (
    <>
      <Topbar title="Flux en direct" subtitle="Reconnaissance faciale en temps réel sur les caméras IoT" />
      <div className="content">
        <div className="grid2" style={{gridTemplateColumns:'1fr 300px'}}>
          <div className="card">
            <div className="card-h">
              <span className="card-title">{camSelectionnee ? `${camSelectionnee.code} — ${camSelectionnee.nom}` : 'Aucune caméra'}</span>
              <div style={{display:'flex',alignItems:'center',gap:5,fontSize:10,color:'var(--text-success)'}}><div className="live-dot" />LIVE</div>
            </div>
            <div style={{padding:14}}>
              <div className="video-wrap">
                {camSelectionnee ? (
                  <img src={`/api/reconnaissance/flux/${camSelectionnee.id}`} alt="Flux caméra" />
                ) : (
                  <div className="empty-state">Aucun flux disponible — ajoutez une caméra</div>
                )}
              </div>
              <p style={{fontSize:11,color:'var(--text-muted)',marginTop:10}}>
                Le flux affiche les boîtes de détection (vert = employé reconnu, rouge = visage inconnu)
                calculées côté serveur avec OpenCV + face_recognition.
              </p>
            </div>
          </div>

          <div className="card">
            <div className="card-h"><span className="card-title">Caméras disponibles</span></div>
            <div className="feed">
              {cameras.map((cam) => (
                <div
                  key={cam.id}
                  className="feed-item"
                  style={{cursor:'pointer'}}
                  onClick={() => setCamSelectionnee(cam)}
                >
                  <div className="av" style={{background: cam.statut === 'en_ligne' ? 'var(--bg-success)' : 'var(--bg-danger)', color: cam.statut === 'en_ligne' ? 'var(--text-success)' : 'var(--text-danger)'}}>
                    <i className="ti ti-camera" style={{fontSize:14}} />
                  </div>
                  <div style={{flex:1}}>
                    <div className="f-name">{cam.code}</div>
                    <div className="f-dept">{cam.emplacement}</div>
                  </div>
                  <span className="pill" style={{background: cam.statut === 'en_ligne' ? 'var(--bg-success)' : 'var(--bg-danger)', color: cam.statut === 'en_ligne' ? 'var(--text-success)' : 'var(--text-danger)'}}>
                    {cam.statut === 'en_ligne' ? 'En ligne' : 'Hors ligne'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
