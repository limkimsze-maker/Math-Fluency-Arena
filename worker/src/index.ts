import { DurableObject } from "cloudflare:workers";

interface AppEnv {
  MY_DURABLE_OBJECT: DurableObjectNamespace;
  CREATOR_PASSWORD: string;
}

// Up to 500 teacher/public rooms may exist at once.
// The password-protected creator room is separate and does not count toward this limit.
const PUBLIC_ROOM_LIMIT = 500;
const ROOM_RELEASE_DELAY_MS = 2 * 60 * 1000;
const RESERVATION_TIMEOUT_MS = 2 * 60 * 1000;

type RoomRecord = {
  createdAt: number;
  active: boolean;
};

type CreatorRoomRecord = {
  code: string;
  createdAt: number;
  active: boolean;
};

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json;charset=UTF-8",
      "access-control-allow-origin": "*",
    },
  });
}

function makeRoomCode(usedCodes: Set<string>): string {
  for (let i = 0; i < 1000; i++) {
    const code = String(Math.floor(1000 + Math.random() * 9000));
    if (!usedCodes.has(code)) return code;
  }
  throw new Error("Unable to generate room code.");
}

export class MyDurableObject extends DurableObject<AppEnv> {
  private appEnv: AppEnv;

  constructor(ctx: DurableObjectState, env: AppEnv) {
    super(ctx, env);
    this.appEnv = env;
  }

  private capacityStub() {
    const id = this.appEnv.MY_DURABLE_OBJECT.idFromName("__CAPACITY__");
    return this.appEnv.MY_DURABLE_OBJECT.get(id);
  }

  private async getPublicRooms(): Promise<Record<string, RoomRecord>> {
    return (
      (await this.ctx.storage.get<Record<string, RoomRecord>>("publicRooms")) || {}
    );
  }

  private async getCreatorRoom(): Promise<CreatorRoomRecord | null> {
    return (
      (await this.ctx.storage.get<CreatorRoomRecord>("creatorRoom")) || null
    );
  }

  private async cleanupReservations() {
    const now = Date.now();
    const publicRooms = await this.getPublicRooms();
    let publicChanged = false;

    for (const [code, room] of Object.entries(publicRooms)) {
      if (!room.active && now - room.createdAt > RESERVATION_TIMEOUT_MS) {
        delete publicRooms[code];
        publicChanged = true;
      }
    }

    if (publicChanged) {
      await this.ctx.storage.put("publicRooms", publicRooms);
    }

    const creatorRoom = await this.getCreatorRoom();
    if (
      creatorRoom &&
      !creatorRoom.active &&
      now - creatorRoom.createdAt > RESERVATION_TIMEOUT_MS
    ) {
      await this.ctx.storage.delete("creatorRoom");
    }
  }

  private async scheduleCapacityCleanup() {
    await this.ctx.storage.setAlarm(Date.now() + RESERVATION_TIMEOUT_MS);
  }

  private async handleCapacityRequest(request: Request): Promise<Response> {
    await this.ctx.storage.put("objectRole", "capacity");

    const url = new URL(request.url);
    const path = url.pathname;

    await this.cleanupReservations();

    // PUBLIC TEACHER: CREATE ROOM
    // Teacher/public rooms are capped at 500. Creator room is separate.
    if (path === "/capacity/reserve-public") {
      const publicRooms = await this.getPublicRooms();

      if (Object.keys(publicRooms).length >= PUBLIC_ROOM_LIMIT) {
        return jsonResponse(
          {
            ok: false,
            full: true,
            message: "All 500 teacher rooms are currently in use. Please try again later.",
          },
          429,
        );
      }

      const creatorRoom = await this.getCreatorRoom();
      const used = new Set(Object.keys(publicRooms));
      if (creatorRoom) used.add(creatorRoom.code);

      const code = makeRoomCode(used);
      publicRooms[code] = {
        createdAt: Date.now(),
        active: false,
      };

      await this.ctx.storage.put("publicRooms", publicRooms);
      await this.scheduleCapacityCleanup();

      return jsonResponse({
        ok: true,
        code,
        type: "public",
      });
    }

    // PASSWORD-PROTECTED CREATOR ROOM
    if (path === "/capacity/reserve-creator") {
      let creatorRoom = await this.getCreatorRoom();
      if (creatorRoom) {
        return jsonResponse({
          ok: true,
          code: creatorRoom.code,
          type: "creator",
        });
      }

      const publicRooms = await this.getPublicRooms();
      const used = new Set(Object.keys(publicRooms));
      const code = makeRoomCode(used);

      creatorRoom = {
        code,
        createdAt: Date.now(),
        active: false,
      };

      await this.ctx.storage.put("creatorRoom", creatorRoom);
      await this.scheduleCapacityCleanup();

      return jsonResponse({
        ok: true,
        code,
        type: "creator",
      });
    }

    // CHECK WHETHER A ROOM EXISTS
    if (path === "/capacity/check") {
      const code = url.searchParams.get("room") || "";
      const publicRooms = await this.getPublicRooms();

      if (publicRooms[code]) {
        return jsonResponse({ ok: true, valid: true, type: "public" });
      }

      const creatorRoom = await this.getCreatorRoom();
      if (creatorRoom && creatorRoom.code === code) {
        return jsonResponse({ ok: true, valid: true, type: "creator" });
      }

      return jsonResponse(
        { ok: false, valid: false, message: "That room is not active." },
        404,
      );
    }

    // MARK ROOM ACTIVE WHEN A WEBSOCKET ENTERS IT
    if (path === "/capacity/mark-active") {
      const code = url.searchParams.get("room") || "";
      const publicRooms = await this.getPublicRooms();

      if (publicRooms[code]) {
        publicRooms[code].active = true;
        await this.ctx.storage.put("publicRooms", publicRooms);
        return jsonResponse({ ok: true });
      }

      const creatorRoom = await this.getCreatorRoom();
      if (creatorRoom && creatorRoom.code === code) {
        creatorRoom.active = true;
        await this.ctx.storage.put("creatorRoom", creatorRoom);
        return jsonResponse({ ok: true });
      }

      return jsonResponse({ ok: false }, 404);
    }

    // RELEASE ROOM AFTER EVERYONE HAS LEFT AND THE RECONNECT GRACE PERIOD PASSES
    if (path === "/capacity/release") {
      const code = url.searchParams.get("room") || "";
      const publicRooms = await this.getPublicRooms();

      if (publicRooms[code]) {
        delete publicRooms[code];
        await this.ctx.storage.put("publicRooms", publicRooms);
        return jsonResponse({ ok: true, released: "public" });
      }

      const creatorRoom = await this.getCreatorRoom();
      if (creatorRoom && creatorRoom.code === code) {
        await this.ctx.storage.delete("creatorRoom");
        return jsonResponse({ ok: true, released: "creator" });
      }

      return jsonResponse({ ok: true, released: "none" });
    }

    return jsonResponse({ ok: false }, 404);
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname.startsWith("/capacity/")) {
      return this.handleCapacityRequest(request);
    }

    if (request.headers.get("Upgrade") !== "websocket") {
      return new Response("Expected WebSocket connection", { status: 426 });
    }

    const roomCode = url.pathname.split("/")[2] || "";
    const capacity = this.capacityStub();

    const checkResponse = await capacity.fetch(
      "https://capacity/capacity/check?room=" + encodeURIComponent(roomCode),
    );

    if (!checkResponse.ok) {
      return new Response("Room is not active.", { status: 403 });
    }

    await capacity.fetch(
      "https://capacity/capacity/mark-active?room=" + encodeURIComponent(roomCode),
      { method: "POST" },
    );

    await this.ctx.storage.put("objectRole", "room");
    await this.ctx.storage.put("roomCode", roomCode);

    // Someone returned, so cancel any pending release alarm.
    await this.ctx.storage.deleteAlarm();

    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    this.ctx.acceptWebSocket(server);

    return new Response(null, {
      status: 101,
      webSocket: client,
    });
  }

  webSocketMessage(sender: WebSocket, message: string | ArrayBuffer) {
    for (const socket of this.ctx.getWebSockets()) {
      if (socket !== sender && socket.readyState === WebSocket.OPEN) {
        socket.send(message);
      }
    }
  }

  webSocketClose(
    _socket: WebSocket,
    _code: number,
    _reason: string,
    _wasClean: boolean,
  ) {
    if (this.ctx.getWebSockets().length === 0) {
      this.ctx.waitUntil(
        this.ctx.storage.setAlarm(Date.now() + ROOM_RELEASE_DELAY_MS),
      );
    }
  }

  webSocketError(_socket: WebSocket, error: unknown) {
    console.error("WebSocket error:", error);
    if (this.ctx.getWebSockets().length === 0) {
      this.ctx.waitUntil(
        this.ctx.storage.setAlarm(Date.now() + ROOM_RELEASE_DELAY_MS),
      );
    }
  }

  async alarm() {
    const role = await this.ctx.storage.get<string>("objectRole");

    if (role === "capacity") {
      await this.cleanupReservations();
      return;
    }

    if (role === "room" && this.ctx.getWebSockets().length === 0) {
      const roomCode = await this.ctx.storage.get<string>("roomCode");
      if (roomCode) {
        const capacity = this.capacityStub();
        await capacity.fetch(
          "https://capacity/capacity/release?room=" +
            encodeURIComponent(roomCode),
          { method: "POST" },
        );
      }
    }
  }
}

export default {
  async fetch(request: Request, env: AppEnv): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-methods": "GET, POST, OPTIONS",
          "access-control-allow-headers": "content-type",
        },
      });
    }

    const capacityId = env.MY_DURABLE_OBJECT.idFromName("__CAPACITY__");
    const capacity = env.MY_DURABLE_OBJECT.get(capacityId);

    if (url.pathname === "/api/create-room") {
      return capacity.fetch("https://capacity/capacity/reserve-public", {
        method: "POST",
      });
    }

    if (url.pathname === "/api/creator-room") {
      if (request.method !== "POST") {
        return jsonResponse({ ok: false }, 405);
      }

      let body: { password?: string } | undefined;
      try {
        body = await request.json();
      } catch {
        return jsonResponse({ ok: false, message: "Invalid request." }, 400);
      }

      if (!env.CREATOR_PASSWORD || body?.password !== env.CREATOR_PASSWORD) {
        return jsonResponse(
          { ok: false, message: "Incorrect creator password." },
          403,
        );
      }

      return capacity.fetch("https://capacity/capacity/reserve-creator", {
        method: "POST",
      });
    }

    if (url.pathname === "/api/join-room") {
      const code = (url.searchParams.get("code") || "")
        .replace(/[^0-9]/g, "")
        .slice(0, 4);

      if (code.length !== 4) {
        return jsonResponse(
          { ok: false, message: "Please enter a 4-digit room code." },
          400,
        );
      }

      return capacity.fetch(
        "https://capacity/capacity/check?room=" + encodeURIComponent(code),
      );
    }

    if (url.pathname.startsWith("/room/")) {
      const roomCode = url.pathname.split("/")[2] || "";
      const id = env.MY_DURABLE_OBJECT.idFromName(roomCode);
      const room = env.MY_DURABLE_OBJECT.get(id);
      return room.fetch(request);
    }

    return new Response("Math Star Chase and Bank live service", {
      headers: { "content-type": "text/plain;charset=UTF-8" },
    });
  },
} satisfies ExportedHandler<AppEnv>;
