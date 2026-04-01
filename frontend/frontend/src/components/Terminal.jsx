import React from 'react';

const Terminal = ({ logs }) => {
  return (
    <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm h-64 overflow-y-auto border border-gray-700 shadow-2xl">
      <div className="flex gap-2 mb-2 border-b border-gray-800 pb-1">
        <div className="w-3 h-3 rounded-full bg-red-500"></div>
        <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
        <div className="w-3 h-3 rounded-full bg-green-500"></div>
        <span className="text-gray-500 ml-2 text-xs">soar_playbook_logs.sh</span>
      </div>
      {logs.map((log, index) => (
        <div key={index} className="mb-1">
          <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span> {log}
        </div>
      ))}
      {logs.length === 0 && <div className="text-gray-600 italic">Waiting for input...</div>}
    </div>
  );
};

export default Terminal;