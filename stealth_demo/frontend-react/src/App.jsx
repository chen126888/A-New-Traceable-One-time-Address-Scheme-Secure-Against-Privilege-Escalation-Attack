import React, { useState } from 'react'
import SchemeSelector from './components/SchemeSelector'
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

function Header({ activeScheme }) {
  return (
    <h1 className="header">
      🔐 Interactive Crypto Demo {activeScheme && `(${activeScheme})`}
    </h1>
  )
}

function App() {
  const [activeScheme, setActiveScheme] = useState('')

  // Check if current scheme supports signing
  const supportsSign = activeScheme !== 'sitaiba'

  return (
    <AppDataProvider>
      <div className="app">
        <div className="container">
          <Header activeScheme={activeScheme} />
          
          <div className="grid">
            {/* Scheme Selection */}
            <SchemeSelector onSchemeChange={setActiveScheme} />
            
            {/* 第一行：基礎設置和密鑰管理 */}
            <SystemSetup activeScheme={activeScheme} />
            <KeyManagement activeScheme={activeScheme} />
            
            {/* 第二行：地址相關操作 */}
            <AddressGeneration activeScheme={activeScheme} />
            <AddressVerification activeScheme={activeScheme} />
            
            {/* 第三行：DSK和簽名操作 */}
            <DSKGeneration activeScheme={activeScheme} />
            {supportsSign && <MessageSigning activeScheme={activeScheme} />}
            
            {/* 第四行：驗證和追蹤 */}
            {supportsSign && <SignatureVerification activeScheme={activeScheme} />}
            <IdentityTracing activeScheme={activeScheme} />
          </div>
          
          {/* 性能測試跨越整個寬度 */}
          <PerformanceTest />
        </div>
      </div>
    </AppDataProvider>
  )
}

export default App