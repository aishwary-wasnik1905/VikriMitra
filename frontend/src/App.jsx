import { useState } from "react";
import { Bar, Doughnut, Line, Scatter } from "react-chartjs-2";

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

import Dashboard from "./Dashboard";
import "./App.css";

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


// ============================================================
// Analytics Chart
// ============================================================

function AnalyticsChart({ chart }) {
  if (!chart) {
    return null;
  }

  // ----------------------------------------------------------
  // Scatter chart
  // ----------------------------------------------------------

  if (chart.chart_type === "scatter") {
    const scatterDatasets = (chart.datasets || []).map(
      (dataset) => ({
        ...dataset,
        showLine: false,
        pointRadius: 6,
        pointHoverRadius: 8,
      })
    );

    const scatterData = {
      datasets: scatterDatasets,
    };

    return (
      <Scatter
        data={scatterData}
        options={{
          responsive: true,
          maintainAspectRatio: false,

          plugins: {
            legend: {
              position: "top",
            },

            tooltip: {
              mode: "nearest",
              intersect: true,
            },
          },

          scales: {
            x: {
              type: "linear",
              title: {
                display: true,
                text: chart.x_axis_label || "Items Sold",
              },
            },

            y: {
              type: "linear",
              beginAtZero: true,
              title: {
                display: true,
                text: chart.y_axis_label || "Revenue",
              },
            },
          },
        }}
      />
    );
  }


  // ----------------------------------------------------------
  // Validate normal chart data
  // ----------------------------------------------------------

  if (!chart.labels || !chart.datasets) {
    return null;
  }


  // ----------------------------------------------------------
  // Normal Chart.js data
  // ----------------------------------------------------------

  const chartData = {
    labels: chart.labels,

    datasets: chart.datasets.map(
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
    ),
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


  // ----------------------------------------------------------
  // Line chart
  // ----------------------------------------------------------

  if (chart.chart_type === "line") {
    return (
      <Line
        data={chartData}

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

              title: {
                display: true,
                text: "Orders",
              },

              beginAtZero: true,
            },

            yRevenue: {
              type: "linear",
              position: "right",

              title: {
                display: true,
                text: "Revenue",
              },

              beginAtZero: true,

              grid: {
                drawOnChartArea: false,
              },
            },
          },
        }}
      />
    );
  }


  // ----------------------------------------------------------
  // Doughnut chart
  // ----------------------------------------------------------

  if (chart.chart_type === "donut") {
    return (
      <Doughnut
        data={chartData}
        options={options}
      />
    );
  }


  // ----------------------------------------------------------
  // Bar charts
  // ----------------------------------------------------------

  return (
    <Bar
      data={chartData}

      options={{
        ...options,

        indexAxis:
          chart.chart_type === "horizontal_bar" ||
          chart.chart_type === "stacked_horizontal_bar"
            ? "y"
            : "x",

        scales: {
          x: {
            beginAtZero: true,
          },

          y: {
            beginAtZero: true,
          },
        },
      }}
    />
  );
}


// ============================================================
// Main App
// ============================================================

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [pinning, setPinning] = useState(false);

  const [response, setResponse] = useState(null);
  const [error, setError] = useState("");
  const [pinMessage, setPinMessage] = useState("");


  // ==========================================================
  // Submit query
  // ==========================================================

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!query.trim()) {
      return;
    }

    setLoading(true);
    setError("");
    setResponse(null);
    setPinMessage("");

    try {
      const result = await fetch(
        "http://127.0.0.1:8000/api/query",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            query: query.trim(),
          }),
        }
      );

      const data = await result.json();

      if (!result.ok) {
        throw new Error(
          data?.error?.message ||
            "Request failed."
        );
      }

      if (data?.error) {
        throw new Error(
          data.error.message ||
            "Analytics request failed."
        );
      }

      setResponse(data);

    } catch (err) {
      setError(
        err.message ||
          "Something went wrong."
      );

    } finally {
      setLoading(false);
    }
  };


  // ==========================================================
  // Pin chart
  // ==========================================================

  const handlePin = async () => {
    if (!response) {
      return;
    }

    setPinning(true);
    setPinMessage("");
    setError("");

    try {
      const result = await fetch(
        "http://127.0.0.1:8000/api/dashboard/pin",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            query: query.trim(),

            chart_type:
              response.chart?.chart_type ||
              "bar",

            chart_config:
              response.chart || {},

            insight:
              response.insight || "",

            data_snapshot:
              response.result || {},
          }),
        }
      );

      const data = await result.json();

      if (!result.ok) {
        throw new Error(
          data?.error?.message ||
            "Could not pin the chart."
        );
      }

      setPinMessage(
        "Chart pinned to dashboard successfully."
      );

    } catch (err) {
      setError(
        err.message ||
          "Could not pin the chart."
      );

    } finally {
      setPinning(false);
    }
  };


  // ==========================================================
  // UI
  // ==========================================================

  return (
    <div className="app">

      <header className="header">

        <div className="header-content">

          <div>
            <div className="brand">
              VikriMitra
            </div>

            <div className="tagline">
              E-Commerce Sales Intelligence
            </div>
          </div>

          <div className="status-badge">
            <span className="status-dot"></span>
            Analytics Online
          </div>

        </div>

      </header>


      <main className="container">

        <section className="hero-section">

          <div className="hero-text">

            <span className="eyebrow">
              AI-POWERED ANALYTICS
            </span>

            <h1>
              Ask questions.
              <br />
              Get insights.
            </h1>

            <p>
              Explore your e-commerce data using
              natural language. VikriMitra turns
              your questions into analytics,
              charts, and actionable insights.
            </p>

          </div>


          <div className="query-section">

            <div className="query-header">

              <h2>
                Ask VikriMitra
              </h2>

              <p>
                Ask a question about your sales data
              </p>

            </div>


            <form
              onSubmit={handleSubmit}
              className="query-form"
            >

              <input
                type="text"
                value={query}
                onChange={(event) =>
                  setQuery(event.target.value)
                }
                placeholder="e.g. Show monthly revenue and order count for 2017"
                disabled={loading}
              />

              <button
                type="submit"
                disabled={
                  loading ||
                  !query.trim()
                }
              >
                {loading
                  ? "Analyzing..."
                  : "Analyze"}
              </button>

            </form>


            <div className="example-section">

              <span>
                Try an example:
              </span>

              <div className="example-buttons">

                <button
                  type="button"
                  className="example-button"
                  onClick={() =>
                    setQuery(
                      "Show monthly revenue and order count for 2017"
                    )
                  }
                >
                  Monthly revenue 2017
                </button>


                <button
                  type="button"
                  className="example-button"
                  onClick={() =>
                    setQuery(
                      "Show the top 10 categories by revenue"
                    )
                  }
                >
                  Top categories
                </button>


                <button
                  type="button"
                  className="example-button"
                  onClick={() =>
                    setQuery(
                      "Show payment breakdown"
                    )
                  }
                >
                  Payment breakdown
                </button>


                <button
                  type="button"
                  className="example-button"
                  onClick={() =>
                    setQuery(
                      "Show delivery performance by state"
                    )
                  }
                >
                  Delivery performance
                </button>

              </div>

            </div>

          </div>

        </section>


        {error && (
          <div className="error">

            <strong>
              Something went wrong
            </strong>

            <span>
              {error}
            </span>

          </div>
        )}


        {response && (
          <section className="result-section">

            <div className="result-card">

              <div className="result-header">

                <div>

                  <span className="result-label">
                    ANALYSIS RESULT
                  </span>

                  <h2>
                    {response.chart?.title ||
                      "Analytics Result"}
                  </h2>

                </div>

                <div className="result-tags">

                  <span className="tag">
                    {response.tool}
                  </span>

                  <span className="tag">
                    {response.chart?.chart_type}
                  </span>

                </div>

              </div>


              {response.insight && (
                <div className="insight">

                  <span className="insight-icon">
                    ✦
                  </span>

                  <div>

                    <strong>
                      Key insight
                    </strong>

                    <p>
                      {response.insight}
                    </p>

                  </div>

                </div>
              )}


              <div className="dashboard-actions">

                <button
                  className="pin-button"
                  onClick={handlePin}
                  disabled={pinning}
                >
                  {pinning
                    ? "Pinning..."
                    : "📌 Pin to Dashboard"}
                </button>

                {pinMessage && (
                  <span className="pin-message">
                    ✓ {pinMessage}
                  </span>
                )}

              </div>


              <div className="chart-container">

                <AnalyticsChart
                  chart={response.chart}
                />

              </div>

            </div>

          </section>
        )}


        <Dashboard />

      </main>


      <footer className="footer">

        <p>
          VikriMitra • E-Commerce Sales Analytics
        </p>

        <span>
          Powered by AI + MCP + PostgreSQL
        </span>

      </footer>

    </div>
  );
}


export default App;