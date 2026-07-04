export type DeviceType = "fan" | "light";
export type RoomId = "drawing" | "work1" | "work2";

export interface Device {
  id: string;
  label: string;
  type: DeviceType;
  room: RoomId;
  status: "on" | "off";
  powerW: number;
  lastChanged: string;
}

export interface Alert {
  id: string;
  severity: "info" | "warning";
  message: string;
  room?: RoomId | null;
  createdAt: string;
  simTime: string;
}

export interface Snapshot {
  devices: Device[];
  totals: {
    totalPowerW: number;
    perRoomW: Record<RoomId, number>;
    estimatedKWhToday: number;
  };
  alerts: Alert[];
  serverTime: string;
  simTime: string;
}
