import axios from "axios";
import { getDeviceId, MOD_KEY_STORAGE } from "./device";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const client = axios.create({ baseURL: API });

export const api = {
  // topics
  topics: () => client.get("/topics").then((r) => r.data),

  // posts
  posts: (topic) =>
    client
      .get("/posts", { params: topic && topic !== "all" ? { topic } : {} })
      .then((r) => r.data),
  trendingPosts: () => client.get("/posts/trending").then((r) => r.data),
  createPost: (data) =>
    client
      .post("/posts", { ...data, device_id: getDeviceId() })
      .then((r) => r.data),
  reactPost: (id, type) =>
    client
      .post(`/posts/${id}/reaction`, { type, device_id: getDeviceId() })
      .then((r) => r.data),
  myPostReaction: (id) =>
    client
      .get(`/posts/${id}/my-reaction`, { params: { device_id: getDeviceId() } })
      .then((r) => r.data),

  // music
  music: () => client.get("/music").then((r) => r.data),
  featuredMusic: () => client.get("/music/featured").then((r) => r.data),
  uploadMusic: (data) =>
    client
      .post("/music", { ...data, device_id: getDeviceId() })
      .then((r) => r.data),
  reactMusic: (id, type) =>
    client
      .post(`/music/${id}/reaction`, { type, device_id: getDeviceId() })
      .then((r) => r.data),
  myReaction: (id) =>
    client
      .get(`/music/${id}/my-reaction`, { params: { device_id: getDeviceId() } })
      .then((r) => r.data),

  // reports
  report: (target_type, target_id, reason = "") =>
    client
      .post("/reports", {
        target_type,
        target_id,
        reason,
        device_id: getDeviceId(),
      })
      .then((r) => r.data),

  // moderation
  modReported: () =>
    client
      .get("/mod/reported", {
        headers: { "X-Mod-Key": localStorage.getItem(MOD_KEY_STORAGE) || "" },
      })
      .then((r) => r.data),
  modDelete: (target_type, target_id) =>
    client
      .post(
        `/mod/${target_type}/${target_id}/delete`,
        {},
        {
          headers: {
            "X-Mod-Key": localStorage.getItem(MOD_KEY_STORAGE) || "",
          },
        }
      )
      .then((r) => r.data),
  modSafe: (target_type, target_id) =>
    client
      .post(
        `/mod/${target_type}/${target_id}/safe`,
        {},
        {
          headers: {
            "X-Mod-Key": localStorage.getItem(MOD_KEY_STORAGE) || "",
          },
        }
      )
      .then((r) => r.data),
};
