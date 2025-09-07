import React, { useState, useEffect } from 'react'
import { Section, Button, DataList, Output } from '../../components/common'
import { useAppData } from '../../hooks/useAppData'
import { apiService } from '../../services/apiService'
import { truncateHex } from '../../utils/helpers'

function HdwsaKeyManagement() {
  const { keys, addKey, loadKeys, loading: globalLoading, error: globalError, setError } = useAppData()
  const [selectedKeyIndex, setSelectedKeyIndex] = useState(-1)
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')
  const [walletTree, setWalletTree] = useState(null)

  // 載入錢包樹結構
  useEffect(() => {
    if (keys.length > 0) {
      loadWalletTree()
    }
  }, [keys])

  const loadWalletTree = async () => {
    try {
      setLocalLoading(prev => ({ ...prev, walletTree: true }))
      const tree = await apiService.getWalletTree()
      setWalletTree(tree)
    } catch (err) {
      console.warn('Failed to load wallet tree:', err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, walletTree: false }))
    }
  }

  const handleGenerateWallet = async () => {
    try {
      setLocalLoading(prev => ({ ...prev, keygen: true }))
      setLocalError('')
      setError('')
      
      const newWallet = await apiService.generateKey()
      addKey(newWallet)
      
    } catch (err) {
      setLocalError('Wallet generation failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, keygen: false }))
    }
  }

  const handleRefreshWallets = async () => {
    setLocalError('')
    setError('')
    await loadKeys()
    await loadWalletTree()
  }

  const handleWalletClick = (index) => {
    setSelectedKeyIndex(index)
  }

  const getWalletLevel = (walletId) => {
    if (!walletId) return 0
    return walletId.split(',').length - 1
  }

  const getWalletParent = (walletId) => {
    if (!walletId || !walletId.includes(',')) return null
    const parts = walletId.split(',')
    return parts.slice(0, -1).join(',')
  }

  const getOutputContent = () => {
    // 使用 localError 或 globalError
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (selectedKeyIndex >= 0 && keys[selectedKeyIndex]) {
      const wallet = keys[selectedKeyIndex]
      const level = getWalletLevel(wallet.full_id)
      const parent = getWalletParent(wallet.full_id)
      
      return `🔍 Wallet Details - ${wallet.full_id}
🆔 Index: ${selectedKeyIndex}
🏗️ Hierarchical Level: ${level} ${level === 0 ? '(Root Level)' : '(Child Wallet)'}
${parent ? `👤 Parent Wallet: ${parent}` : ''}
📄 Parameter File: ${wallet.param_file || 'Unknown'}
📊 Status: ${wallet.status}

🔓 Public Key A:
${wallet.A_hex}

🔓 Public Key B:
${wallet.B_hex}

🔐 Private Key alpha:
${wallet.alpha_hex}

🔐 Private Key beta:
${wallet.beta_hex}`
    }
    
    if (selectedKeyIndex >= 0 && keys && keys[selectedKeyIndex]) {
      const wallet = keys[selectedKeyIndex]
      return format_wallet_info(wallet)
    }
    
    // 顯示最新生成的錢包信息
    if (keys && keys.length > 0) {
      const latestWallet = keys[keys.length - 1]
      const level = getWalletLevel(latestWallet.full_id)
      return `✅ User Wallet Generated Successfully!
🆔 Wallet ID: ${latestWallet.full_id}
🏗️ Level: ${level} ${level === 0 ? '(Root Level User Wallet)' : '(Child Wallet)'}
🔓 Public Key A: ${truncateHex(latestWallet.A_hex)}
🔓 Public Key B: ${truncateHex(latestWallet.B_hex)}
🔐 Private Key alpha: ${truncateHex(latestWallet.alpha_hex)}
🔐 Private Key beta: ${truncateHex(latestWallet.beta_hex)}`
    }
    
    return ''
  }

  const walletItems = keys.map((wallet, index) => {
    const level = getWalletLevel(wallet.full_id)
    const levelIcon = level === 0 ? '🏠' : '📁'.repeat(level)
    const parent = getWalletParent(wallet.full_id)
    
    return {
      id: wallet.full_id,
      header: `${levelIcon} ${wallet.full_id}`,
      details: [
        `Level: ${level}`,
        parent ? `Parent: ${parent}` : 'Root Level',
        `A: ${truncateHex(wallet.A_hex, 12)}`,
        `B: ${truncateHex(wallet.B_hex, 12)}`
      ],
      selected: index === selectedKeyIndex,
      onClick: () => handleWalletClick(index)
    }
  })

  return (
    <Section title="🏗️ Hierarchical Wallet Management (HDWSA)">
      <div className="controls">
        <Button
          onClick={handleGenerateWallet}
          loading={localLoading.keygen || globalLoading.keys}
          disabled={localLoading.keygen || globalLoading.keys}
        >
          🔑 Generate User Wallet
        </Button>
        <Button
          onClick={handleRefreshWallets}
          variant="secondary"
          loading={localLoading.walletTree}
        >
          🔄 Refresh Wallets
        </Button>
      </div>

      {walletTree && (
        <div className="wallet-tree-info">
          <h4>📊 Wallet Tree Summary</h4>
          <div className="tree-stats">
            <span className="stat-item">
              📁 Total Wallets: {walletTree.total_wallets}
            </span>
            <span className="stat-item">
              🎯 Scheme: {walletTree.scheme.toUpperCase()}
            </span>
          </div>
        </div>
      )}
      
      <DataList items={walletItems} />
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />

      

      <style jsx>{`
        .controls {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1rem;
          flex-wrap: wrap;
        }

        .wallet-tree-info {
          background: #e7f3ff;
          border: 1px solid #b3d9ff;
          border-radius: 4px;
          padding: 0.75rem;
          margin-bottom: 1rem;
        }

        .wallet-tree-info h4 {
          margin: 0 0 0.5rem 0;
          color: #0056b3;
          font-size: 14px;
        }

        .tree-stats {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .stat-item {
          font-size: 12px;
          background: #ffffff;
          border: 1px solid #b3d9ff;
          border-radius: 3px;
          padding: 0.25rem 0.5rem;
          color: #495057;
        }

        .hdwsa-info {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 4px;
          padding: 1rem;
          margin-top: 1rem;
        }

        .hdwsa-info h4 {
          margin: 0 0 0.75rem 0;
          color: #495057;
          font-size: 14px;
        }

        .info-content p {
          margin: 0.5rem 0;
          font-size: 13px;
          line-height: 1.4;
          color: #6c757d;
        }

        .info-content strong {
          color: #495057;
        }
      `}</style>
    </Section>
  )
}

export default HdwsaKeyManagement