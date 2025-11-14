import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { TrendingUp, Users, MessageSquare, Clock, Loader2 } from 'lucide-react';
import api from '../api/axiosConfig';

const Dashboard = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/analytics/summary');
      setAnalyticsData(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError('Failed to load analytics data');
      // Use mock data as fallback
      setAnalyticsData({
        ticket_count_by_priority: { High: 15, Medium: 42, Low: 28 },
        top_articles_usage: [
          { article: "How to reset password", usage_count: 45 },
          { article: "Troubleshooting login issues", usage_count: 38 },
          { article: "Account verification guide", usage_count: 32 },
          { article: "Payment processing help", usage_count: 28 },
          { article: "Feature request process", usage_count: 25 },
          { article: "API integration guide", usage_count: 22 },
          { article: "Data export instructions", usage_count: 18 },
          { article: "Security best practices", usage_count: 15 },
          { article: "Billing FAQ", usage_count: 12 },
          { article: "General troubleshooting", usage_count: 10 },
        ],
        language_distribution: [
          { language: "English", count: 65, percentage: 65.0 },
          { language: "Spanish", count: 12, percentage: 12.0 },
          { language: "French", count: 10, percentage: 10.0 },
          { language: "German", count: 8, percentage: 8.0 },
          { language: "Chinese", count: 5, percentage: 5.0 },
        ],
        total_tickets: 85
      });
    } finally {
      setLoading(false);
    }
  };

  // Prepare data for charts
  const priorityData = analyticsData ? [
    { name: 'High', count: analyticsData.ticket_count_by_priority.High || 0, color: '#ef4444' },
    { name: 'Medium', count: analyticsData.ticket_count_by_priority.Medium || 0, color: '#f59e0b' },
    { name: 'Low', count: analyticsData.ticket_count_by_priority.Low || 0, color: '#10b981' },
  ] : [];

  const articlesData = analyticsData?.top_articles_usage || [];
  
  const languageData = analyticsData?.language_distribution || [];
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'];

  const stats = analyticsData ? [
    { label: 'Total Tickets', value: analyticsData.total_tickets || 0, icon: MessageSquare, color: 'text-blue-600' },
    { label: 'High Priority', value: analyticsData.ticket_count_by_priority?.High || 0, icon: TrendingUp, color: 'text-red-600' },
    { label: 'Medium Priority', value: analyticsData.ticket_count_by_priority?.Medium || 0, icon: Clock, color: 'text-yellow-600' },
    { label: 'Low Priority', value: analyticsData.ticket_count_by_priority?.Low || 0, icon: Users, color: 'text-green-600' },
  ] : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        <span className="ml-3 text-gray-600">Loading analytics...</span>
      </div>
    );
  }

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
        {/* Ticket Count by Priority */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Tickets by Priority</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={priorityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]}>
                {priorityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Language Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Language Distribution</h3>
          {languageData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={languageData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ language, percentage }) => `${language}: ${percentage}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {languageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name, props) => [
                  `${props.payload.language}: ${value} (${props.payload.percentage}%)`,
                  'Count'
                ]} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-500">
              No language data available
            </div>
          )}
        </div>
      </div>

      {/* Top 10 Articles Usage */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top 10 Recommended Articles Usage</h3>
        {articlesData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart 
              data={articlesData} 
              layout="vertical"
              margin={{ top: 5, right: 30, left: 200, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis 
                dataKey="article" 
                type="category" 
                width={180}
                tick={{ fontSize: 12 }}
              />
              <Tooltip />
              <Bar dataKey="usage_count" fill="#3b82f6" radius={[0, 8, 8, 0]}>
                {articlesData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-[400px] text-gray-500">
            No article usage data available
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
