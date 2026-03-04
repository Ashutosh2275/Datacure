import { Card } from '../components/Common'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line, ResponsiveContainer } from 'recharts'

function AIPage() {
  const data = [
    { name: 'Jan', risk: 40, prediction: 24 },
    { name: 'Feb', risk: 30, prediction: 13 },
    { name: 'Mar', risk: 20, prediction: 98 },
  ]

  return (
    <div className="container-custom py-8">
      <h1 className="text-3xl font-bold mb-6">AI Analytics & Predictions</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Patient Risk Scores">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="risk" stackId="a" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Predictions">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="prediction" stroke="#0ea5e9" />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  )
}

export default AIPage
