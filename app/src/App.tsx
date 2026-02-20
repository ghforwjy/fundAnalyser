import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from 'react-router-dom'
import { ThemeProvider } from 'next-themes'
import { Layout } from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import FundList from './pages/FundAnalysis/FundList'
import FundDetail from './pages/FundAnalysis/FundDetail'
import Portfolio from './pages/Portfolio'
import DataSource from './pages/DataManage/DataSource'
import TableData from './pages/DataManage/TableData'
import TableSchema from './pages/DataManage/TableSchema'
import Settings from './pages/Settings'
import './App.css'

function AppContent() {
  const location = useLocation()
  const navigate = useNavigate()
  
  const getCurrentPage = () => {
    const path = location.pathname
    if (path === '/') return 'dashboard'
    if (path === '/funds') return 'fund-list'
    if (path.startsWith('/funds/')) return 'fund-detail'
    if (path === '/portfolio') return 'portfolio'
    if (path === '/data/source') return 'data-source'
    if (path === '/data/tables') return 'table-data'
    if (path === '/data/schema') return 'table-schema'
    if (path === '/settings') return 'settings'
    return 'dashboard'
  }
  
  const handleNavigate = (page: 'dashboard' | 'data-source' | 'table-schema' | 'table-data' | 'fund-list' | 'fund-detail' | 'portfolio' | 'settings') => {
    switch (page) {
      case 'dashboard':
        navigate('/')
        break
      case 'fund-list':
        navigate('/funds')
        break
      case 'portfolio':
        navigate('/portfolio')
        break
      case 'data-source':
        navigate('/data/source')
        break
      case 'table-data':
        navigate('/data/tables')
        break
      case 'table-schema':
        navigate('/data/schema')
        break
      case 'settings':
        navigate('/settings')
        break
      default:
        break
    }
  }
  
  return (
    <Layout currentPage={getCurrentPage()} onNavigate={handleNavigate}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/funds" element={<FundList />} />
        <Route path="/funds/:fundCode" element={<FundDetail />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/data/source" element={<DataSource />} />
        <Route path="/data/tables" element={<TableData />} />
        <Route path="/data/schema" element={<TableSchema />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  )
}

function App() {
  return (
    <ThemeProvider defaultTheme="dark" enableSystem={false} attribute="class">
      <Router>
        <AppContent />
      </Router>
    </ThemeProvider>
  )
}

export default App