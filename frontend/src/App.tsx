import { useLiveState } from "./useLiveState";
import { RoomPanel } from "./components/RoomPanel";
import { PowerMeter } from "./components/PowerMeter";
import { AlertsPanel } from "./components/AlertsPanel";
import type { RoomId } from "./types";

const ROOMS: RoomId[] = ["drawing", "work1", "work2"];

export default function App() {
  const { snapshot, connected } = useLiveState();

  return (
    <div className="min-h-screen p-4 sm:p-6 max-w-6xl mx-auto">
      <header className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Office Energy Monitor</h1>
          <p className="text-sm text-slate-400">
            Live device &amp; power monitoring
          </p>
        </div>
        <div className="text-right">
          <div className="flex items-center gap-2 justify-end">
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                connected ? "bg-emerald-500" : "bg-red-500 animate-pulse"
              }`}
            />
            <span className="text-sm">
              {connected ? "Live" : "Reconnecting…"}
            </span>
          </div>
          {snapshot && (
            <div className="text-xs text-slate-400">
              Office time: {snapshot.simTime}
            </div>
          )}
        </div>
      </header>

      {!snapshot ? (
        <p className="text-slate-400">Connecting to backend…</p>
      ) : (
        <div className="grid lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 space-y-4">
            {ROOMS.map((room) => (
              <RoomPanel
                key={room}
                room={room}
                devices={snapshot.devices.filter((d) => d.room === room)}
                power={snapshot.totals.perRoomW[room]}
              />
            ))}
          </div>
          <div className="space-y-4">
            <PowerMeter totals={snapshot.totals} />
            <AlertsPanel alerts={snapshot.alerts} />
          </div>
        </div>
      )}
    </div>
  );
}
