import React, { useEffect } from 'react'
import SystemSetup from './components/SystemSetup'
import KeyManagement from './components/KeyManagement'
import AddressGeneration from './components/AddressGeneration'
import { apiService } from './services/apiService'

function Header() {
  return (
    <h1 className="header">
      🔐 Interactive Stealth Scheme Demo
    </h1>
  )
}

function AddressVerification() {
  return (
    <div className="section">
      <h3 className="section-title">🔍 Address Verification</h3>
      <p>Address verification component will be here</p>
    </div>
  )
}

function App() {
  useEffect(() => {
    const resetEverything = async () => {
      try {
        // 強制重置後端
        await apiService.resetSystem()
        
        // 延遲一點讓重置完成
        await new Promise(resolve => setTimeout(resolve, 100))
        
        console.log('✅ Backend reset completed')
        
        // 強制清除瀏覽器可能的緩存
        if (window.performance && window.performance.navigation.type === window.performance.navigation.TYPE_RELOAD) {
          console.log('🔄 Page refreshed - data should be clean')
        }
        
      } catch (err) {
        console.log('⚠️ Reset failed:', err.message)
      }
    }

    resetEverything()
  }, [])

  return (
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
  )
}

export default App