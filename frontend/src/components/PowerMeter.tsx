import type { RoomId, Snapshot } from "../types";

const ROOM_NAMES: Record<RoomId, string> = {
  drawing: "Drawing Room",
  work1: "Work Room 1",
  work2: "Work Room 2",
};

export function PowerMeter({ totals }: { totals: Snapshot["totals"] }) {
  const rooms = Object.keys(totals.perRoomW) as RoomId[];
  const max = Math.max(1, ...rooms.map((r) => totals.perRoomW[r]));

  return (
    <div className="rounded-xl bg-slate-900 border border-slate-800 p-4">
      <h3 className="font-semibold mb-2">Power Consumption</h3>
      <div className="text-3xl font-bold text-emerald-400">
        {totals.totalPowerW} W
      </div>
      <div className="text-xs text-slate-400 mb-4">
        Today: {totals.estimatedKWhToday} kWh (estimated)
      </div>
      <div className="space-y-2">
        {rooms.map((r) => (
          <div key={r}>
            <div className="flex justify-between text-xs mb-0.5">
              <span>{ROOM_NAMES[r]}</span>
              <span className="text-slate-400">{totals.perRoomW[r]} W</span>
            </div>
            <div className="h-2 rounded bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all duration-500"
                style={{ width: `${(totals.perRoomW[r] / max) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
