import React, { createContext, useContext, useState, useEffect } from 'react'
import { apiService } from '../services/apiService'

// 創建方案上下文
const SchemeContext = createContext()

// 方案提供者組件
export function SchemeProvider({ children }) {
  const [currentScheme, setCurrentScheme] = useState('stealth')
  const [availableSchemes, setAvailableSchemes] = useState(['stealth', 'sitaiba'])
  const [capabilities, setCapabilities] = useState({})
  const [loading, setLoading] = useState(false)

  // 獲取可用方案和當前狀態
  const fetchSchemeStatus = async () => {
    try {
      const response = await apiService.get('/schemes')
      setCurrentScheme(response.current_scheme)
      setAvailableSchemes(response.available_schemes)
      setCapabilities(response.current_capabilities)
    } catch (error) {
      console.error('Failed to fetch scheme status:', error)
    }
  }

  // 初始化時獲取方案狀態
  useEffect(() => {
    fetchSchemeStatus()
  }, [])

  // 切換方案
  const switchScheme = async (schemeName) => {
    if (schemeName === currentScheme) return

    setLoading(true)
    try {
      const response = await apiService.post('/switch_scheme', { 
        scheme: schemeName 
      })
      
      if (response.status === 'switched') {
        setCurrentScheme(schemeName)
        
        // 獲取新方案的能力
        const capResponse = await apiService.get(`/scheme_capabilities?scheme=${schemeName}`)
        setCapabilities(capResponse)
        
        console.log(`✅ Switched to ${schemeName} scheme`)
        return true
      }
    } catch (error) {
      console.error(`Failed to switch to ${schemeName}:`, error)
      return false
    } finally {
      setLoading(false)
    }
  }

  // 獲取方案能力
  const getSchemeCapabilities = (schemeName = null) => {
    if (schemeName && schemeName !== currentScheme) {
      // 如果查詢其他方案的能力，需要額外請求
      return apiService.get(`/scheme_capabilities?scheme=${schemeName}`)
    }
    return capabilities
  }

  // 檢查當前方案是否支援某功能
  const hasCapability = (capability) => {
    return capabilities[capability] || false
  }

  // 清空當前方案數據
  const clearCurrentData = async () => {
    try {
      await apiService.post('/reset')
      console.log(`🧹 Cleared ${currentScheme} scheme data`)
    } catch (error) {
      console.error('Failed to clear scheme data:', error)
    }
  }

  // 清空所有方案數據
  const clearAllData = async () => {
    try {
      await apiService.post('/reset', { reset_all: true })
      console.log('🧹 Cleared all schemes data')
    } catch (error) {
      console.error('Failed to clear all data:', error)
    }
  }

  const contextValue = {
    // 狀態
    currentScheme,
    availableSchemes,
    capabilities,
    loading,
    
    // 方法
    switchScheme,
    getSchemeCapabilities,
    hasCapability,
    clearCurrentData,
    clearAllData,
    refreshStatus: fetchSchemeStatus,
    
    // 便利屬性
    isStealthScheme: currentScheme === 'stealth',
    isSitaibaScheme: currentScheme === 'sitaiba',
    supportsSigning: hasCapability('has_signing'),
    supportsVerification: hasCapability('has_verification')
  }

  return (
    <SchemeContext.Provider value={contextValue}>
      {children}
    </SchemeContext.Provider>
  )
}

// 使用方案上下文的 Hook
export function useSchemeContext() {
  const context = useContext(SchemeContext)
  if (!context) {
    throw new Error('useSchemeContext must be used within a SchemeProvider')
  }
  return context
}

// 快捷 Hooks
export function useCurrentScheme() {
  const { currentScheme } = useSchemeContext()
  return currentScheme
}

export function useSchemeCapabilities() {
  const { capabilities, hasCapability } = useSchemeContext()
  return { capabilities, hasCapability }
}

export function useSchemeActions() {
  const { switchScheme, clearCurrentData, clearAllData, loading } = useSchemeContext()
  return { switchScheme, clearCurrentData, clearAllData, loading }
}