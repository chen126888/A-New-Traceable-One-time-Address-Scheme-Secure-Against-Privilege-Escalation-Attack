import React from 'react'

// Card組件
export function Card({ title, children, className = '', ...props }) {
  return (
    <div className={`card ${className}`} {...props}>
      {title && <div className="card-header">
        <h3 className="card-title">{title}</h3>
      </div>}
      <div className="card-content">
        {children}
      </div>
    </div>
  )
}

// Section組件
export function Section({ title, children, statusActive = false, className = '', wide = false }) {
  const sectionClass = `section ${wide ? 'wide-section' : ''} ${className}`
  
  return (
    <div className={sectionClass}>
      <h3 className="section-title">
        {statusActive && <span className="status-indicator active"></span>}
        {title}
      </h3>
      {children}
    </div>
  )
}

// Button組件
export function Button({ 
  children, 
  onClick, 
  loading = false, 
  disabled = false, 
  variant = 'primary',
  className = '',
  ...props 
}) {
  const buttonClass = `button ${variant} ${className} ${loading ? 'loading' : ''}`
  
  return (
    <button
      className={buttonClass}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <span className="loading-spinner"></span>}
      {children}
    </button>
  )
}

// Select組件
export function Select({ children, value, onChange, disabled = false, className = '', ...props }) {
  return (
    <select
      className={`select ${className}`}
      value={value}
      onChange={onChange}
      disabled={disabled}
      {...props}
    >
      {children}
    </select>
  )
}

// Input組件
export function Input({ 
  type = 'text', 
  value, 
  onChange, 
  placeholder = '', 
  disabled = false,
  className = '',
  ...props 
}) {
  return (
    <input
      type={type}
      className={`input ${className}`}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      {...props}
    />
  )
}

// Output組件
export function Output({ content, isError = false, className = '' }) {
  if (!content) return null
  
  const outputClass = `output ${isError ? 'error' : 'success'} ${className}`
  
  return (
    <div className={outputClass}>
      {content}
    </div>
  )
}

// DataList組件
export function DataList({ items = [], className = '' }) {
  if (items.length === 0) return null
  
  return (
    <div className={`data-list ${className}`}>
      {items.map((item, index) => (
        <div
          key={item.id || index}
          className={`data-item ${item.selected ? 'selected' : ''}`}
          onClick={item.onClick}
        >
          <div className="item-header">{item.header}</div>
          {item.details && item.details.map((detail, detailIndex) => (
            <div key={detailIndex} className="item-details">
              {detail}
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}