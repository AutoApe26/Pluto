import { useEffect, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { Toaster } from "sonner";
import { Header } from "./components/Header";
import { BottomNav } from "./components/BottomNav";
import { CreatePostModal } from "./components/CreatePostModal";
import { Landing } from "./pages/Landing";
import { Feed } from "./pages/Feed";
import { MusicPage } from "./pages/Music";
import { Moderation } from "./pages/Moderation";
import { api } from "./lib/api";

function Shell() {
  const [topics, setTopics] = useState([]);
  const [createOpen, setCreateOpen] = useState(false);
  const [postsRefresh, setPostsRefresh] = useState(0);
  const loc = useLocation();
  const isMod = loc.pathname.startsWith("/mod-station");

  useEffect(() => {
    api.topics().then(setTopics).catch(() => {});
  }, []);

  return (
    <div className="App min-h-screen relative">
      {!isMod && <Header onCreate={() => setCreateOpen(true)} />}
      <main className="relative z-10">
        <Routes>
          <Route
            path="/"
            element={<Landing onCreate={() => setCreateOpen(true)} />}
          />
          <Route path="/feed" element={<Feed topics={topics} key={postsRefresh} />} />
          <Route path="/music" element={<MusicPage />} />
          <Route path="/mod-station" element={<Moderation />} />
        </Routes>
      </main>
      {!isMod && <BottomNav onCreate={() => setCreateOpen(true)} />}
      <CreatePostModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        topics={topics}
        onCreated={() => setPostsRefresh((v) => v + 1)}
      />
      <Toaster
        theme="dark"
        position="top-center"
        toastOptions={{
          style: {
            background: "rgba(18, 18, 25, 0.95)",
            border: "1px solid rgba(255,255,255,0.1)",
            color: "#fff",
            backdropFilter: "blur(20px)",
          },
        }}
      />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Shell />
    </BrowserRouter>
  );
}

export default App;
