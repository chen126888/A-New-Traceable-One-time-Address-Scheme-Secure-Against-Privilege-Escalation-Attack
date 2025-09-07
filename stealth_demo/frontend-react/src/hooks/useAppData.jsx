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
  const [dsks, setDsks] = useState([]) // 新增 DSK 狀態
  const [txMessages, setTxMessages] = useState([]) // 新增交易訊息狀態
  const [loading, setLoading] = useState({})
  const [error, setError] = useState('')

  // 使用 useCallback 來防止無限循環
  const loadKeys = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, keys: true }))
      const keyData = await apiService.getKeys()
      const keys = keyData?.keys || keyData || []
      setKeys(Array.isArray(keys) ? keys : [])
      setError('')
    } catch (err) {
      console.error('Failed to load keys:', err)
      setError('Failed to load keys: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, keys: false }))
    }
  }, [])

  const loadAddresses = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, addresses: true }))
      const addressData = await apiService.get('/addresslist')
      const addresses = addressData?.addresses || addressData || []
      setAddresses(Array.isArray(addresses) ? addresses : [])
      setError('')
    } catch (err) {
      console.error('Failed to load addresses:', err)
      setError('Failed to load addresses: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, addresses: false }))
    }
  }, [])

  // 新增載入 DSK 函式
  const loadDsks = useCallback(async () => {
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

  // 新增載入交易訊息函式
  const loadTxMessages = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, txMessages: true }))
      const txData = await apiService.get('/tx_messages')
      const txMessages = txData?.tx_messages || txData || []
      setTxMessages(Array.isArray(txMessages) ? txMessages : [])
      setError('')
    } catch (err) {
      console.error('Failed to load transaction messages:', err)
      setError('Failed to load transaction messages: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, txMessages: false }))
    }
  }, [])

  const loadAllData = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, all: true }))
      setError('')
      
      const results = await Promise.allSettled([
        loadKeys(),
        loadAddresses(),
        loadDsks(), // 新增載入 DSKs
        loadTxMessages() // 新增載入交易訊息
      ])
      
      const failures = results.filter(result => result.status === 'rejected')
      if (failures.length > 0) {
        console.warn('Some data loading operations failed:', failures)
      }
      
    } catch (err) {
      console.error('Data loading error:', err)
      setError('Failed to load data: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, all: false }))
    }
  }, [loadKeys, loadAddresses, loadDsks, loadTxMessages]) // 更新依賴數組

  const addKey = useCallback((newKey) => {
    setKeys(prev => [...prev, newKey])
  }, [])

  const addAddress = useCallback((newAddress) => {
    setAddresses(prev => [...prev, newAddress])
  }, [])

  // 新增添加 DSK 函式
  const addDsk = useCallback((newDsk) => {
    setDsks(prev => [...prev, newDsk])
  }, [])

  // 新增添加交易訊息函式
  const addTxMessage = useCallback((newTxMessage) => {
    setTxMessages(prev => [...prev, newTxMessage])
  }, [])

  const resetData = useCallback(() => {
    console.log('Manual reset data called')
    setKeys([])
    setAddresses([])
    setDsks([]) // 新增重置 DSKs
    setTxMessages([]) // 新增重置交易訊息
    setError('')
  }, [])

  const clearError = useCallback(() => {
    setError('')
  }, [])

  const value = {
    // 數據
    keys,
    addresses,
    dsks, // 新增 DSKs
    txMessages, // 新增交易訊息
    loading,
    error,
    
    // 方法
    loadAllData,
    loadKeys,
    loadAddresses,
    loadDsks, // 新增載入 DSKs
    loadTxMessages, // 新增載入交易訊息
    addKey,
    addAddress,
    addDsk, // 新增添加 DSK
    addTxMessage, // 新增添加交易訊息
    resetData,
    setError,
    clearError
  }

  console.log('AppDataProvider rendering with:', { 
    keysCount: keys.length, 
    addressesCount: addresses.length,
    dsksCount: dsks.length, // 新增 DSKs 數量
    txMessagesCount: txMessages.length, // 新增交易訊息數量
    loading,
    error 
  })

  return (
    <AppDataContext.Provider value={value}>
      {children}
    </AppDataContext.Provider>
  )
}