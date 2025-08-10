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
  const [transactions, setTransactions] = useState([])  // 添加 txlist
  const [loading, setLoading] = useState({})
  const [error, setError] = useState('')

  // 使用 useCallback 來防止無限循環
  const loadKeys = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, keys: true }))
      const keyData = await apiService.getKeys()
      setKeys(keyData)
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
      
      // 標準化地址數據格式，處理不同 scheme 的差異
      const normalizedAddresses = addressData.map(addr => ({
        ...addr,
        // 確保有統一的 id 字段
        id: addr.id || `stealth_addr_${addr.addr_id}`,
        // 為 stealth 地址添加平坦化的字段以便顯示
        addr_hex: addr.addr_hex || addr.address,
        r1_hex: addr.r1_hex || addr.R1,
        r2_hex: addr.r2_hex || addr.R2,
        c_hex: addr.c_hex || addr.C,
        // 確保有 key_id 字段
        key_id: addr.key_id
      }))
      
      setAddresses(normalizedAddresses)
      // 成功時清除錯誤
      setError('')
    } catch (err) {
      console.error('Failed to load addresses:', err)
      setError('Failed to load addresses: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, addresses: false }))
    }
  }, []) // 空依賴數組

  // 使用 useCallback 來防止無限循環
  const loadAllData = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, all: true }))
      setError('')
      
      // 並行執行但分別處理錯誤
      const results = await Promise.allSettled([
        loadKeys(),
        loadAddresses()
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
  }, [loadKeys, loadAddresses]) // 依賴 loadKeys 和 loadAddresses

  // 添加新密鑰
  const addKey = useCallback((newKey) => {
    setKeys(prev => [...prev, newKey])
  }, [])

  // 添加新地址
  const addAddress = useCallback((newAddress) => {
    // 標準化地址數據格式，處理不同 scheme 的差異
    const normalizedAddress = {
      ...newAddress,
      // 確保有統一的 id 字段
      id: newAddress.id || `addr_${newAddress.addr_id ?? Date.now()}`,
      // 為 stealth 地址添加平坦化的 hex 字段以便顯示
      addr_hex: newAddress.addr_hex || newAddress.address?.hex,
      r1_hex: newAddress.r1_hex || newAddress.R1?.hex,
      r2_hex: newAddress.r2_hex || newAddress.R2?.hex, 
      c_hex: newAddress.c_hex || newAddress.C?.hex
    }
    
    setAddresses(prev => [...prev, normalizedAddress])
  }, [])

  // 添加新交易
  const addTransaction = useCallback((newTransaction) => {
    // 構造完整的交易對象 tx = (addr, R, m, σ)
    const transaction = {
      ...newTransaction,
      id: newTransaction.id || `tx_${Date.now()}`,
      timestamp: new Date().toISOString(),
      status: newTransaction.status || 'pending_verification'
    }
    
    console.log('Adding transaction to global txlist:', transaction)
    setTransactions(prev => [...prev, transaction])
    
    return transaction
  }, [])

  // 重置所有數據
  const resetData = useCallback(() => {
    console.log('Manual reset data called')
    setKeys([])
    setAddresses([])
    setTransactions([])  // 也重置交易列表
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
    transactions,  // 添加 transactions
    loading,
    error,
    
    // 方法
    loadAllData,
    loadKeys,
    loadAddresses,
    addKey,
    addAddress,
    addTransaction,  // 添加 addTransaction
    resetData,
    setError,
    clearError
  }

  console.log('AppDataProvider rendering with:', { 
    keysCount: keys.length, 
    addressesCount: addresses.length,
    loading,
    error 
  })

  return (
    <AppDataContext.Provider value={value}>
      {children}
    </AppDataContext.Provider>
  )
}