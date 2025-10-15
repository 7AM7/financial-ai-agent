"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { useCopilotReadable, useCopilotAction } from "@copilotkit/react-core";
import { AreaChart } from "./ui/area-chart";
import { BarChart } from "./ui/bar-chart";
import { DonutChart } from "./ui/pie-chart";
import { api, type ProfitLoss, type TopAccount, type TrendAnalysis, type CategoryPerformance } from "../lib/api";

type WidgetId = "revenue" | "profit" | "expenses" | "margin";

export function FinancialDashboard() {
  // State for dashboard data
  const [profitLoss, setProfitLoss] = useState<ProfitLoss[]>([]);
  const [topExpenses, setTopExpenses] = useState<TopAccount[]>([]);
  const [topRevenue, setTopRevenue] = useState<TopAccount[]>([]);
  const [trends, setTrends] = useState<TrendAnalysis[]>([]);
  const [categoryPerformance, setCategoryPerformance] = useState<CategoryPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State for widget order
  const [widgetOrder, setWidgetOrder] = useState<WidgetId[]>(["revenue", "profit", "expenses", "margin"]);

  // Fetch data on mount
  useEffect(() => {
    async function fetchDashboardData() {
      try {
        setLoading(true);
        setError(null);

        // First, fetch P&L to get the latest year
        const plData = await api.getProfitLoss();
        const latestYear = plData[0]?.year || new Date().getFullYear();

        // Fetch remaining dashboard data with latest year filter for top accounts
        const [topExp, topRev, trendData, catPerf] = await Promise.all([
          api.getTopAccounts({ account_type: 'expense', period: 'yearly', year: latestYear, limit: 5 }),
          api.getTopAccounts({ account_type: 'revenue', period: 'yearly', year: latestYear, limit: 5 }),
          api.getTrendAnalysis({ year: latestYear }),
          api.getCategoryPerformance({ account_type: 'expense' }),
        ]);

        setProfitLoss(plData);
        setTopExpenses(topExp);
        setTopRevenue(topRev);
        setTrends(trendData);
        setCategoryPerformance(catPerf);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  // Calculate key metrics from profit & loss data
  const latestPL = profitLoss[0];
  const totalRevenue = profitLoss.reduce((sum, pl) => sum + pl.revenue, 0);
  const totalProfit = profitLoss.reduce((sum, pl) => sum + pl.net_profit, 0);
  const avgProfitMargin = latestPL?.profit_margin_percent ?? 0;
  const totalExpenses = profitLoss.reduce((sum, pl) => sum + pl.expenses, 0);

  // Make data available to the Copilot
  useCopilotReadable({
    description: "Financial dashboard data including P&L, top accounts, trends, and category performance",
    value: {
      profitLoss,
      topExpenses,
      topRevenue,
      trends,
      categoryPerformance,
      metrics: {
        totalRevenue,
        totalProfit,
        avgProfitMargin,
        totalExpenses,
      }
    }
  });

  // Widget swapping action
  useCopilotAction({
    name: "swapDashboardWidgets",
    description: "Swap the positions of two metric boxes on the dashboard. Use this when user wants to rearrange or swap widget positions.",
    parameters: [
      {
        name: "widget1",
        type: "string",
        description: "First widget to swap (revenue, profit, expenses, or margin)",
        enum: ["revenue", "profit", "expenses", "margin"],
        required: true,
      },
      {
        name: "widget2",
        type: "string",
        description: "Second widget to swap with",
        enum: ["revenue", "profit", "expenses", "margin"],
        required: true,
      }
    ],
    handler: async ({ widget1, widget2 }) => {
      // Find indices of both widgets
      const index1 = widgetOrder.indexOf(widget1 as WidgetId);
      const index2 = widgetOrder.indexOf(widget2 as WidgetId);

      if (index1 === -1 || index2 === -1) {
        return "Error: Invalid widget selection";
      }

      if (widget1 === widget2) {
        return "Cannot swap a widget with itself";
      }

      // Swap positions
      const newOrder = [...widgetOrder];
      [newOrder[index1], newOrder[index2]] = [newOrder[index2], newOrder[index1]];
      setWidgetOrder(newOrder);

      const widgetNames: Record<WidgetId, string> = {
        revenue: "Total Revenue",
        profit: "Total Profit",
        expenses: "Total Expenses",
        margin: "Profit Margin"
      };

      return `Successfully swapped ${widgetNames[widget1 as WidgetId]} with ${widgetNames[widget2 as WidgetId]}`;
    },
    render: ({ args, status }) => {
      const widgetNames: Record<string, string> = {
        revenue: "Total Revenue",
        profit: "Total Profit",
        expenses: "Total Expenses",
        margin: "Profit Margin"
      };

      return (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center gap-2 text-sm text-blue-900">
            <span className="text-lg">🔄</span>
            <span className="font-medium">
              Swapping {widgetNames[args.widget1 || ""]} ↔ {widgetNames[args.widget2 || ""]}
            </span>
          </div>
          {status === "complete" && (
            <p className="text-xs text-green-600 mt-1">✓ Widgets swapped successfully</p>
          )}
        </div>
      );
    }
  });

  // Color palettes
  const colors = {
    profitLoss: ["#3b82f6", "#ef4444", "#10b981"],  // Blue (revenue), Red (expenses), Green (profit)
    topAccounts: ["#8b5cf6", "#6366f1", "#4f46e5", "#4338ca", "#3730a3"],  // Purple spectrum
    categories: ["#3b82f6", "#64748b", "#10b981", "#f59e0b", "#94a3b8", "#ef4444", "#8b5cf6"],
    trends: ["#059669", "#10b981", "#34d399"],  // Green spectrum
  };

  // Loading state
  if (loading) {
    return (
      <div className="grid gap-4 grid-cols-1 w-full">
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-500 border-r-transparent"></div>
            <p className="mt-4 text-gray-600">Loading financial data...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="grid gap-4 grid-cols-1 w-full">
        <Card>
          <CardContent className="p-6">
            <div className="text-center text-red-600">
              <p className="font-semibold">Error loading dashboard</p>
              <p className="text-sm mt-2">{error}</p>
              <p className="text-xs mt-4 text-gray-500">
                Make sure the backend is running at http://localhost:8000
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Transform data for charts
  const profitLossChartData = profitLoss.map(pl => ({
    period: pl.year_quarter,
    Revenue: pl.revenue,
    Expenses: pl.expenses,
    "Net Profit": pl.net_profit,
  }));

  const topExpensesChartData = topExpenses.map(acc => ({
    name: acc.account_name.length > 20 ? acc.account_name.substring(0, 20) + '...' : acc.account_name,
    amount: acc.total_amount,
  }));

  const topRevenueChartData = topRevenue.map(acc => ({
    name: acc.account_name.length > 20 ? acc.account_name.substring(0, 20) + '...' : acc.account_name,
    amount: acc.total_amount,
  }));

  // Get unique categories and aggregate totals
  const categoryTotals = categoryPerformance.reduce((acc, cat) => {
    if (!acc[cat.account_category]) {
      acc[cat.account_category] = 0;
    }
    acc[cat.account_category] += cat.total_amount;
    return acc;
  }, {} as Record<string, number>);

  const categoryChartData = Object.entries(categoryTotals)
    .map(([name, value]) => ({
      name: name.length > 25 ? name.substring(0, 25) + '...' : name,
      value: Math.round((value / Object.values(categoryTotals).reduce((a, b) => a + b, 0)) * 100),
    }))
    .slice(0, 6); // Top 6 categories

  // Trend data for area chart (last 12 months)
  const revenueTrends = trends
    .filter(t => t.account_type === 'revenue')
    .slice(0, 12)
    .reverse()
    .map(t => ({
      month: t.year_month,
      Revenue: t.month_total,
    }));

  // Define widget data mapping
  const widgetData: Record<WidgetId, { label: string; value: string }> = {
    revenue: {
      label: "Total Revenue",
      value: `$${totalRevenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
    },
    profit: {
      label: "Total Profit",
      value: `$${totalProfit.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
    },
    expenses: {
      label: "Total Expenses",
      value: `$${totalExpenses.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
    },
    margin: {
      label: "Profit Margin",
      value: `${avgProfitMargin?.toFixed(1)}%`
    }
  };

  return (
    <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-4 w-full">
      {/* Key Metrics - Dynamic Order */}
      <div className="col-span-1 md:col-span-2 lg:col-span-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {widgetOrder.map((widgetId) => (
            <div
              key={widgetId}
              className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm transition-all duration-300 ease-in-out hover:shadow-md"
            >
              <p className="text-xs text-gray-500">{widgetData[widgetId].label}</p>
              <p className="text-xl font-semibold text-gray-900">
                {widgetData[widgetId].value}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Profit & Loss Chart */}
      <Card className="col-span-1 md:col-span-2 lg:col-span-4">
        <CardHeader className="pb-1 pt-3">
          <CardTitle className="text-base font-medium">Profit & Loss by Quarter</CardTitle>
          <CardDescription className="text-xs">Revenue, expenses, and net profit trends</CardDescription>
        </CardHeader>
        <CardContent className="p-3">
          <div className="h-60">
            {profitLossChartData.length > 0 ? (
              <AreaChart
                data={profitLossChartData}
                index="period"
                categories={["Revenue", "Expenses", "Net Profit"]}
                colors={colors.profitLoss}
                valueFormatter={(value) => `$${value.toLocaleString()}`}
                showLegend={true}
                showGrid={true}
                showXAxis={true}
                showYAxis={true}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                No P&L data available
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Top Revenue Accounts */}
      <Card className="col-span-1 md:col-span-1 lg:col-span-2">
        <CardHeader className="pb-1 pt-3">
          <CardTitle className="text-base font-medium">Top Revenue Accounts</CardTitle>
          <CardDescription className="text-xs">
            Highest revenue sources {topRevenue[0]?.year ? `(${topRevenue[0].year})` : ''}
          </CardDescription>
        </CardHeader>
        <CardContent className="p-3">
          <div className="h-60">
            {topRevenueChartData.length > 0 ? (
              <BarChart
                data={topRevenueChartData}
                index="name"
                categories={["amount"]}
                colors={colors.topAccounts}
                valueFormatter={(value) => `$${value.toLocaleString()}`}
                showLegend={false}
                showGrid={true}
                layout="vertical"
                yAxisWidth={180}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                No revenue data available
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Top Expense Accounts */}
      <Card className="col-span-1 md:col-span-1 lg:col-span-2">
        <CardHeader className="pb-1 pt-3">
          <CardTitle className="text-base font-medium">Top Expense Accounts</CardTitle>
          <CardDescription className="text-xs">
            Highest expense categories {topExpenses[0]?.year ? `(${topExpenses[0].year})` : ''}
          </CardDescription>
        </CardHeader>
        <CardContent className="p-3">
          <div className="h-60">
            {topExpensesChartData.length > 0 ? (
              <BarChart
                data={topExpensesChartData}
                index="name"
                categories={["amount"]}
                colors={colors.topAccounts}
                valueFormatter={(value) => `$${value.toLocaleString()}`}
                showLegend={false}
                showGrid={true}
                layout="vertical"
                yAxisWidth={180}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                No expense data available
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Expense Categories */}
      <Card className="col-span-1 md:col-span-1 lg:col-span-2">
        <CardHeader className="pb-1 pt-3">
          <CardTitle className="text-base font-medium">Expense Categories</CardTitle>
          <CardDescription className="text-xs">Distribution by category</CardDescription>
        </CardHeader>
        <CardContent className="p-3">
          <div className="h-60">
            {categoryChartData.length > 0 ? (
              <DonutChart
                data={categoryChartData}
                category="value"
                index="name"
                valueFormatter={(value) => `${value}%`}
                colors={colors.categories}
                centerText="Categories"
                paddingAngle={0}
                showLabel={false}
                showLegend={true}
                innerRadius={45}
                outerRadius="90%"
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                No category data available
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Revenue Trends */}
      <Card className="col-span-1 md:col-span-1 lg:col-span-2">
        <CardHeader className="pb-1 pt-3">
          <CardTitle className="text-base font-medium">Revenue Trend</CardTitle>
          <CardDescription className="text-xs">Monthly revenue over time</CardDescription>
        </CardHeader>
        <CardContent className="p-3">
          <div className="h-60">
            {revenueTrends.length > 0 ? (
              <AreaChart
                data={revenueTrends}
                index="month"
                categories={["Revenue"]}
                colors={colors.trends}
                valueFormatter={(value) => `$${value.toLocaleString()}`}
                showLegend={false}
                showGrid={true}
                showXAxis={true}
                showYAxis={true}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                No trend data available
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
