import React from 'react'
import SystemSetup from './components/SystemSetup'
import KeyManagement from './components/KeyManagement'
import AddressGeneration from './components/AddressGeneration'
import AddressRecognition from './components/AddressRecognition'
import DSKGeneration from './components/DSKGeneration'
import MessageSigning from './components/MessageSigning'
import SignatureVerification from './components/SignatureVerification'
import IdentityTracing from './components/IdentityTracing'
import PerformanceTest from './components/PerformanceTest'
import SchemeSelector from './components/SchemeSelector'
import { AppDataProvider } from './hooks/useAppData'
import { SchemeProvider, useSchemeContext } from './hooks/useSchemeContext'

function Header() {
  return (
    <h1 className="header">
      🔐 Multi-Scheme Cryptography Demo System
    </h1>
  )
}

function AppGrid() {
  const { supportsSigning, supportsVerification, hasCapability } = useSchemeContext()
  
  // Determine which components to show based on scheme capabilities
  const showSigning = supportsSigning || supportsVerification
  const showIdentityTracing = hasCapability('has_tracing')
  
  return (
    <div className="grid">
      {/* Row 1: Scheme Selection and System Setup */}
      <SchemeSelector />
      <SystemSetup />
      
      {/* Row 2: Key Management and Address Generation */}
      <KeyManagement />
      <AddressGeneration />
      
      {/* Row 3: Address Recognition and DSK Generation */}
      <AddressRecognition />
      <DSKGeneration />
      
      {/* Row 4: Message Signing and Signature Verification OR Identity Tracing */}
      {showSigning ? (
        <>
          <MessageSigning />
          <SignatureVerification />
        </>
      ) : (
        <>
          {showIdentityTracing && <IdentityTracing />}
          <div></div> {/* Empty div to maintain grid layout */}
        </>
      )}
      
      {/* Row 5: Identity Tracing for schemes that support both signing and tracing */}
      {showSigning && showIdentityTracing && <IdentityTracing />}
    </div>
  )
}

function App() {
  return (
    <SchemeProvider>
      <AppDataProvider>
        <div className="app">
          <div className="container">
            <Header />
            <AppGrid />
            
            {/* Performance Test spans full width */}
            <PerformanceTest />
          </div>
        </div>
      </AppDataProvider>
    </SchemeProvider>
  )
}

export default App