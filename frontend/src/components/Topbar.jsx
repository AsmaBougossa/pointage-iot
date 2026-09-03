export default function Topbar({ title, subtitle, children }) {
  const heure = new Date().toLocaleTimeString('fr-FR')
  return (
    <div className="topbar">
      <div>
        <div className="page-title">{title}</div>
        <div className="page-sub">{subtitle}</div>
      </div>
      <div className="topbar-r">
        <div className="tb-time">{heure}</div>
        {children}
      </div>
    </div>
  )
}
