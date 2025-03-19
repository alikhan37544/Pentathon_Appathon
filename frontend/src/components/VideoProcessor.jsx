import { useState } from "react";

const VideoProcessor = ({ setIsLoading, setError }) => {
  const [videoId, setVideoId] = useState("");
  const [processedInfo, setProcessedInfo] = useState(null);
  const [debug, setDebug] = useState("");

  const processVideo = async () => {
    if (!videoId.trim()) {
      setError("Please enter a YouTube video ID");
      return;
    }

    setIsLoading(true);
    setError("");
    setDebug("");

    try {
      const response = await fetch("/api/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ videoId }),
      });

      // Debug response status and headers
      setDebug(
        `Response status: ${response.status}, type: ${response.headers.get(
          "content-type"
        )}`
      );

      // Check if response is ok before trying to parse JSON
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Server error: ${response.status} - ${text}`);
      }

      // Safely parse JSON
      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        const text = await response.text();
        throw new Error(
          `Failed to parse JSON: ${
            parseError.message
          }. Raw response: ${text.substring(0, 200)}...`
        );
      }

      setProcessedInfo(data);
    } catch (error) {
      setError(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="video-processor">
      <h2>Process YouTube Video</h2>
      <div className="input-group">
        <input
          type="text"
          placeholder="YouTube Video ID (e.g., dQw4w9WgXcQ)"
          value={videoId}
          onChange={(e) => setVideoId(e.target.value)}
        />
        <button onClick={processVideo}>Process Video</button>
      </div>

      {debug && <div className="debug-info">{debug}</div>}

      {processedInfo && (
        <div className="processed-info">
          {/* Rest of your component remains the same */}
          <h3>Video Processed Successfully</h3>
          <div className="video-details">
            <img
              src={processedInfo.video_info.thumbnail}
              alt={processedInfo.video_info.title}
            />
            <div>
              <h4>{processedInfo.video_info.title}</h4>
              <p>Channel: {processedInfo.video_info.channel}</p>
              <a
                href={processedInfo.video_info.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                Watch on YouTube
              </a>
            </div>
          </div>

          <h4>Video Segments</h4>
          <div className="segments">
            {processedInfo.segments.map((segment, index) => (
              <div className="segment" key={index}>
                <div className="segment-title">{segment.title}</div>
                <div className="segment-time">
                  {segment.start_time} - {segment.end_time}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoProcessor;
