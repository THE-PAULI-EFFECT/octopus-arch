import Head from 'next/head'
import { useState, useEffect } from 'react'

export default function Home() {
  const [apiStatus, setApiStatus] = useState('checking...')
  const [apiData, setApiData] = useState(null)

  useEffect(() => {
    // Check API health
    const checkApi = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/health`)
        if (response.ok) {
          const data = await response.json()
          setApiStatus('✅ Connected')
          setApiData(data)
        } else {
          setApiStatus('❌ Error')
        }
      } catch (error) {
        setApiStatus('⚠️ Backend not running (expected for static preview)')
      }
    }
    checkApi()
  }, [])

  return (
    <div className="container">
      <Head>
        <title>Octopus Architecture - Trust-Based Service Marketplace</title>
        <meta name="description" content="Trust-based, agent-driven smart directory for verified service providers" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="main">
        <div className="header">
          <h1 className="title">
            🐙 Octopus Architecture
          </h1>
          <p className="subtitle">Trust-Based Service Marketplace</p>
        </div>

        <div className="pitch">
          <h2>We don't sell ads. We don't sell software.</h2>
          <h2>We deliver verified customers to verified businesses —</h2>
          <h2>and we only get paid when they win.</h2>
        </div>

        <div className="status-card">
          <h3>System Status</h3>
          <p><strong>Backend API:</strong> {apiStatus}</p>
          {apiData && (
            <>
              <p><strong>Version:</strong> {apiData.version}</p>
              <p><strong>Environment:</strong> {apiData.environment}</p>
              <p><strong>City:</strong> {apiData.city || 'Seattle'}</p>
            </>
          )}
        </div>

        <div className="features">
          <h2>Key Features</h2>
          <div className="feature-grid">
            <div className="feature">
              <h3>✓ Trust-Gated</h3>
              <p>Human + AI verification</p>
            </div>
            <div className="feature">
              <h3>✓ Performance-Based</h3>
              <p>3-7% commission only</p>
            </div>
            <div className="feature">
              <h3>✓ Social Purpose</h3>
              <p>Community contribution mandate</p>
            </div>
            <div className="feature">
              <h3>✓ Agent-Native</h3>
              <p>Built for AI agents</p>
            </div>
          </div>
        </div>

        <div className="stats">
          <h2>Business Model</h2>
          <div className="stat-grid">
            <div className="stat">
              <div className="stat-value">96%</div>
              <div className="stat-label">Profit Margin</div>
            </div>
            <div className="stat">
              <div className="stat-value">$4,320</div>
              <div className="stat-label">Per Provider/Year</div>
            </div>
            <div className="stat">
              <div className="stat-value">8.8/10</div>
              <div className="stat-label">System Quality</div>
            </div>
          </div>
        </div>

        <div className="cta">
          <h2>Seattle Metro P0 Launch</h2>
          <p>Target: 250 providers | 11 service niches | 7 languages</p>
          <div className="button-group">
            <a href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/docs`} className="button primary">
              API Documentation
            </a>
            <a href="https://github.com/THE-PAULI-EFFECT/octopus-arch" className="button secondary">
              View on GitHub
            </a>
          </div>
        </div>

        <div className="architecture">
          <h2>The "Octopus" Model</h2>
          <pre className="architecture-diagram">{`
        ┌─────────────────────────────────────┐
        │      Control Plane (Head)           │
        │  OpenHands + Agent Zero + Diffy     │
        └──────────┬──────────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     ┌─────┐   ┌─────┐   ┌─────┐
     │ SEA │   │ PDX │   │ SF  │  ... (Each = City)
     └─────┘   └─────┘   └─────┘
          `}</pre>
          <p>One system, infinite cities. Replicable in 2 weeks.</p>
        </div>

        <footer className="footer">
          <p>Octopus Architecture | Washington State Social Purpose Corporation</p>
          <p>Built with OpenHands • Powered by Claude Sonnet 4.5</p>
        </footer>
      </main>

      <style jsx>{`
        .container {
          min-height: 100vh;
          padding: 0 0.5rem;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .main {
          padding: 5rem 0;
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          max-width: 1200px;
          width: 100%;
        }

        .header {
          text-align: center;
          margin-bottom: 3rem;
        }

        .title {
          margin: 0;
          line-height: 1.15;
          font-size: 4rem;
          color: white;
          text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .subtitle {
          font-size: 1.5rem;
          color: rgba(255,255,255,0.9);
          margin-top: 0.5rem;
        }

        .pitch {
          background: white;
          border-radius: 10px;
          padding: 2rem;
          margin: 2rem 0;
          box-shadow: 0 10px 40px rgba(0,0,0,0.2);
          text-align: center;
        }

        .pitch h2 {
          margin: 0.5rem 0;
          font-size: 1.5rem;
          color: #333;
          font-weight: 600;
        }

        .status-card {
          background: white;
          border-radius: 10px;
          padding: 2rem;
          margin: 2rem 0;
          box-shadow: 0 10px 40px rgba(0,0,0,0.2);
          width: 100%;
          max-width: 600px;
        }

        .status-card h3 {
          margin-top: 0;
          color: #667eea;
        }

        .features, .stats, .cta, .architecture {
          background: white;
          border-radius: 10px;
          padding: 2rem;
          margin: 2rem 0;
          box-shadow: 0 10px 40px rgba(0,0,0,0.2);
          width: 100%;
        }

        .feature-grid, .stat-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
          margin-top: 1.5rem;
        }

        .feature, .stat {
          text-align: center;
          padding: 1rem;
          background: #f7f7f7;
          border-radius: 8px;
        }

        .feature h3 {
          color: #667eea;
          margin-bottom: 0.5rem;
        }

        .stat-value {
          font-size: 3rem;
          font-weight: bold;
          color: #667eea;
        }

        .stat-label {
          font-size: 0.9rem;
          color: #666;
          margin-top: 0.5rem;
        }

        .cta {
          text-align: center;
        }

        .button-group {
          display: flex;
          gap: 1rem;
          justify-content: center;
          margin-top: 1.5rem;
          flex-wrap: wrap;
        }

        .button {
          padding: 1rem 2rem;
          border-radius: 8px;
          text-decoration: none;
          font-weight: 600;
          transition: transform 0.2s;
          display: inline-block;
        }

        .button:hover {
          transform: translateY(-2px);
        }

        .button.primary {
          background: #667eea;
          color: white;
        }

        .button.secondary {
          background: #764ba2;
          color: white;
        }

        .architecture-diagram {
          background: #f7f7f7;
          padding: 1.5rem;
          border-radius: 8px;
          overflow-x: auto;
          font-size: 0.85rem;
        }

        .footer {
          margin-top: 3rem;
          padding: 2rem 0;
          text-align: center;
          color: rgba(255,255,255,0.9);
        }

        @media (max-width: 768px) {
          .title {
            font-size: 2.5rem;
          }
          .pitch h2 {
            font-size: 1.2rem;
          }
          .button-group {
            flex-direction: column;
          }
        }
      `}</style>

      <style jsx global>{`
        html,
        body {
          padding: 0;
          margin: 0;
          font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto,
            Oxygen, Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue,
            sans-serif;
        }

        * {
          box-sizing: border-box;
        }
      `}</style>
    </div>
  )
}
