import React, { useState, useEffect, useRef } from 'react';
import { Shield, ShieldAlert, Activity, Camera, AlertTriangle, Settings, Eye } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function App() {
  const [systemStatus, setSystemStatus] = useState('CONNECTING');
  const [currentRisk, setCurrentRisk] = useState('SAFE'); // SAFE, ALERT, WARNING, HIGH RISK
  const [safetyScore, setSafetyScore] = useState(100);
  const [fps, setFps] = useState(0);
  const [cpu, setCpu] = useState(0);
  const [gpu, setGpu] = useState(0);
  const [emotions, setEmotions] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [chartData, setChartData] = useState([]);

  const wsRef = useRef(null);
  const imgRef = useRef(null);

  useEffect(() => {
    // Initialize WebSocket connection
    connectWebSocket();
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const connectWebSocket = () => {
    setSystemStatus('CONNECTING');
    wsRef.current = new WebSocket('ws://localhost:8000/stream/0');

    wsRef.current.onopen = () => {
      setSystemStatus('CONNECTED');
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'frame' && imgRef.current) {
        // We receive the base64 encoded image directly
        imgRef.current.src = `data:image/jpeg;base64,${data.image}`;
      } else if (data.type === 'analytics') {
        updateAnalytics(data.data);
      }
    };

    wsRef.current.onclose = () => {
      setSystemStatus('DISCONNECTED');
      setTimeout(connectWebSocket, 3000); // Reconnect
    };
  };

  const updateAnalytics = (data) => {
    setCurrentRisk(data.threat_level);
    setSafetyScore(data.safety_score);
    setFps(data.fps);
    setEmotions(data.emotions || {});
    
    setChartData(prev => {
      const newD = [...prev, { time: new Date().toLocaleTimeString(), score: data.safety_score }];
      if (newD.length > 20) newD.shift();
      return newD;
    });

    if (data.threat_level === 'HIGH RISK' && currentRisk !== 'HIGH RISK') {
      // Add alert
      setAlerts(prev => [{
        id: Date.now(),
        time: new Date().toLocaleTimeString(),
        type: 'HIGH RISK',
        desc: 'Panic/Anger spike detected'
      }, ...prev].slice(0, 10));
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'SAFE': return 'text-safeGreen';
      case 'ALERT': return 'text-alertYellow';
      case 'WARNING': return 'text-alertOrange';
      case 'HIGH RISK': return 'text-alertRed neon-text-red';
      default: return 'text-white';
    }
  };

  return (
    <div className="min-h-screen bg-charcoal p-4 font-sans text-gray-200">
      {/* Header */}
      <header className="flex justify-between items-center mb-6 glass-panel p-4 rounded-xl">
        <div className="flex items-center gap-3">
          <Shield className="text-neonCyan w-8 h-8" />
          <div>
            <h1 className="text-2xl font-bold tracking-wider text-white neon-text-cyan">SAFEGUARD AI</h1>
            <p className="text-xs text-gray-400">HUMAN SAFETY & BEHAVIORAL ANALYSIS SYSTEM</p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${systemStatus === 'CONNECTED' ? 'bg-safeGreen shadow-[0_0_8px_#00ff88]' : 'bg-red-500 animate-pulse'}`}></div>
            <span className="text-sm font-mono">{systemStatus}</span>
          </div>
          <div className="flex gap-4">
             <span className="text-xs bg-charcoalLight px-3 py-1 rounded border border-gray-700">CPU: {cpu}%</span>
             <span className="text-xs bg-charcoalLight px-3 py-1 rounded border border-gray-700">FPS: {fps}</span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Video Feed & Charts */}
        <div className="lg:col-span-8 space-y-6">
          {/* Video Feed Panel */}
          <div className="glass-panel rounded-xl overflow-hidden relative border border-gray-800">
            <div className="absolute top-4 left-4 z-10 flex gap-2">
               <div className="bg-black/60 backdrop-blur px-3 py-1 rounded text-xs font-mono border border-gray-600 flex items-center gap-2">
                 <Camera className="w-3 h-3" /> CAM-01 (MAIN)
               </div>
               <div className={`bg-black/60 backdrop-blur px-3 py-1 rounded text-xs font-mono border border-gray-600 ${getRiskColor(currentRisk)} font-bold`}>
                 {currentRisk}
               </div>
            </div>
            
            <div className="aspect-video bg-black flex items-center justify-center relative">
               <img 
                 ref={imgRef} 
                 className="w-full h-full object-cover opacity-90"
                 alt="Live Camera Feed"
               />
               {!imgRef.current?.src && (
                 <div className="text-gray-600 flex flex-col items-center">
                   <Eye className="w-12 h-12 mb-2 opacity-50" />
                   <p className="font-mono text-sm tracking-widest">AWAITING SIGNAL...</p>
                 </div>
               )}
            </div>
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-2 gap-6">
            {/* Safety Graph */}
            <div className="glass-panel p-4 rounded-xl h-64">
              <h3 className="text-sm text-gray-400 mb-4 font-mono flex items-center gap-2">
                <Activity className="w-4 h-4 text-neonCyan" /> SAFETY SCORE TIMELINE
              </h3>
              <ResponsiveContainer width="100%" height="80%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="time" stroke="#666" tick={{fontSize: 10}} />
                  <YAxis domain={[0, 100]} stroke="#666" tick={{fontSize: 10}} />
                  <Tooltip contentStyle={{backgroundColor: '#1e1e1e', borderColor: '#333'}} />
                  <Line type="monotone" dataKey="score" stroke="#00f3ff" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Emotion Bars */}
            <div className="glass-panel p-4 rounded-xl h-64 overflow-y-auto">
              <h3 className="text-sm text-gray-400 mb-4 font-mono">LIVE EMOTION ANALYSIS</h3>
              <div className="space-y-3">
                {Object.entries(emotions).sort((a,b) => b[1] - a[1]).map(([emotion, val]) => (
                  <div key={emotion}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="uppercase text-gray-300">{emotion}</span>
                      <span className="font-mono">{val.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-800 rounded-full h-1.5">
                      <div 
                        className={`h-1.5 rounded-full ${['angry', 'fear', 'disgust', 'sad'].includes(emotion) ? 'bg-alertRed' : 'bg-neonCyan'}`}
                        style={{ width: `${val}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
                {Object.keys(emotions).length === 0 && (
                  <div className="text-center text-gray-600 text-xs mt-10">NO FACE DETECTED</div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Threats & Alerts */}
        <div className="lg:col-span-4 space-y-6">
          
          {/* Threat Meter */}
          <div className="glass-panel p-6 rounded-xl flex flex-col items-center justify-center border-t-4 border-t-neonCyan" style={{ borderTopColor: currentRisk === 'HIGH RISK' ? '#ff003c' : currentRisk === 'WARNING' ? '#ff8c00' : currentRisk === 'ALERT' ? '#ffd700' : '#00ff88'}}>
            <h2 className="text-gray-400 text-sm font-mono mb-4 tracking-widest">SYSTEM THREAT LEVEL</h2>
            <div className={`text-5xl font-bold tracking-widest mb-2 ${getRiskColor(currentRisk)}`}>
              {currentRisk}
            </div>
            <div className="text-4xl font-mono mt-4 font-light text-white">
              {safetyScore}<span className="text-lg text-gray-500">%</span>
            </div>
            <div className="text-xs text-gray-500 mt-1 uppercase">Overall Safety Score</div>
          </div>

          {/* Incident Log */}
          <div className="glass-panel p-4 rounded-xl flex-1 min-h-[400px]">
             <h3 className="text-sm text-gray-400 mb-4 font-mono flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-alertRed" /> RECENT INCIDENTS
              </h3>
              <div className="space-y-3">
                {alerts.length === 0 ? (
                  <div className="text-center text-gray-600 text-xs mt-10">NO RECENT INCIDENTS</div>
                ) : (
                  alerts.map((alert) => (
                    <div key={alert.id} className="bg-red-900/20 border border-red-500/30 p-3 rounded flex gap-3 items-start">
                       <ShieldAlert className="w-5 h-5 text-alertRed shrink-0 mt-0.5" />
                       <div>
                         <div className="flex justify-between items-center mb-1">
                           <span className="text-xs font-bold text-alertRed">{alert.type}</span>
                           <span className="text-[10px] text-gray-400 font-mono">{alert.time}</span>
                         </div>
                         <p className="text-xs text-gray-300">{alert.desc}</p>
                       </div>
                    </div>
                  ))
                )}
              </div>
          </div>

        </div>

      </div>
    </div>
  );
}

export default App;
