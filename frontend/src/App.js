import { useState, useEffect } from "react";

const API_URL = "http://localhost:8000";

export default function App() {
  const [grid, setGrid] = useState(null);

  useEffect(() => {
    fetchGrid();
  }, []);

  const fetchGrid = async () => {
    const res = await fetch(`${API_URL}/grid`);
    const data = await res.json();
    setGrid(data);
  };

  const moveRobot = async (direction) => {
    await fetch(`${API_URL}/move?direction=${direction}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    fetchGrid();
  };

  const pickUpCircle = async () => {
    await fetch(`${API_URL}/pickup`, { method: "POST" });
    fetchGrid();
  };

  const placeCircle = async () => {
    await fetch(`${API_URL}/place`, { method: "POST" });
    console.log("Hello World");
    fetchGrid();
  };

  const downloadHistory = async () => {
    const res = await fetch(`${API_URL}/history`);
    const text = await res.text();
    const blob = new Blob([text], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "movement_history.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const gridSize = 3;
  const renderCell = (x, y) => {
    const isRobot = grid?.robot[0] === x && grid?.robot[1] === y;
    // there may be more than one circle in the same cell, if so, we only render the last one in the array
    const circle = grid?.circles.slice().reverse().find((c) => c[1] === x && c[2] === y);
    let bgColor = "bg-gray-200"; // Default empty cell
    if (circle) {
      if (circle[0] === "red") {
        bgColor = "bg-red-500";
      } else if (circle[0] === "green") {
        bgColor = "bg-green-500";
      } else if (circle[0] === "blue") {
        bgColor = "bg-blue-500";
      }
    }
    console.log("x", x, "y", y, "isRobot", isRobot, "circle", circle);
    return (
      <div
        key={`${x}-${y}`}
        className={`w-32 h-32 border flex items-center justify-center ${bgColor}`}
      >
        {isRobot ?  "🤖" : ""}
      </div>
    );
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Robot Grid Control</h1>
      <div className="grid grid-cols-4 gap-2 mb-4">
        {["up", "left", "right", "down"].map((dir) => (
          <button
            key={dir}
            onClick={() => moveRobot(dir)}
            className="p-2 bg-blue-500 text-white rounded"
          >
            Move {dir}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-1 border border-gray-400 mb-4">
        {Array.from({ length: gridSize }).map((_, y) =>
          Array.from({ length: gridSize }).map((_, x) => renderCell(x, y))
        )}
      </div>
      <div className="flex gap-2">
        <button
          onClick={pickUpCircle}
          className="p-2 bg-yellow-500 text-white rounded"
        >
          Pick Up
        </button>
        <button
          onClick={placeCircle}
          className="p-2 bg-green-500 text-white rounded"
        >
          Place Down
        </button>
        <button
          onClick={downloadHistory}
          className="p-2 bg-red-500 text-white rounded"
        >
          Download History
        </button>
      </div>
    </div>
  );
}
