import type { Device } from "../types";

export function DeviceCard({ device }: { device: Device }) {
  const on = device.status === "on";
  return (
    <div
      className={`rounded-lg border p-3 flex flex-col items-center gap-1 transition-colors ${
        on
          ? "border-emerald-500/60 bg-emerald-500/10"
          : "border-slate-700 bg-slate-800/40"
      }`}
    >
      <DeviceIcon type={device.type} on={on} />
      <span className="text-sm font-medium">{device.label}</span>
      <span className={`text-xs ${on ? "text-emerald-400" : "text-slate-500"}`}>
        {on ? `ON · ${device.powerW}W` : "OFF"}
      </span>
    </div>
  );
}

function DeviceIcon({ type, on }: { type: Device["type"]; on: boolean }) {
  if (type === "fan") {
    return (
      <span
        className={`text-3xl leading-none ${
          on ? "fan-spin text-sky-400" : "text-slate-600"
        }`}
      >
        ✳
      </span>
    );
  }
  // light — glows when on
  return (
    <span
      className={`text-3xl leading-none ${on ? "text-yellow-300" : "text-slate-600"}`}
      style={
        on ? { filter: "drop-shadow(0 0 8px rgba(253, 224, 71, 0.9))" } : undefined
      }
    >
      ●
    </span>
  );
}
