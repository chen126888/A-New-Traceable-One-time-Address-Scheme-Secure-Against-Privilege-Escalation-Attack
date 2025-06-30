import React from 'react'
import SystemSetup from './components/SystemSetup'
import KeyManagement from './components/KeyManagement'
import AddressGeneration from './components/AddressGeneration'
import AddressVerification from './components/AddressVerification'
import DSKGeneration from './components/DSKGeneration'
import MessageSigning from './components/MessageSigning'
import SignatureVerification from './components/SignatureVerification'
import IdentityTracing from './components/IdentityTracing'
import PerformanceTest from './components/PerformanceTest'
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
            {/* 第一行：基礎設置和密鑰管理 */}
            <SystemSetup />
            <KeyManagement />
            
            {/* 第二行：地址相關操作 */}
            <AddressGeneration />
            <AddressVerification />
            
            {/* 第三行：DSK和簽名操作 */}
            <DSKGeneration />
            <MessageSigning />
            
            {/* 第四行：驗證和追蹤 */}
            <SignatureVerification />
            <IdentityTracing />
          </div>
          
          {/* 性能測試跨越整個寬度 */}
          <PerformanceTest />
        </div>
      </div>
    </AppDataProvider>
  )
}

export default App