import Dashboard from '../components/Dashboard';

const Analytics = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Analytics Dashboard
          </h1>
          <p className="text-lg text-gray-600">
            Insights and metrics for your support ticket analysis
          </p>
        </div>

        {/* Dashboard Content */}
        <Dashboard />
      </div>
    </div>
  );
};

export default Analytics;
