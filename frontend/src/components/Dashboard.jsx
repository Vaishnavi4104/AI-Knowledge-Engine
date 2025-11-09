import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { TrendingUp, Users, MessageSquare, Clock } from 'lucide-react';

const Dashboard = () => {
  // Mock data for charts
  const ticketData = [
    { name: 'Jan', tickets: 45, resolved: 42 },
    { name: 'Feb', tickets: 52, resolved: 48 },
    { name: 'Mar', tickets: 38, resolved: 35 },
    { name: 'Apr', tickets: 61, resolved: 58 },
    { name: 'May', tickets: 47, resolved: 44 },
    { name: 'Jun', tickets: 55, resolved: 52 },
  ];

  const categoryData = [
    { name: 'Technical Issues', value: 35, color: '#3b82f6' },
    { name: 'Account Problems', value: 25, color: '#10b981' },
    { name: 'Billing Questions', value: 20, color: '#f59e0b' },
    { name: 'Feature Requests', value: 15, color: '#ef4444' },
    { name: 'Other', value: 5, color: '#8b5cf6' },
  ];

  const responseTimeData = [
    { name: 'Week 1', avgTime: 2.5 },
    { name: 'Week 2', avgTime: 2.2 },
    { name: 'Week 3', avgTime: 1.8 },
    { name: 'Week 4', avgTime: 1.5 },
  ];

  const stats = [
    { label: 'Total Tickets', value: '342', icon: MessageSquare, color: 'text-blue-600' },
    { label: 'Resolved', value: '318', icon: TrendingUp, color: 'text-green-600' },
    { label: 'Avg Response Time', value: '1.8h', icon: Clock, color: 'text-yellow-600' },
    { label: 'Customer Satisfaction', value: '94%', icon: Users, color: 'text-purple-600' },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-full bg-gray-50 ${stat.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ticket Volume Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Ticket Volume</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={ticketData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="tickets" fill="#3b82f6" name="Total Tickets" />
              <Bar dataKey="resolved" fill="#10b981" name="Resolved" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Category Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Ticket Categories</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Response Time Trend */}
        <div className="card lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Average Response Time Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={responseTimeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="avgTime" 
                stroke="#3b82f6" 
                strokeWidth={2}
                name="Hours"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity Placeholder */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((item) => (
            <div key={item} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-600">
                Ticket #{1000 + item} resolved - Technical Issue
              </span>
              <span className="text-xs text-gray-400 ml-auto">2 hours ago</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
