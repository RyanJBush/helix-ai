import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Login' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/ticker', label: 'Ticker View' },
  { to: '/news', label: 'News Feed' },
  { to: '/signals', label: 'Signals' },
]

export default function NavBar() {
  return (
    <header className="border-b border-slate-800 bg-slate-900 px-4 py-3">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4">
        <h1 className="text-lg font-bold text-cyan-400">Helix AI</h1>
        <nav className="flex flex-wrap gap-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `rounded-md px-3 py-1.5 text-sm ${
                  isActive
                    ? 'bg-cyan-500/20 text-cyan-300'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}
