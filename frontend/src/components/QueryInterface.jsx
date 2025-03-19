import { useState } from "react";

const QueryInterface = ({ setResults, setIsLoading, setError }) => {
  const [queryText, setQueryText] = useState("");

  const handleQuery = async () => {
    if (!queryText.trim()) {
      setError("Please enter a query");
      return;
    }

    setIsLoading(true);
    setError("");
    setResults([]);

    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: queryText }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to process query");
      }

      setResults(data.results);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="query-interface">
      <h2>Search Video Transcripts</h2>
      <div className="input-group">
        <input
          type="text"
          placeholder="Enter your search query"
          value={queryText}
          onChange={(e) => setQueryText(e.target.value)}
        />
        <button onClick={handleQuery}>Search</button>
      </div>
    </div>
  );
};

export default QueryInterface;
