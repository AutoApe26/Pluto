import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Loader2, Ghost } from "lucide-react";
import { PostCard } from "../components/PostCard";
import { api } from "../lib/api";

/**
 * Single-post page used as the destination of share links
 * (https://<app>/post/<id>). If the post is missing, hidden, or already
 * expired (24h), we show a friendly "this pluck has vanished" state.
 */
export const PostPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setNotFound(false);
    api
      .getPost(id)
      .then((p) => {
        if (cancelled) return;
        setPost(p);
      })
      .catch(() => {
        if (cancelled) return;
        setNotFound(true);
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  return (
    <div className="min-h-screen pt-20 sm:pt-24 pb-28 px-4">
      <div className="max-w-2xl mx-auto">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-zinc-400 hover:text-white transition mb-4"
          data-testid="post-page-back"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to feed
        </button>

        {loading && (
          <div className="glass rounded-3xl p-10 flex flex-col items-center gap-3 text-zinc-400">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span className="text-xs font-mono uppercase tracking-widest">
              Fetching pluck…
            </span>
          </div>
        )}

        {!loading && notFound && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-3xl p-10 flex flex-col items-center gap-3 text-center"
            data-testid="post-not-found"
          >
            <Ghost className="w-10 h-10 text-purple-300" />
            <h2 className="font-display text-2xl">This pluck has vanished</h2>
            <p className="text-sm text-zinc-400 max-w-sm">
              Posts on Pluto disappear after 24 hours. The link you opened
              might be from an expired or removed pluck.
            </p>
            <button
              onClick={() => navigate("/feed")}
              className="mt-2 inline-flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-purple-500 via-fuchsia-500 to-pink-500 hover:opacity-95 transition shadow-lg shadow-purple-500/30"
            >
              Explore the feed
            </button>
          </motion.div>
        )}

        {!loading && post && (
          <div data-testid="single-post-view">
            <PostCard post={post} index={0} />
          </div>
        )}
      </div>
    </div>
  );
};

export default PostPage;
