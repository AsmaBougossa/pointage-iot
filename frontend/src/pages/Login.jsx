import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import client from '../api/client.js'

export default function Login() {
  const [email, setEmail] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [erreur, setErreur] = useState('')
  const navigate = useNavigate()

  async function onSubmit(e) {
    e.preventDefault()
    setErreur('')
    try {
      const res = await client.post('/auth/connexion', { email, mot_de_passe: motDePasse })
      localStorage.setItem('access_token', res.data.access_token)
      navigate('/')
    } catch {
      setErreur('Identifiants invalides')
    }
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <div style={{display:'flex',alignItems:'center',gap:9,marginBottom:22}}>
          <div className="s-logo-icon"><i className="ti ti-wifi" style={{fontSize:18,color:'var(--text-accent)'}} /></div>
          <div>
            <div className="s-logo-text">IoT Pointage</div>
            <div className="s-logo-sub">Système intelligent</div>
          </div>
        </div>
        <form onSubmit={onSubmit}>
          <div className="field"><label>Email</label><input type="email" required value={email} onChange={(e)=>setEmail(e.target.value)} /></div>
          <div className="field"><label>Mot de passe</label><input type="password" required value={motDePasse} onChange={(e)=>setMotDePasse(e.target.value)} /></div>
          {erreur && <p style={{color:'var(--text-danger)',fontSize:12,marginBottom:12}}>{erreur}</p>}
          <button type="submit" className="btn-sm btn-acc" style={{width:'100%'}}>Se connecter</button>
        </form>
      </div>
    </div>
  )
}
