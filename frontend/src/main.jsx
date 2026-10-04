import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { ThemeProvider } from './context/ThemeContext'
import { LiveDataProvider } from './context/LiveDataContext'
import ErrorBoundary from './components/ErrorBoundary'
import './index.css'
import 'leaflet/dist/leaflet.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <ThemeProvider>
        <LiveDataProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </LiveDataProvider>
      </ThemeProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)
