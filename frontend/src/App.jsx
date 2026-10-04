/**
 * AirVision AI — router & page registry
 */

import { Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import DashboardPage from './pages/DashboardPage'
import LiveMapPage from './pages/LiveMapPage'
import ForecastPage from './pages/ForecastPage'
import ComparePage from './pages/ComparePage'
import CountriesPage from './pages/CountriesPage'
import HotspotsPage from './pages/HotspotsPage'
import AboutPage from './pages/AboutPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/map" element={<LiveMapPage />} />
        <Route path="/forecast" element={<ForecastPage />} />
        <Route path="/compare" element={<ComparePage />} />
        <Route path="/countries" element={<CountriesPage />} />
        <Route path="/hotspots" element={<HotspotsPage />} />
        <Route path="/about" element={<AboutPage />} />
        {/* Historical Analytics was removed — redirect old links/bookmarks */}
        <Route path="/analytics" element={<Navigate to="/" replace />} />
        <Route path="/historical" element={<Navigate to="/" replace />} />
        <Route path="*" element={<DashboardPage />} />
      </Route>
    </Routes>
  )
}
