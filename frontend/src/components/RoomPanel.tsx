import type { Device, RoomId } from "../types";
import { DeviceCard } from "./DeviceCard";

const ROOM_NAMES: Record<RoomId, string> = {
  drawing: "Drawing Room",
  work1: "Work Room 1",
  work2: "Work Room 2",
};

export function RoomPanel({
  room,
  devices,
  power,
}: {
  room: RoomId;
  devices: Device[];
  power: number;
}) {
  const onCount = devices.filter((d) => d.status === "on").length;
  return (
    <div className="rounded-xl bg-slate-900 border border-slate-800 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">{ROOM_NAMES[room]}</h3>
        <span className="text-xs text-slate-400">
          {onCount}/{devices.length} on · {power} W
        </span>
      </div>
      <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
        {devices.map((d) => (
          <DeviceCard key={d.id} device={d} />
        ))}
      </div>
    </div>
  );
}
