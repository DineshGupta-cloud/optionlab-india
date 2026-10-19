import React, { useState } from "react";
import axios from "axios";

type Leg = {
  action: "BUY" | "SELL";
  option_type: "CE" | "PE";
  strike: number;
  premium: number;
  quantity: number;
};

export default function StrategyBuilder({ templates }: { templates: any[] }) {
  const [legs, setLegs] = useState<Leg[]>([
    { action: "BUY", option_type: "CE", strike: 25000, premium: 150, quantity: 1 },
    { action: "SELL", option_type: "CE", strike: 25200, premium: 70, quantity: 1 },
  ]);
  const [spot, setSpot] = useState<number>(25000);
  const [result, setResult] = useState<any>(null);

  function updateLeg(idx: number, partial: Partial<Leg>) {
    const copy = [...legs];
    copy[idx] = { ...copy[idx], ...partial };
    setLegs(copy);
  }
  function addLeg() {
    setLegs([...legs, { action: "BUY", option_type: "CE", strike: spot, premium: 0, quantity: 1 }]);
  }
  function reset() {
    setLegs([]);
    setResult(null);
  }
  function loadTemplate(t: any) {
    setLegs(t.legs || []);
    if (t.spot) setSpot(t.spot);
  }
  async function analyze() {
    try {
      const resp = await axios.post("http://localhost:8000/api/v1/strategies/analyze", {
        legs,
        spot,
        range_min: Math.max(1, spot * 0.9),
        range_max: spot * 1.1,
        steps: 201,
      });
      setResult(resp.data);
    } catch (err) {
      setResult({ error: "Failed to call API (is backend running?)" });
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 10 }}>
        Templates:{" "}
        {templates.map((t: any, i: number) => (
          <button key={i} onClick={() => loadTemplate(t)} style={{ marginRight: 8 }}>
            {t.name}
          </button>
        ))}
      </div>

      <div style={{ background: "#0b1220", padding: 12, borderRadius: 8 }}>
        <div>
          Spot: <input value={spot} onChange={(e) => setSpot(Number(e.target.value))} />
          <button onClick={addLeg} style={{ marginLeft: 8 }}>Add Leg</button>
          <button onClick={reset} style={{ marginLeft: 8 }}>Reset</button>
          <button onClick={analyze} style={{ marginLeft: 8 }}>Analyze</button>
        </div>

        <table style={{ width: "100%", marginTop: 12 }}>
          <thead>
            <tr>
              <th>Action</th>
              <th>Type</th>
              <th>Strike</th>
              <th>Premium</th>
              <th>Qty</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {legs.map((l, i) => (
              <tr key={i}>
                <td>
                  <select value={l.action} onChange={(e) => updateLeg(i, { action: e.target.value as any })}>
                    <option>BUY</option>
                    <option>SELL</option>
                  </select>
                </td>
                <td>
                  <select value={l.option_type} onChange={(e) => updateLeg(i, { option_type: e.target.value as any })}>
                    <option>CE</option>
                    <option>PE</option>
                  </select>
                </td>
                <td>
                  <input type="number" value={l.strike} onChange={(e) => updateLeg(i, { strike: Number(e.target.value) })} />
                </td>
                <td>
                  <input type="number" value={l.premium} onChange={(e) => updateLeg(i, { premium: Number(e.target.value) })} />
                </td>
                <td>
                  <input type="number" value={l.quantity} onChange={(e) => updateLeg(i, { quantity: Number(e.target.value) })} />
                </td>
                <td>
                  <button onClick={() => setLegs(legs.filter((_, idx) => idx !== i))}>Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div style={{ marginTop: 12 }}>
          <h4>Analysis</h4>
          <pre style={{ maxHeight: 300, overflow: "auto", background: "#021020", padding: 8 }}>
            {result ? JSON.stringify(result, null, 2) : "No results yet"}
          </pre>
        </div>
      </div>
    </div>
  );
}
