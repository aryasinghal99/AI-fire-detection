"use client";
import { useEffect, useState, useRef } from "react";

type Alert = {
  id: number;
  timestamp: string;
  type: string;
  confidence: number;
  snapshot: string;
};

export default function Home() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const fetchAlerts = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/alerts");
      const data = await res.json();

      // 🔔 Play sound if new FIRE detected
      if (data.alerts.length > 0) {
        const latest = data.alerts[0];
        if (latest.type === "FIRE") {
          audioRef.current?.play();
        }
      }

      setAlerts(data.alerts);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>🔥 Fire Detection Alerts</h1>

      {/* 🔔 Hidden audio */}
      <audio ref={audioRef} src="/alarm.mp3" />

      {alerts.length === 0 ? (
        <p>No alerts yet</p>
      ) : (
        alerts.map((alert) => (
          <div
            key={alert.id}
            style={{
              border: "2px solid red",
              margin: "10px",
              padding: "10px",
              backgroundColor:
                alert.type === "FIRE" ? "#ffcccc" : "#fff",
            }}
          >
            <h3>{alert.type}</h3>
            <p>Confidence: {alert.confidence.toFixed(2)}</p>
            <p>{alert.timestamp}</p>

            {alert.snapshot && (
              <img
                src={`http://127.0.0.1:8000/${alert.snapshot}`}
                width="300"
                alt="snapshot"
              />
            )}
          </div>
        ))
      )}
    </div>
  );
}