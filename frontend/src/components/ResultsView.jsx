const ResultsView = ({ results }) => {
  return (
    <div className="results-view">
      <h2>Search Results</h2>
      {results.length === 0 ? (
        <p>No results found</p>
      ) : (
        <div className="results-list">
          {results.map((result, index) => (
            <div className="result-card" key={index}>
              <h3>{result.metadata.title}</h3>
              <p className="timestamp">
                Timestamp:{" "}
                <a
                  href={result.metadata.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {typeof result.metadata.start_time === "number"
                    ? new Date(result.metadata.start_time * 1000)
                        .toISOString()
                        .substr(11, 8)
                    : result.metadata.start_time}
                </a>
              </p>
              <p className="content">{result.content}</p>
              <p className="relevance">
                Relevance: {result.relevance.toFixed(2)}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ResultsView;
