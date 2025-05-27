import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './ResultCard.css';

function ResultCard() {
  const [result, setResult] = useState(null);
  const [alertShown, setAlertShown] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      axios.get('http://localhost:5001/latest')
        .then(res => {
          const data = res.data;
          if (data.label) {
            setResult(data);
            if (data.label === "WannaCry" && !alertShown) {
              // RED POPUP DANGER
              const warning = document.createElement("div");
              warning.innerText = "🚨 WannaCry Attack Detected!";
              warning.className = "alert-popup";
              document.body.appendChild(warning);
              setTimeout(() => warning.remove(), 4000);
              setAlertShown(true);
            }
          }
        })
        .catch(err => {
          console.error("Error fetching result:", err);
        });
    }, 3000);
    return () => clearInterval(interval);
  }, [alertShown]);

  return (
    <div className={`card-container ${result?.label === "WannaCry" ? "danger" : ""}`}>
      <h2>Latest Detection</h2>
      {result ? (
        <div className="result-details">
          <p><strong>Status:</strong> {result.label}</p>
          <p><strong>Packets Detected:</strong> {result.count} out of {result.total}</p>
          <p><strong>File:</strong> {result.file}</p>
          <p><strong>Time:</strong> {new Date(result.timestamp).toLocaleString()}</p>
        </div>
      ) : (
        <p>Waiting for result...</p>
      )}
    </div>
  );
}

export default ResultCard;

