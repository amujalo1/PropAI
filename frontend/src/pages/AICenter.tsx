/**
 * AI Center page - all AI features in one place
 */
import { useState } from 'react'
import { useProperties } from '@/hooks/useProperties'
import { useValuation, useMarketAnalysis, useRiskAssessment, usePricePrediction, useAIInsights } from '@/hooks/useAI'

type Tab = 'insights' | 'valuation' | 'market' | 'risk' | 'prediction'

function Badge({ text, color }: { text: string; color: string }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${color}`}>
      {text}
    </span>
  )
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>
      {children}
    </div>
  )
}

// ─── Insights Tab ────────────────────────────────────────────────────────────
function InsightsTab() {
  const { data, isLoading, refetch } = useAIInsights()

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-gray-500 text-sm">Portfolio-wide AI analysis</p>
        <button
          onClick={() => refetch()}
          className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-gray-400">Analysing portfolio...</div>
      ) : data ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <SectionCard title="Market Sentiment">
            <div className="flex items-center gap-3">
              <span className="text-4xl">
                {data.market_sentiment === 'Positive' ? '📈' : data.market_sentiment === 'Cautious' ? '⚠️' : '➡️'}
              </span>
              <div>
                <p className="text-2xl font-bold">{data.market_sentiment}</p>
                <p className="text-sm text-gray-500">Current market outlook</p>
              </div>
            </div>
          </SectionCard>

          <SectionCard title="Portfolio Performance">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Properties analysed</span>
                <span className="font-semibold">{data.total_properties_analyzed}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Avg value change</span>
                <span className={`font-semibold ${data.avg_portfolio_value_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {data.avg_portfolio_value_change >= 0 ? '+' : ''}{data.avg_portfolio_value_change}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Top performing type</span>
                <span className="font-semibold capitalize">{data.top_performing_type}</span>
              </div>
            </div>
          </SectionCard>

          <div className="md:col-span-2">
            <SectionCard title="AI Recommendations">
              <ul className="space-y-2">
                {data.ai_recommendations?.map((rec: string, i: number) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-blue-500 mt-0.5">💡</span>
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
              <p className="mt-4 text-xs text-gray-400 italic">{data.note}</p>
            </SectionCard>
          </div>
        </div>
      ) : null}
    </div>
  )
}

// ─── Valuation Tab ───────────────────────────────────────────────────────────
function ValuationTab({ properties }: { properties: any[] }) {
  const [selectedId, setSelectedId] = useState('')
  const mutation = useValuation()

  const handleRun = () => {
    if (selectedId) mutation.mutate(selectedId)
  }

  const d = mutation.data

  return (
    <div className="space-y-4">
      <p className="text-gray-500 text-sm">Get an AI-estimated market value for any property.</p>

      <div className="flex gap-3">
        <select
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
          className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:border-blue-500"
        >
          <option value="">Select a property...</option>
          {properties.map((p) => (
            <option key={p.id} value={p.id}>{p.name} — €{Number(p.price).toLocaleString()}</option>
          ))}
        </select>
        <button
          onClick={handleRun}
          disabled={!selectedId || mutation.isPending}
          className="px-5 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Analysing...' : 'Run Valuation'}
        </button>
      </div>

      {d && (
        <SectionCard title="Valuation Result">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-blue-50 rounded p-4 text-center">
              <p className="text-sm text-gray-500">Estimated Value</p>
              <p className="text-3xl font-bold text-blue-700">€{d.estimated_value.toLocaleString()}</p>
            </div>
            <div className="bg-green-50 rounded p-4 text-center">
              <p className="text-sm text-gray-500">Confidence</p>
              <p className="text-3xl font-bold text-green-700">{Math.round(d.confidence * 100)}%</p>
            </div>
          </div>
          <div className="space-y-2 text-sm">
            {Object.entries(d.factors).map(([k, v]) => (
              <div key={k} className="flex justify-between border-b border-gray-100 pb-1">
                <span className="text-gray-500 capitalize">{k.replace(/_/g, ' ')}</span>
                <span className="font-medium">{String(v)}</span>
              </div>
            ))}
          </div>
          <p className="mt-3 text-xs text-gray-400 italic">{d.note}</p>
        </SectionCard>
      )}
    </div>
  )
}

// ─── Market Analysis Tab ─────────────────────────────────────────────────────
function MarketTab() {
  const [location, setLocation] = useState('')
  const [type, setType] = useState('residential')
  const mutation = useMarketAnalysis()

  const d = mutation.data

  return (
    <div className="space-y-4">
      <p className="text-gray-500 text-sm">Analyse market conditions for any location and property type.</p>

      <div className="grid grid-cols-2 gap-3">
        <input
          type="text"
          placeholder="Location (e.g. Sarajevo, Downtown)"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:border-blue-500"
        />
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:border-blue-500"
        >
          <option value="residential">Residential</option>
          <option value="commercial">Commercial</option>
          <option value="land">Land</option>
        </select>
      </div>
      <button
        onClick={() => mutation.mutate({ location, property_type: type })}
        disabled={!location || mutation.isPending}
        className="px-5 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {mutation.isPending ? 'Analysing...' : 'Analyse Market'}
      </button>

      {d && (
        <SectionCard title={`Market Analysis — ${d.location}`}>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-gray-50 rounded p-3 text-center">
              <p className="text-xs text-gray-500">Avg Price/m²</p>
              <p className="text-xl font-bold">€{d.avg_price_per_sqm.toLocaleString()}</p>
            </div>
            <div className="bg-gray-50 rounded p-3 text-center">
              <p className="text-xs text-gray-500">Market Trend</p>
              <p className="text-xl font-bold">{d.market_trend}</p>
            </div>
            <div className="bg-gray-50 rounded p-3 text-center">
              <p className="text-xs text-gray-500">Demand</p>
              <p className="text-xl font-bold">{d.demand_level}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-gray-600 text-sm">6-month price change:</span>
            <span className={`font-bold ${d.price_change_6m >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {d.price_change_6m >= 0 ? '+' : ''}{d.price_change_6m}%
            </span>
          </div>
          <p className="mt-3 text-xs text-gray-400 italic">{d.note}</p>
        </SectionCard>
      )}
    </div>
  )
}

// ─── Risk Assessment Tab ─────────────────────────────────────────────────────
function RiskTab({ properties }: { properties: any[] }) {
  const [selectedId, setSelectedId] = useState('')
  const mutation = useRiskAssessment()

  const d = mutation.data
  const riskColor = d?.risk_level === 'Low' ? 'text-green-600' : d?.risk_level === 'Medium' ? 'text-yellow-600' : 'text-red-600'
  const riskBg = d?.risk_level === 'Low' ? 'bg-green-50' : d?.risk_level === 'Medium' ? 'bg-yellow-50' : 'bg-red-50'

  return (
    <div className="space-y-4">
      <p className="text-gray-500 text-sm">Evaluate investment risk for a property.</p>

      <div className="flex gap-3">
        <select
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
          className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:border-blue-500"
        >
          <option value="">Select a property...</option>
          {properties.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        <button
          onClick={() => mutation.mutate(selectedId)}
          disabled={!selectedId || mutation.isPending}
          className="px-5 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Assessing...' : 'Assess Risk'}
        </button>
      </div>

      {d && (
        <SectionCard title="Risk Assessment">
          <div className={`${riskBg} rounded p-4 flex items-center gap-4 mb-4`}>
            <div className="text-center">
              <p className="text-xs text-gray-500">Risk Score</p>
              <p className={`text-4xl font-bold ${riskColor}`}>{d.risk_score}</p>
              <p className="text-xs text-gray-400">out of 100</p>
            </div>
            <div>
              <p className={`text-2xl font-bold ${riskColor}`}>{d.risk_level} Risk</p>
              <div className="w-48 bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className={`h-2 rounded-full ${d.risk_level === 'Low' ? 'bg-green-500' : d.risk_level === 'Medium' ? 'bg-yellow-500' : 'bg-red-500'}`}
                  style={{ width: `${d.risk_score}%` }}
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-2">Risk Factors</p>
              <ul className="space-y-1">
                {d.factors.map((f: string, i: number) => (
                  <li key={i} className="text-sm text-gray-600 flex gap-2">
                    <span className="text-red-400">⚠</span> {f}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-2">Recommendations</p>
              <ul className="space-y-1">
                {d.recommendations.map((r: string, i: number) => (
                  <li key={i} className="text-sm text-gray-600 flex gap-2">
                    <span className="text-blue-400">✓</span> {r}
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <p className="mt-3 text-xs text-gray-400 italic">{d.note}</p>
        </SectionCard>
      )}
    </div>
  )
}

// ─── Price Prediction Tab ────────────────────────────────────────────────────
function PredictionTab({ properties }: { properties: any[] }) {
  const [selectedId, setSelectedId] = useState('')
  const [months, setMonths] = useState(6)
  const mutation = usePricePrediction()

  const d = mutation.data

  return (
    <div className="space-y-4">
      <p className="text-gray-500 text-sm">Predict future property value based on market trends.</p>

      <div className="flex gap-3">
        <select
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
          className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:border-blue-500"
        >
          <option value="">Select a property...</option>
          {properties.map((p) => (
            <option key={p.id} value={p.id}>{p.name} — €{Number(p.price).toLocaleString()}</option>
          ))}
        </select>
        <select
          value={months}
          onChange={(e) => setMonths(Number(e.target.value))}
          className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:border-blue-500"
        >
          <option value={3}>3 months</option>
          <option value={6}>6 months</option>
          <option value={12}>12 months</option>
          <option value={24}>24 months</option>
        </select>
        <button
          onClick={() => mutation.mutate({ property_id: selectedId, months_ahead: months })}
          disabled={!selectedId || mutation.isPending}
          className="px-5 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Predicting...' : 'Predict'}
        </button>
      </div>

      {d && (
        <SectionCard title={`Price Prediction — ${d.months_ahead} months`}>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="bg-gray-50 rounded p-4 text-center">
              <p className="text-xs text-gray-500">Current Value</p>
              <p className="text-xl font-bold">€{d.current_value.toLocaleString()}</p>
            </div>
            <div className="bg-blue-50 rounded p-4 text-center">
              <p className="text-xs text-gray-500">Predicted Value</p>
              <p className="text-xl font-bold text-blue-700">€{d.predicted_value.toLocaleString()}</p>
            </div>
            <div className={`rounded p-4 text-center ${d.change_percent >= 0 ? 'bg-green-50' : 'bg-red-50'}`}>
              <p className="text-xs text-gray-500">Change</p>
              <p className={`text-xl font-bold ${d.change_percent >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                {d.change_percent >= 0 ? '+' : ''}{d.change_percent}%
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-gray-600 text-sm">Trend:</span>
            <span className={`font-semibold ${d.trend === 'Upward' ? 'text-green-600' : d.trend === 'Downward' ? 'text-red-600' : 'text-gray-600'}`}>
              {d.trend === 'Upward' ? '↑' : d.trend === 'Downward' ? '↓' : '→'} {d.trend}
            </span>
          </div>
          <p className="mt-3 text-xs text-gray-400 italic">{d.note}</p>
        </SectionCard>
      )}
    </div>
  )
}

// ─── Main Page ───────────────────────────────────────────────────────────────
export function AICenter() {
  const [activeTab, setActiveTab] = useState<Tab>('insights')
  const { data: propertiesData } = useProperties(100, 0)
  const properties = propertiesData?.data || []

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'insights', label: 'Portfolio Insights', icon: '🧠' },
    { id: 'valuation', label: 'Property Valuation', icon: '💰' },
    { id: 'market', label: 'Market Analysis', icon: '📊' },
    { id: 'risk', label: 'Risk Assessment', icon: '⚠️' },
    { id: 'prediction', label: 'Price Prediction', icon: '🔮' },
  ]

  return (
    <div className="p-8">
      <div className="flex items-center gap-3 mb-2">
        <span className="text-3xl">🤖</span>
        <h1 className="text-3xl font-bold">AI Center</h1>
        <span className="px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs rounded font-medium">MOCK</span>
      </div>
      <p className="text-gray-500 mb-6">AI-powered real estate intelligence. All results are simulated for MVP.</p>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg mb-6 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? 'bg-white text-blue-700 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'insights' && <InsightsTab />}
        {activeTab === 'valuation' && <ValuationTab properties={properties} />}
        {activeTab === 'market' && <MarketTab />}
        {activeTab === 'risk' && <RiskTab properties={properties} />}
        {activeTab === 'prediction' && <PredictionTab properties={properties} />}
      </div>
    </div>
  )
}
