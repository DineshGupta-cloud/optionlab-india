import React, { useEffect, useState } from "react";
import axios from "axios";
import StrategyBuilder from "./components/StrategyBuilder";

export default function App() {
  const [templates, setTemplates] = useState<any[]>([]);
  useEffect(() => {
    axios.get("http://localhost:8000/api/v1/strategies/templates").then((r) => {
      setTemplates(r.data.templates || []);
    }).catch(()=>{});
  }, []);
  return (
    <div style={{ background: "#071127", color: "#cbd5e1", minHeight: "100vh", padding: 20 }}>
      <header style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom: 20 }}>
        <h1>OptionLab India — DEMO DATA — PAPER MODE</h1>
        <div>Market: NIFTY 50 • Spot: ₹25,000</div>
      </header>
      <main>
        <StrategyBuilder templates={templates} />
      </main>
    </div>
  );
}
