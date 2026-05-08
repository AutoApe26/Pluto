// Anonymous device id stored in localStorage
const KEY = "pluto.device_id";

export function getDeviceId() {
  let id = localStorage.getItem(KEY);
  if (!id) {
    id =
      "dev_" +
      (crypto?.randomUUID?.() ||
        Math.random().toString(36).slice(2) + Date.now().toString(36));
    localStorage.setItem(KEY, id);
  }
  return id;
}

export const MOD_KEY_STORAGE = "pluto.mod_key";
