import React, { useState, createContext, useContext } from 'react'
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
  const [loading, setLoading] = useState({})
  const [error, setError] = useState('')

  // 載入密鑰
  const loadKeys = async () => {
    try {
      setLoading(prev => ({ ...prev, keys: true }))
      const keyData = await apiService.getKeys()
      setKeys(keyData)
    } catch (err) {
      console.error('Failed to load keys:', err)
      setError('Failed to load keys: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, keys: false }))
    }
  }

  // 載入地址
  const loadAddresses = async () => {
    try {
      setLoading(prev => ({ ...prev, addresses: true }))
      const addressData = await apiService.get('/addresslist')
      setAddresses(addressData)
    } catch (err) {
      console.error('Failed to load addresses:', err)
      setError('Failed to load addresses: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, addresses: false }))
    }
  }

  // 載入所有數據
  const loadAllData = async () => {
    try {
      setLoading(prev => ({ ...prev, all: true }))
      setError('')
      
      await Promise.all([
        loadKeys(),
        loadAddresses()
      ])
      
    } catch (err) {
      console.error('Data loading error:', err)
      setError('Failed to load data: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, all: false }))
    }
  }

  // 添加新密鑰
  const addKey = (newKey) => {
    setKeys(prev => [...prev, newKey])
  }

  // 添加新地址
  const addAddress = (newAddress) => {
    setAddresses(prev => [...prev, newAddress])
  }

  // 重置所有數據（禁用自動調用）
  const resetData = () => {
    console.log('Manual reset data called')
    setKeys([])
    setAddresses([])
    setError('')
  }

  const value = {
    // 數據
    keys,
    addresses,
    loading,
    error,
    
    // 方法
    loadAllData,
    loadKeys,
    loadAddresses,
    addKey,
    addAddress,
    resetData,
    setError
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