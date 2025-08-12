import React from 'react'
import { Section } from '../../components/common/index.jsx'

function SitaibaNoSigning({ title = "🚫 Signing Feature Not Available" }) {
  return (
    <Section title={`${title} (Sitaiba)`} className="card disabled">
      <div className="no-signing-content">
        <div className="no-signing-icon">🔒</div>
        <h3>Sitaiba Scheme Does Not Support This Feature</h3>
        <p>According to the Sitaiba scheme design, this scheme does not include message signing and signature verification functionality.</p>
        <div className="scheme-info">
          <h4>Scheme Differences:</h4>
          <div className="comparison">
            <div className="scheme-column">
              <h5>Stealth Scheme</h5>
              <ul className="supported">
                <li>✅ Message Signing</li>
                <li>✅ Signature Verification</li>
                <li>✅ Complete Feature Set</li>
              </ul>
            </div>
            <div className="scheme-column">
              <h5>Sitaiba Scheme</h5>
              <ul className="not-supported">
                <li>❌ No Message Signing</li>
                <li>❌ No Signature Verification</li>
                <li>✅ Other Features Supported</li>
              </ul>
            </div>
          </div>
        </div>
        <div className="suggestion">
          <p>💡 If you need signing functionality, please switch to the Stealth scheme</p>
        </div>
      </div>
      
      <style>{`
        .no-signing-content {
          text-align: center;
          padding: 2rem;
          color: #666;
        }
        
        .no-signing-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
          color: #dc3545;
        }
        
        .scheme-info {
          margin: 1.5rem 0;
        }
        
        .scheme-info h4 {
          color: #555;
          margin-bottom: 1rem;
        }
        
        .comparison {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 2rem;
          margin-top: 1rem;
        }
        
        .scheme-column {
          text-align: left;
          background: #f8f9fa;
          padding: 1rem;
          border-radius: 4px;
          border-left: 4px solid #007bff;
        }
        
        .scheme-column h5 {
          margin: 0 0 0.5rem 0;
          color: #333;
        }
        
        .scheme-column ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .scheme-column li {
          margin-bottom: 0.25rem;
          font-size: 14px;
        }
        
        .supported li {
          color: #28a745;
        }
        
        .not-supported li {
          color: #dc3545;
        }
        
        .suggestion {
          margin-top: 1.5rem;
          padding: 1rem;
          background: #e3f2fd;
          border-radius: 4px;
          border-left: 4px solid #2196f3;
        }
        
        .suggestion p {
          margin: 0;
          color: #1565c0;
          font-weight: 500;
        }
        
        :global(.card.disabled) {
          opacity: 0.7;
          background-color: #f8f9fa;
        }
      `}</style>
    </Section>
  )
}

export default SitaibaNoSigning