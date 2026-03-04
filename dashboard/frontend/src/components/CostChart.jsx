import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'
import { AGENTS } from '../utils/constants'

export function StackedCostChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-64 text-muted-foreground text-sm">No cost data yet</div>
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(35 12% 85%)" />
        <XAxis dataKey="date" tick={{ fill: 'hsl(30 8% 50%)', fontSize: 12 }} tickFormatter={d => d?.slice(5)} />
        <YAxis tick={{ fill: 'hsl(30 8% 50%)', fontSize: 12 }} tickFormatter={v => `$${v.toFixed(2)}`} />
        <Tooltip
          contentStyle={{ backgroundColor: 'hsl(40 25% 99%)', border: '1px solid hsl(35 12% 88%)', borderRadius: '8px' }}
          labelStyle={{ color: '#555' }}
          formatter={(v) => [`$${Number(v).toFixed(4)}`, '']}
        />
        <Legend />
        {Object.entries(AGENTS).map(([key, agent]) => (
          <Bar key={key} dataKey={key} stackId="a" fill={agent.color} name={agent.name.split('—')[0].trim()} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}

export function CumulativeCostChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-64 text-muted-foreground text-sm">No cost data yet</div>
  }

  const agentKeys = Object.keys(AGENTS)
  let cumulative = 0
  const cumData = data.map(d => {
    const dayTotal = agentKeys.reduce((sum, k) => sum + (d[k] || 0), 0)
    cumulative += dayTotal
    return { date: d.date, total: cumulative }
  })

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={cumData}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(35 12% 85%)" />
        <XAxis dataKey="date" tick={{ fill: 'hsl(30 8% 50%)', fontSize: 12 }} tickFormatter={d => d?.slice(5)} />
        <YAxis tick={{ fill: 'hsl(30 8% 50%)', fontSize: 12 }} tickFormatter={v => `$${v.toFixed(2)}`} />
        <Tooltip
          contentStyle={{ backgroundColor: 'hsl(40 25% 99%)', border: '1px solid hsl(35 12% 88%)', borderRadius: '8px' }}
          formatter={(v) => [`$${Number(v).toFixed(4)}`, 'Cumulative']}
        />
        <Line type="monotone" dataKey="total" stroke="#7C5CBF" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}
