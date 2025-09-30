/**
 * Member Dashboard - Primary landing page after login
 */
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Activity,
  Heart,
  TrendingDown,
  Award,
  AlertCircle,
  CheckCircle,
  DollarSign,
} from 'lucide-react';
import { apiClient } from '@/services/api';
import { formatCurrency, formatDate } from '@/utils/formatting';

export const Dashboard: React.FC = () => {
  // Fetch member data
  const { data: member, isLoading: memberLoading } = useQuery({
    queryKey: ['member', 'current'],
    queryFn: () => apiClient.getCurrentMember(),
  });

  // Fetch current health score
  const { data: healthScore, isLoading: scoreLoading } = useQuery({
    queryKey: ['health-score', member?.member_id],
    queryFn: () => apiClient.getCurrentHealthScore(member!.member_id),
    enabled: !!member,
  });

  // Fetch premium info
  const { data: premiumInfo } = useQuery({
    queryKey: ['premium', member?.member_id],
    queryFn: () => apiClient.getPremiumInfo(member!.member_id),
    enabled: !!member,
  });

  // Fetch rebates
  const { data: rebates } = useQuery({
    queryKey: ['rebates', member?.member_id],
    queryFn: () => apiClient.getRebates(member!.member_id),
    enabled: !!member,
  });

  // Fetch enrollments
  const { data: enrollments } = useQuery({
    queryKey: ['enrollments', member?.member_id],
    queryFn: () => apiClient.getMyEnrollments(member!.member_id),
    enabled: !!member,
  });

  if (memberLoading || scoreLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-vitanexus-primary"></div>
      </div>
    );
  }

  const getRiskCategoryColor = (category?: string) => {
    switch (category) {
      case 'low':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'moderate':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'high':
        return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskCategoryIcon = (category?: string) => {
    if (category === 'low') return <CheckCircle className="w-5 h-5" />;
    if (category === 'critical' || category === 'high') return <AlertCircle className="w-5 h-5" />;
    return <Activity className="w-5 h-5" />;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {member?.first_name}!
              </h1>
              <p className="text-gray-600 mt-1">
                Member since {formatDate(member?.enrollment_date || '')}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Monthly Premium</p>
              <p className="text-2xl font-bold text-vitanexus-primary">
                {formatCurrency(premiumInfo?.monthly_premium || 0)}
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Health Score Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Heart className="w-5 h-5 text-vitanexus-primary mr-2" />
                <h3 className="text-sm font-medium text-gray-600">Health Score</h3>
              </div>
            </div>
            <div className="flex items-baseline">
              <p className="text-4xl font-bold text-gray-900">
                {healthScore?.score.toFixed(0)}
              </p>
              <p className="ml-2 text-sm text-gray-500">/100</p>
            </div>
            <div className={`mt-3 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getRiskCategoryColor(healthScore?.risk_category)}`}>
              {getRiskCategoryIcon(healthScore?.risk_category)}
              <span className="ml-2 capitalize">{healthScore?.risk_category} Risk</span>
            </div>
          </div>

          {/* Predicted Cost Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <TrendingDown className="w-5 h-5 text-green-600 mr-2" />
                <h3 className="text-sm font-medium text-gray-600">Predicted Annual Cost</h3>
              </div>
            </div>
            <div className="flex items-baseline">
              <p className="text-3xl font-bold text-gray-900">
                {formatCurrency(healthScore?.predicted_annual_cost || 0)}
              </p>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              Range: {formatCurrency(healthScore?.cost_prediction_range?.low || 0)} -{' '}
              {formatCurrency(healthScore?.cost_prediction_range?.high || 0)}
            </p>
          </div>

          {/* Total Rebates Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <DollarSign className="w-5 h-5 text-green-600 mr-2" />
                <h3 className="text-sm font-medium text-gray-600">Total Rebates</h3>
              </div>
            </div>
            <div className="flex items-baseline">
              <p className="text-3xl font-bold text-green-600">
                {formatCurrency(rebates?.total_rebates_lifetime || 0)}
              </p>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              {rebates?.rebates?.length || 0} rebates received
            </p>
          </div>

          {/* Active Programs Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Award className="w-5 h-5 text-vitanexus-primary mr-2" />
                <h3 className="text-sm font-medium text-gray-600">Active Programs</h3>
              </div>
            </div>
            <div className="flex items-baseline">
              <p className="text-4xl font-bold text-gray-900">
                {enrollments?.filter((e) => e.enrollment_status === 'active').length || 0}
              </p>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              {enrollments?.length || 0} total enrollments
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Risk Factors */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-5 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Top Risk Factors</h2>
            </div>
            <div className="p-6">
              {healthScore?.top_risk_factors && healthScore.top_risk_factors.length > 0 ? (
                <div className="space-y-4">
                  {healthScore.top_risk_factors.map((factor, index) => (
                    <div key={index} className="border-l-4 border-orange-400 bg-orange-50 p-4 rounded-r">
                      <div className="flex items-start">
                        <AlertCircle className="w-5 h-5 text-orange-600 mt-0.5 mr-3" />
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900">{factor.factor_name}</h4>
                          <p className="text-sm text-gray-600 mt-1">{factor.description}</p>
                          <div className="mt-3 bg-white rounded p-3 border border-orange-200">
                            <p className="text-sm font-medium text-gray-700">
                              Recommended Action:
                            </p>
                            <p className="text-sm text-gray-600 mt-1">
                              {factor.recommended_action}
                            </p>
                          </div>
                        </div>
                        <span className="ml-3 px-2 py-1 bg-orange-200 text-orange-800 text-xs font-bold rounded">
                          {factor.contribution_points.toFixed(0)} pts
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No risk factors identified</p>
              )}
            </div>
          </div>

          {/* Recommended Interventions */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-5 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Recommended Programs</h2>
            </div>
            <div className="p-6">
              {healthScore?.recommended_interventions && healthScore.recommended_interventions.length > 0 ? (
                <div className="space-y-3">
                  {healthScore.recommended_interventions.map((intervention, index) => (
                    <div
                      key={index}
                      className="flex items-start p-4 bg-blue-50 border border-blue-200 rounded-lg"
                    >
                      <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-sm text-gray-900">{intervention}</p>
                      </div>
                    </div>
                  ))}
                  <button className="w-full mt-4 px-4 py-3 bg-vitanexus-primary text-white rounded-lg font-medium hover:bg-vitanexus-700 transition">
                    Browse All Programs
                  </button>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">
                  Great job! No additional programs recommended.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Recent Rebates */}
        {rebates && rebates.rebates && rebates.rebates.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow">
            <div className="px-6 py-5 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Recent Rebates</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Period
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Base Rebate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Health Bonus
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Participation Bonus
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {rebates.rebates.slice(0, 5).map((rebate) => (
                    <tr key={rebate.rebate_id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {rebate.rebate_period}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(rebate.base_rebate_amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                        +{formatCurrency(rebate.health_improvement_bonus)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                        +{formatCurrency(rebate.participation_bonus)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                        {formatCurrency(rebate.total_rebate_amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full ${
                            rebate.distribution_status === 'completed'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {rebate.distribution_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};