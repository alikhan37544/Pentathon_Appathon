import { useState } from "react";
import "./App.css";
import VideoProcessor from "./components/VideoProcessor";
import QueryInterface from "./components/QueryInterface";
import ResultsView from "./components/ResultsView";

function App() {
  const [activeTab, setActiveTab] = useState("process");
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  return (
    <div className="App">
      <header className="App-header">
        <h1>YouTube Transcript Explorer</h1>
        <div className="tabs">
          <button
            className={activeTab === "process" ? "active" : ""}
            onClick={() => setActiveTab("process")}
          >
            Process Video
          </button>
          <button
            className={activeTab === "query" ? "active" : ""}
            onClick={() => setActiveTab("query")}
          >
            Query Transcripts
          </button>
        </div>
      </header>
      <main>
        {error && <div className="error-message">{error}</div>}

        {activeTab === "process" ? (
          <VideoProcessor setIsLoading={setIsLoading} setError={setError} />
        ) : (
          <QueryInterface
            setResults={setResults}
            setIsLoading={setIsLoading}
            setError={setError}
          />
        )}

        {results.length > 0 && activeTab === "query" && (
          <ResultsView results={results} />
        )}

        {isLoading && <div className="loading">Processing...</div>}
      </main>
    </div>
  );
}

export default App;
