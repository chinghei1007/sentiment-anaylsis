import { Outlet, Link, NavLink } from 'react-router-dom'
import { Home, FileText, Batch, Key, Brain, BarChart3, Database, Menu, X } from 'lucide-react'
import { useState } from 'react'

export default function Layout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  const navItems = [
    { to: '/', icon: Home, label: 'Home' },
    { to: '/predict', icon: FileText, label: 'Single Predict' },
    { to: '/batch', icon: Batch, label: 'Batch Predict' },
    { to: '/keywords', icon: Key, label: 'Keyword Analysis' },
    { to: '/train', icon: Brain, label: 'Train Model' },
    { to: '/evaluate', icon: BarChart3, label: 'Evaluate' },
    { to: '/dataset', icon: Database, label: 'Dataset' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar toggle */}
      <button
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md"
      >
        {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      <aside
        className={`fixed lg:relative lg:translate-x-0 z-40 w-64 bg-white shadow-lg lg:shadow-none h-full lg:h-auto lg:border-r lg:border-gray-200 transition-transform duration-300 ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="p-6 border-b border-gray-200">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">S</span>
            </div>
            <div>
              <h1 className="font-bold text-lg">Sentiment Analysis</h1>
              <p className="text-sm text-gray-500">PySpark ML</p>
            </div>
          </Link>
        </div>

        <nav className="p-4">
          <ul className="space-y-2">
            {navItems.map(({ to, icon: Icon, label }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  onClick={() => setIsSidebarOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary-50 text-primary-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`
                  }
                >
                  <Icon size={20} />
                  {label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-gray-50">
          <p className="text-xs text-gray-500 text-center">
            v1.0.0 | PySpark ML
          </p>
        </div>
      </aside>

      {/* Overlay for mobile sidebar */}
      {isSidebarOpen && (
        <div
          onClick={() => setIsSidebarOpen(false)}
          className="lg:hidden fixed inset-0 bg-black/50 z-30"
        />
      )}

      {/* Main content */}
      <main
        className={`lg:ml-64 p-4 lg:p-8 transition-all duration-300 ${
          isSidebarOpen ? 'ml-0 lg:ml-64' : 'ml-0 lg:ml-64'
        }`}
      >
        <Outlet />
      </main>
    </div>
  )
}
