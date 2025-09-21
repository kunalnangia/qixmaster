import React, { useState, useEffect } from "react";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, BarChart, Bar 
} from "recharts";
import * as XLSX from "xlsx";

const PerformanceTestUI = () => {
  // State management
  const [activeTab, setActiveTab] = useState("configure");
  const [testName, setTestName] = useState("");
  const [testType, setTestType] = useState("load");
  const [url, setUrl] = useState("https://example.com");
  const [concurrentUsers, setConcurrentUsers] = useState(10);
  const [duration, setDuration] = useState(60);
  const [rampUpTime, setRampUpTime] = useState(10);
  const [isRunning, setIsRunning] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [testHistory, setTestHistory] = useState([]);
  const [selectedTest, setSelectedTest] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [thresholds, setThresholds] = useState({
    responseTime: 1000,
    errorRate: 1,
    throughput: 10
  });

  // Fetch test history on component mount
  useEffect(() => {
    fetchTestHistory();
  }, []);

  const fetchTestHistory = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8002/performance-history");
      const data = await response.json();
      setTestHistory(data);
    } catch (error) {
      console.error("Error fetching test history:", error);
    }
  };

  const fetchTestDetails = async (runId) => {
    try {
      const response = await fetch(`http://127.0.0.1:8002/run-details/${runId}`);
      const data = await response.json();
      setSelectedTest(data);
      
      // Also fetch AI analysis if available
      fetchAIAnalysis(runId);
    } catch (error) {
      console.error("Error fetching test details:", error);
    }
  };
  
  const fetchAIAnalysis = async (runId) => {
    try {
      const response = await fetch(`http://127.0.0.1:8002/ai-analysis/${runId}`);
      const data = await response.json();
      setAiAnalysis(data);
    } catch (error) {
      console.error("Error fetching AI analysis:", error);
      setAiAnalysis(null);
    }
  };

  const runTest = async () => {
    if (!testName || !url) {
      alert("Please provide a test name and URL");
      return;
    }

    setIsRunning(true);
    try {
      const response = await fetch("http://127.0.0.1:8002/run-performance-test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          test_name: testName,
          test_type: testType,
          url: url,
          concurrent_users: concurrentUsers,
          duration: duration,
          ramp_up_time: rampUpTime,
          thresholds: {
            response_time: thresholds.responseTime,
            error_rate: thresholds.errorRate,
            throughput: thresholds.throughput
          }
        })
      });

      const result = await response.json();
      setTestResults(result);
      fetchTestHistory();
      setActiveTab("results");
    } catch (error) {
      console.error("Error running test:", error);
      alert("Failed to run test. Please check console for details.");
    } finally {
      setIsRunning(false);
    }
  };

  const exportToExcel = () => {
    if (!selectedTest) return;

    const data = selectedTest.time_series.timestamps.map((ts, i) => ({
      Timestamp: ts,
      "Response Time (ms)": selectedTest.time_series.response_times[i],
      "Error Rate (%)": selectedTest.time_series.error_rate_series[i],
      "Throughput (req/min)": selectedTest.time_series.throughput_series[i]
    }));

    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Performance Data");
    XLSX.writeFile(wb, `performance_test_${Date.now()}.xlsx`);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold flex items-center">
            <span className="mr-2">📊</span> AI Perf Tester
          </h1>
          <div className="flex space-x-4">
            <button 
              className={`px-4 py-2 rounded transition ${activeTab === "configure" ? "bg-blue-600" : "bg-gray-700"}`}
              onClick={() => setActiveTab("configure")}
            >
              Configure
            </button>
            <button 
              className={`px-4 py-2 rounded transition ${activeTab === "results" ? "bg-blue-600" : "bg-gray-700"}`}
              onClick={() => setActiveTab("results")}
            >
              Results
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto p-6">
        {/* Configuration Tab */}
        {activeTab === "configure" && (
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <h2 className="text-2xl font-semibold mb-6 flex items-center">
              <span className="mr-2">⚙️</span> Performance Test Configuration
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Left Column */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Test Name</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md"
                    value={testName}
                    onChange={(e) => setTestName(e.target.value)}
                    placeholder="Enter test name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Test Type</label>
                  <select
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md"
                    value={testType}
                    onChange={(e) => setTestType(e.target.value)}
                  >
                    <option value="load">Load Test</option>
                    <option value="stress">Stress Test</option>
                    <option value="spike">Spike Test</option>
                    <option value="endurance">Endurance Test</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">URL to Test</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://example.com"
                  />
                </div>
              </div>
              
              {/* Right Column */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Concurrent Users</label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md"
                    value={concurrentUsers}
                    onChange={(e) => setConcurrentUsers(Number(e.target.value))}
                    min="1"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Duration (seconds)</label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md"
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    min="1"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Ramp-up Time (seconds)</label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md"
                    value={rampUpTime}
                    onChange={(e) => setRampUpTime(Number(e.target.value))}
                    min="0"
                  />
                </div>
              </div>
            </div>
            
            {/* Thresholds */}
            <div className="mt-6">
              <h3 className="text-lg font-medium mb-3">Performance Thresholds</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Response Time (ms)</label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md"
                    value={thresholds.responseTime}
                    onChange={(e) => setThresholds({...thresholds, responseTime: Number(e.target.value)})}
                    min="0"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Error Rate (%)</label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md"
                    value={thresholds.errorRate}
                    onChange={(e) => setThresholds({...thresholds, errorRate: Number(e.target.value)})}
                    min="0"
                    max="100"
                    step="0.1"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Throughput (req/sec)</label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md"
                    value={thresholds.throughput}
                    onChange={(e) => setThresholds({...thresholds, throughput: Number(e.target.value)})}
                    min="0"
                  />
                </div>
              </div>
            </div>
            
            {/* Run Button */}
            <div className="mt-8 flex justify-end">
              <button
                className={`px-6 py-2 rounded-md font-medium text-white ${
                  isRunning ? "bg-gray-500 cursor-not-allowed" : "bg-green-600 hover:bg-green-700"
                }`}
                onClick={runTest}
                disabled={isRunning}
              >
                {isRunning ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Running Test...
                  </span>
                ) : (
                  "Run Test"
                )}
              </button>
            </div>
          </div>
        )}

        {/* Results Tab */}
        {activeTab === "results" && (
          <div className="space-y-6">
            {/* Test History */}
            <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
              <h2 className="text-2xl font-semibold mb-4">Test History</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-gray-700 rounded-lg overflow-hidden">
                  <thead className="bg-gray-600">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium">Test Name</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Avg Response</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Error Rate</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Date</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-600">
                    {testHistory.length > 0 ? (
                      testHistory.map((test) => (
                        <tr key={test.run_id} className="hover:bg-gray-650">
                          <td className="px-4 py-3 text-sm">{test.test_name}</td>
                          <td className="px-4 py-3 text-sm">{test.test_type}</td>
                          <td className="px-4 py-3 text-sm">
                            {test.avg_response_time ? `${test.avg_response_time.toFixed(2)} ms` : 'N/A'}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {test.error_rate ? `${test.error_rate.toFixed(2)}%` : '0%'}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {new Date(test.created_at).toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <button
                              className="px-3 py-1 bg-blue-600 rounded text-xs hover:bg-blue-700"
                              onClick={() => fetchTestDetails(test.run_id)}
                            >
                              View Details
                            </button>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="6" className="px-4 py-3 text-center text-sm">
                          No test history available
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Selected Test Details */}
            {selectedTest && (
              <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-semibold">{selectedTest.test_name} Details</h2>
                  <button
                    className="px-4 py-2 bg-green-600 rounded hover:bg-green-700 text-sm"
                    onClick={exportToExcel}
                  >
                    Export to Excel
                  </button>
                </div>

                {/* Test Info */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-400">URL</h3>
                    <p className="text-lg font-semibold truncate">{selectedTest.url}</p>
                  </div>
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-400">Users</h3>
                    <p className="text-lg font-semibold">{selectedTest.concurrent_users}</p>
                  </div>
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-400">Duration</h3>
                    <p className="text-lg font-semibold">{selectedTest.duration}s</p>
                  </div>
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-400">Ramp-up</h3>
                    <p className="text-lg font-semibold">{selectedTest.ramp_up_time}s</p>
                  </div>
                </div>

                {/* Summary Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-400">Avg Response Time</h3>
                    <p className="text-2xl font-semibold text-blue-400">
                      {selectedTest.summary_metrics?.avg_response_time?.toFixed(2) || 0} ms
                    </p>
                  </div>
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-400">Error Rate</h3>
                    <p className={`text-2xl font-semibold ${
                      (selectedTest.summary_metrics?.error_rate || 0) > 1 
                        ? "text-red-400" 
                        : "text-green-400"
                    }`}>
                      {selectedTest.summary_metrics?.error_rate?.toFixed(2) || 0}%
                    </p>
                  </div>
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-400">Max Throughput</h3>
                    <p className="text-2xl font-semibold text-purple-400">
                      {selectedTest.summary_metrics?.throughput || 0} req/min
                    </p>
                  </div>
                </div>

                {/* Response Time Chart */}
                <div className="mb-6">
                  <h3 className="text-lg font-medium mb-3">Response Time</h3>
                  <div className="h-64 bg-gray-700 rounded-lg p-4">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={selectedTest.time_series.timestamps.map((ts, i) => ({
                        time: new Date(ts).toLocaleTimeString(),
                        value: selectedTest.time_series.response_times[i]
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                        <XAxis dataKey="time" />
                        <YAxis />
                        <Tooltip contentStyle={{ backgroundColor: "#333", border: "none" }} />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="value" 
                          name="Response Time (ms)" 
                          stroke="#3b82f6" 
                          strokeWidth={2} 
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Error Rate Chart */}
                <div className="mb-6">
                  <h3 className="text-lg font-medium mb-3">Error Rate</h3>
                  <div className="h-64 bg-gray-700 rounded-lg p-4">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={selectedTest.time_series.timestamps.map((ts, i) => ({
                        time: new Date(ts).toLocaleTimeString(),
                        value: selectedTest.time_series.error_rate_series[i]
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                        <XAxis dataKey="time" />
                        <YAxis />
                        <Tooltip contentStyle={{ backgroundColor: "#333", border: "none" }} />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="value" 
                          name="Error Rate (%)" 
                          stroke="#ef4444" 
                          strokeWidth={2} 
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* AI Analysis */}
                {aiAnalysis && (
                  <div className="bg-gray-700 rounded-lg p-6 mt-6">
                    <h3 className="text-xl font-semibold mb-4">AI Analysis</h3>
                    
                    {aiAnalysis.bottlenecks.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-md font-medium text-red-400 mb-2">Identified Bottlenecks</h4>
                        <ul className="list-disc pl-5 space-y-1">
                          {aiAnalysis.bottlenecks.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {aiAnalysis.recommendations.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-md font-medium text-green-400 mb-2">Recommendations</h4>
                        <ul className="list-disc pl-5 space-y-1">
                          {aiAnalysis.recommendations.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {aiAnalysis.next_tests.length > 0 && (
                      <div>
                        <h4 className="text-md font-medium text-blue-400 mb-2">Suggested Next Tests</h4>
                        <ul className="list-disc pl-5 space-y-1">
                          {aiAnalysis.next_tests.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* JMeter Report Link */}
                <div className="mt-6">
                  <a 
                    href={selectedTest.report_url} 
                    target="_blank" 
                    rel="noreferrer"
                    className="inline-block px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded text-white"
                  >
                    View Full JMeter Report
                  </a>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PerformanceTestUI;