import React from 'react'
import SystemSetup from './components/SystemSetup'
import KeyManagement from './components/KeyManagement'
import AddressGeneration from './components/AddressGeneration'
import AddressVerification from './components/AddressVerification'
import { AppDataProvider } from './hooks/useAppData'

function Header() {
  return (
    <h1 className="header">
      🔐 Interactive Stealth Scheme Demo
    </h1>
  )
}

function App() {
  return (
    <AppDataProvider>
      <div className="app">
        <div className="container">
          <Header />
          
          <div className="grid">
            <SystemSetup />
            <KeyManagement />
            <AddressGeneration />
            <AddressVerification />
          </div>
        </div>
      </div>
    </AppDataProvider>
  )
}

export default App