import { useEffect, useState } from "react";
import { Bar, Doughnut, Line } from "react-chartjs-2";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
);


function DashboardChart({ chart }) {
  if (!chart || !chart.labels || !chart.datasets) {
    return null;
  }

  const datasets = chart.datasets.map(
    (dataset, index) => ({
      ...dataset,

      ...(chart.chart_type === "line"
        ? {
            yAxisID:
              index === 0
                ? "yOrders"
                : "yRevenue",
            tension: 0.25,
            pointRadius: 3,
          }
        : {}),
    })
  );

  const data = {
    labels: chart.labels,
    datasets,
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,

    plugins: {
      legend: {
        position: "top",
      },

      tooltip: {
        mode: "index",
        intersect: false,
      },
    },
  };


  if (chart.chart_type === "line") {
    return (
      <Line
        data={data}
        options={{
          ...options,

          interaction: {
            mode: "index",
            intersect: false,
          },

          scales: {
            x: {
              title: {
                display: true,
                text: "Month",
              },
            },

            yOrders: {
              type: "linear",
              position: "left",
              beginAtZero: true,

              title: {
                display: true,
                text: "Orders",
              },
            },

            yRevenue: {
              type: "linear",
              position: "right",
              beginAtZero: true,

              title: {
                display: true,
                text: "Revenue",
              },

              grid: {
                drawOnChartArea: false,
              },
            },
          },
        }}
      />
    );
  }


  if (chart.chart_type === "donut") {
    return (
      <Doughnut
        data={data}
        options={options}
      />
    );
  }


  return (
    <Bar
      data={data}
      options={{
        ...options,

        indexAxis:
          chart.chart_type === "horizontal_bar" ||
          chart.chart_type === "stacked_horizontal_bar"
            ? "y"
            : "x",
      }}
    />
  );
}


export default function Dashboard() {
  const [charts, setCharts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState({});
  const [messages, setMessages] = useState({});
  const [error, setError] = useState("");


  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        "http://127.0.0.1:8000/api/dashboard"
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.error?.message ||
          "Failed to load dashboard."
        );
      }

      setCharts(data.charts || []);

    } catch (err) {
      setError(
        err.message ||
        "Failed to load dashboard."
      );

    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    loadDashboard();
  }, []);


  const handleRefreshChart = async (chartId) => {
    setRefreshing((previous) => ({
      ...previous,
      [chartId]: true,
    }));

    setMessages((previous) => ({
      ...previous,
      [chartId]: "",
    }));

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/dashboard/${chartId}/refresh`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.error?.message ||
          "Failed to refresh chart."
        );
      }

      if (data?.error) {
        throw new Error(
          data.error.message ||
          "Failed to refresh chart."
        );
      }

      setCharts((previousCharts) =>
        previousCharts.map((chart) => {
          if (chart.id !== chartId) {
            return chart;
          }

          return {
            ...chart,
            chart_config: data.chart,
            insight: data.insight,
            data_snapshot: data.result,
            updated_at: new Date().toISOString(),
          };
        })
      );

      setMessages((previous) => ({
        ...previous,
        [chartId]: data.significant_change
          ? "⚠ Significant change detected."
          : "✓ Refreshed — no significant change.",
      }));

    } catch (err) {
      setMessages((previous) => ({
        ...previous,
        [chartId]:
          err.message ||
          "Failed to refresh chart.",
      }));

    } finally {
      setRefreshing((previous) => ({
        ...previous,
        [chartId]: false,
      }));
    }
  };


  return (
    <section className="dashboard-section">

      <div className="dashboard-header">

        <div>
          <span className="result-label">
            SAVED ANALYTICS
          </span>

          <h2>
            📊 Dashboard
          </h2>
        </div>


        <button
          className="refresh-dashboard-button"
          onClick={loadDashboard}
          disabled={loading}
        >
          {loading
            ? "Loading..."
            : "Refresh Dashboard"}
        </button>

      </div>


      {error && (
        <div className="error">

          <strong>
            Dashboard error
          </strong>

          <span>
            {error}
          </span>

        </div>
      )}


      {!loading &&
        charts.length === 0 &&
        !error && (
          <div className="empty-dashboard">
            No charts have been pinned yet.
          </div>
        )}


      <div className="dashboard-grid">

        {charts.map((item) => (

          <article
            className="dashboard-card"
            key={item.id}
          >

            <div className="dashboard-card-header">

              <div>
                <h3>
                  {item.chart_config?.title ||
                    "Analytics Chart"}
                </h3>

                <p className="dashboard-query">
                  {item.query}
                </p>
              </div>

              <span className="tag">
                {item.chart_type}
              </span>

            </div>


            {item.insight && (
              <div className="dashboard-insight">

                <strong>
                  Key insight
                </strong>

                <p>
                  {item.insight}
                </p>

              </div>
            )}


            <div className="dashboard-card-actions">

              <button
                className="card-refresh-button"
                onClick={() =>
                  handleRefreshChart(item.id)
                }
                disabled={
                  refreshing[item.id]
                }
              >
                {refreshing[item.id]
                  ? "Refreshing..."
                  : "↻ Refresh Chart"}
              </button>


              {messages[item.id] && (
                <span
                  className={
                    messages[item.id].includes(
                      "Significant"
                    )
                      ? "refresh-warning"
                      : "refresh-success"
                  }
                >
                  {messages[item.id]}
                </span>
              )}

            </div>


            <div className="dashboard-chart-container">

              <DashboardChart
                chart={item.chart_config}
              />

            </div>


            <div className="dashboard-card-footer">
              Last saved{" "}
              {new Date(
                item.updated_at ||
                item.created_at
              ).toLocaleString()}
            </div>

          </article>

        ))}

      </div>

    </section>
  );
}