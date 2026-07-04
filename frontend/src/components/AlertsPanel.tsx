import type { Alert } from "../types";

export function AlertsPanel({ alerts }: { alerts: Alert[] }) {
  return (
    <div className="rounded-xl bg-slate-900 border border-slate-800 p-4">
      <h3 className="font-semibold mb-2">Active Alerts</h3>
      {alerts.length === 0 ? (
        <p className="text-sm text-slate-500">No alerts. All good. ✅</p>
      ) : (
        <ul className="space-y-2 max-h-72 overflow-auto pr-1">
          {alerts.map((a) => (
            <li
              key={a.id}
              className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-2"
            >
              <div className="text-sm">⚠️ {a.message}</div>
              <div className="text-[10px] text-slate-400 mt-1">
                office time {a.simTime} ·{" "}
                {new Date(a.createdAt).toLocaleTimeString()}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
