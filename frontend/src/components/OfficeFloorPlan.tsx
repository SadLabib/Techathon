import type { Device, RoomId } from "../types";

/**
 * Live top-view office floor plan. Devices are placed in their rooms; lights
 * glow when ON and fans spin when running — all driven by the live snapshot.
 */

interface RoomBox {
  id: RoomId;
  name: string;
  x: number;
  y: number;
  w: number;
  h: number;
  floor: string;
}

const ROOMS: RoomBox[] = [
  { id: "drawing", name: "Drawing Room", x: 30, y: 40, w: 250, h: 352, floor: "#efe7d8" },
  { id: "work1", name: "Work Room 1", x: 286, y: 40, w: 256, h: 352, floor: "#e9ecf1" },
  { id: "work2", name: "Work Room 2", x: 548, y: 40, w: 256, h: 352, floor: "#e7d8bd" },
];

// Placement of each device within its room, as fractions of the room box.
const FAN_POS: Record<number, { fx: number; fy: number }> = {
  1: { fx: 0.5, fy: 0.24 },
  2: { fx: 0.5, fy: 0.66 },
};
const LIGHT_POS: Record<number, { fx: number; fy: number }> = {
  1: { fx: 0.24, fy: 0.16 },
  2: { fx: 0.76, fy: 0.16 },
  3: { fx: 0.5, fy: 0.92 },
};

function deviceIndex(id: string): number {
  return Number(id.split("-").pop());
}

function deviceCenter(device: Device, room: RoomBox): { cx: number; cy: number } {
  const idx = deviceIndex(device.id);
  const pos = device.type === "fan" ? FAN_POS[idx] : LIGHT_POS[idx];
  const p = pos ?? { fx: 0.5, fy: 0.5 };
  return { cx: room.x + room.w * p.fx, cy: room.y + room.h * p.fy };
}

function FanIcon({ cx, cy, on }: { cx: number; cy: number; on: boolean }) {
  const blade = on ? "#6b5335" : "#9aa0a6";
  return (
    <g transform={`translate(${cx}, ${cy})`}>
      <g className={on ? "fan-spin" : undefined}>
        {[0, 120, 240].map((a) => (
          <ellipse
            key={a}
            cx="12"
            cy="0"
            rx="13"
            ry="6"
            fill={blade}
            transform={`rotate(${a})`}
          />
        ))}
      </g>
      <circle r="5" fill={on ? "#4a3728" : "#6b7280"} />
    </g>
  );
}

function LightIcon({ cx, cy, on }: { cx: number; cy: number; on: boolean }) {
  return (
    <g transform={`translate(${cx}, ${cy})`}>
      {on && <circle r="17" fill="#fde68a" opacity="0.55" />}
      <circle
        r="9"
        fill={on ? "#ffdf5e" : "#cbd5e1"}
        stroke={on ? "#f5c542" : "#94a3b8"}
        strokeWidth="2"
        style={on ? { filter: "drop-shadow(0 0 6px rgba(253, 224, 71, 0.95))" } : undefined}
      />
    </g>
  );
}

function Desk({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <rect x={x} y={y} width="54" height="30" rx="3" fill="#b98a5a" stroke="#8a6a44" />
      <rect x={x + 6} y={y + 6} width="18" height="12" rx="2" fill="#3f3f46" />
      <circle cx={x + 27} cy={y + 42} r="7" fill="#52525b" />
    </g>
  );
}

function DrawingFurniture({ room }: { room: RoomBox }) {
  const { x, y } = room;
  return (
    <g opacity="0.9">
      {/* sofa */}
      <rect x={x + 14} y={y + 120} width="34" height="120" rx="8" fill="#cfc4b0" stroke="#a99f88" />
      {/* rug */}
      <rect x={x + 78} y={y + 150} width="120" height="90" rx="6" fill="#dccdae" opacity="0.7" />
      {/* coffee table */}
      <rect x={x + 108} y={y + 178} width="60" height="34" rx="4" fill="#b98a5a" stroke="#8a6a44" />
      {/* armchair */}
      <rect x={x + 40} y={y + 262} width="46" height="46" rx="10" fill="#cfc4b0" stroke="#a99f88" />
    </g>
  );
}

function WorkFurniture({ room }: { room: RoomBox }) {
  const spots = [
    { fx: 0.22, fy: 0.4 },
    { fx: 0.72, fy: 0.4 },
    { fx: 0.22, fy: 0.72 },
    { fx: 0.72, fy: 0.72 },
  ];
  return (
    <g opacity="0.9">
      {spots.map((s, i) => (
        <Desk key={i} x={room.x + room.w * s.fx - 27} y={room.y + room.h * s.fy - 15} />
      ))}
    </g>
  );
}

function Plant({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <circle cx={x} cy={y} r="9" fill="#4ca771" />
      <circle cx={x - 5} cy={y - 4} r="6" fill="#5cba82" />
      <circle cx={x + 5} cy={y - 3} r="6" fill="#3f9463" />
    </g>
  );
}

export function OfficeFloorPlan({
  devices,
  perRoomW,
}: {
  devices: Device[];
  perRoomW: Record<RoomId, number>;
}) {
  return (
    <div className="rounded-xl bg-slate-900 border border-slate-800 p-4">
      <h3 className="font-semibold mb-3">Office Layout — live</h3>
      <svg
        viewBox="0 0 840 540"
        className="w-full h-auto rounded-lg"
        style={{ background: "#f6f1e7" }}
        fontFamily="Segoe UI, Helvetica, Arial, sans-serif"
      >
        {/* room floors */}
        {ROOMS.map((r) => (
          <rect
            key={r.id}
            x={r.x}
            y={r.y}
            width={r.w}
            height={r.h}
            fill={r.floor}
            stroke="#9ca3af"
            strokeWidth="2"
          />
        ))}

        {/* corridor */}
        <rect x={30} y={408} width={774} height={104} fill="#ece5d6" stroke="#9ca3af" strokeWidth="2" />

        {/* outer walls */}
        <rect x={24} y={34} width={786} height={484} fill="none" stroke="#2f2f2f" strokeWidth="6" />

        {/* furniture */}
        <DrawingFurniture room={ROOMS[0]} />
        <WorkFurniture room={ROOMS[1]} />
        <WorkFurniture room={ROOMS[2]} />
        <Plant x={262} y={470} />
        <Plant x={520} y={470} />
        <Plant x={60} y={470} />
        {/* water cooler */}
        <rect x={760} y={452} width={16} height={30} rx="3" fill="#bfe3f0" stroke="#7fb9cc" />

        {/* doors (gaps to corridor) */}
        {[180, 430, 690].map((dx) => (
          <path
            key={dx}
            d={`M ${dx} 392 A 26 26 0 0 1 ${dx + 26} 392`}
            fill="none"
            stroke="#9ca3af"
            strokeWidth="2"
          />
        ))}

        {/* entry arrow */}
        <line x1="417" y1="512" x2="417" y2="486" stroke="#334155" strokeWidth="2" markerEnd="" />
        <path d="M417 484 l-6 10 l12 0 z" fill="#334155" />
        <text x="417" y="530" textAnchor="middle" fontSize="13" fill="#334155">ENTRY</text>

        {/* room labels + live wattage */}
        {ROOMS.map((r) => (
          <g key={r.id}>
            <text x={r.x + r.w / 2} y={r.y + r.h / 2 + 4} textAnchor="middle" fontSize="13" fontWeight="700" fill="#374151" opacity="0.35">
              {r.name}
            </text>
            <text x={r.x + r.w / 2} y={r.y + r.h - 8} textAnchor="middle" fontSize="12" fontWeight="700" fill="#4b5563">
              {perRoomW[r.id]} W
            </text>
          </g>
        ))}

        {/* live devices */}
        {devices.map((d) => {
          const room = ROOMS.find((r) => r.id === d.room);
          if (!room) return null;
          const { cx, cy } = deviceCenter(d, room);
          const on = d.status === "on";
          return d.type === "fan" ? (
            <FanIcon key={d.id} cx={cx} cy={cy} on={on} />
          ) : (
            <LightIcon key={d.id} cx={cx} cy={cy} on={on} />
          );
        })}
      </svg>

      <div className="flex gap-4 mt-3 text-xs text-slate-400">
        <span className="flex items-center gap-1">
          <span className="inline-block h-3 w-3 rounded-full bg-yellow-300" /> light ON
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-3 w-3 rounded-full bg-slate-500" /> off
        </span>
        <span>fans spin when running</span>
      </div>
    </div>
  );
}
