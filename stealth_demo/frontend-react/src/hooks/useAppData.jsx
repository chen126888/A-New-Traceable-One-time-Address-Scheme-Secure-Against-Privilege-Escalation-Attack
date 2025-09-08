import React, { useState, createContext, useContext, useCallback } from 'react'
import { apiService } from '../services/apiService'

// 創建 Context
const AppDataContext = createContext()

// Hook 用於消費 Context
export const useAppData = () => {
  const context = useContext(AppDataContext)
  if (!context) {
    throw new Error('useAppData must be used within AppDataProvider')
  }
  return context
}

// Provider 組件
export const AppDataProvider = ({ children }) => {
  const [keys, setKeys] = useState([])
  const [addresses, setAddresses] = useState([])
  const [dsks, setDsks] = useState([]) // New
  const [txMessages, setTxMessages] = useState([]) // New
  const [loading, setLoading] = useState({})
  const [error, setError] = useState('')

  // 使用 useCallback 來防止無限循環
  const loadKeys = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, keys: true }))
      const keyData = await apiService.getKeys()
      // Handle API response format: { keys: [...] }
      const keys = keyData?.keys || keyData || []
      setKeys(Array.isArray(keys) ? keys : [])
      // 成功時清除錯誤
      setError('')
    } catch (err) {
      console.error('Failed to load keys:', err)
      setError('Failed to load keys: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, keys: false }))
    }
  }, []) // 空依賴數組

  // 使用 useCallback 來防止無限循環
  const loadAddresses = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, addresses: true }))
      const addressData = await apiService.get('/addresslist')
      // Handle API response format: { addresses: [...] }
      const addresses = addressData?.addresses || addressData || []
      setAddresses(Array.isArray(addresses) ? addresses : [])
      // 成功時清除錯誤
      setError('')
    } catch (err) {
      console.error('Failed to load addresses:', err)
      setError('Failed to load addresses: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, addresses: false }))
    }
  }, []) // 空依賴數組

  const loadDSKs = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, dsks: true }))
      const dskData = await apiService.get('/dsklist')
      const dsks = dskData?.dsks || dskData || []
      setDsks(Array.isArray(dsks) ? dsks : [])
      setError('')
    } catch (err) {
      console.error('Failed to load DSKs:', err)
      setError('Failed to load DSKs: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, dsks: false }))
    }
  }, [])

  const loadTxMessages = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, txMessages: true }))
      const txData = await apiService.getTxMessages() // Use the new apiService method
      const txMessages = txData?.tx_messages || txData || []
      setTxMessages(Array.isArray(txMessages) ? txMessages : [])
      setError('')
    } catch (err) {
      console.error('Failed to load Tx Messages:', err)
      setError('Failed to load Tx Messages: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, txMessages: false }))
    }
  }, [])

  // 使用 useCallback 來防止無限循環
  const loadAllData = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, all: true }))
      setError('')
      
      // 並行執行但分別處理錯誤
      const results = await Promise.allSettled([
        loadKeys(),
        loadAddresses(),
        loadDSKs(), // New
        loadTxMessages() // New
      ])
      
      // 檢查是否有失敗的操作
      const failures = results.filter(result => result.status === 'rejected')
      if (failures.length > 0) {
        console.warn('Some data loading operations failed:', failures)
        // 但不設置全局錯誤，讓個別函數處理自己的錯誤
      }
      
    } catch (err) {
      console.error('Data loading error:', err)
      setError('Failed to load data: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, all: false }))
    }
  }, [loadKeys, loadAddresses, loadDSKs, loadTxMessages]) // 依賴 loadKeys 和 loadAddresses

  // 添加新密鑰
  const addKey = useCallback((newKey) => {
    setKeys(prev => [...prev, newKey])
  }, [])

  // 添加新地址
  const addAddress = useCallback((newAddress) => {
    setAddresses(prev => [...prev, newAddress])
  }, [])

  // 添加新 DSK
  const addDsk = useCallback((newDsk) => {
    setDsks(prev => [...prev, newDsk])
  }, [])

  // 添加新 Tx Message
  const addTxMessage = useCallback((newTxMessage) => {
    setTxMessages(prev => [...prev, newTxMessage])
  }, [])

  // 重置所有數據
  const resetData = useCallback(() => {
    console.log('Manual reset data called')
    setKeys([])
    setAddresses([])
    setDsks([]) // New
    setTxMessages([]) // New
    setError('')
  }, [])

  // 清除錯誤的函數
  const clearError = useCallback(() => {
    setError('')
  }, [])

  const value = {
    // 數據
    keys,
    addresses,
    dsks,
    txMessages,
    loading,
    error,
    
    // 方法
    loadAllData,
    loadKeys,
    loadAddresses,
    loadDSKs,
    loadTxMessages,
    addKey,
    addAddress,
    addDsk,
    addTxMessage,
    resetData,
    setError,
    clearError
  }

  console.log('AppDataProvider rendering with:', { 
    keysCount: keys.length, 
    addressesCount: addresses.length,
    dsksCount: dsks.length, // New
    txMessagesCount: txMessages.length, // New
    loading,
    error 
  })

  return (
    <AppDataContext.Provider value={value}>
      {children}
    </AppDataContext.Provider>
  )
}
