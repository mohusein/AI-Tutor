import { useEffect, useMemo, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function api(path, { token, ...options } = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Something went wrong. Please try again.");
  return data;
}

function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem("tutor-token") || "");
  const [user, setUser] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem("tutor-user") || "null"); }
    catch { return null; }
  });
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [lessons, setLessons] = useState([]);
  const [progress, setProgress] = useState([]);
  const [notice, setNotice] = useState("");

  const completed = useMemo(
    () => new Set(progress.filter((item) => item.completed).map((item) => item.lesson_id)),
    [progress],
  );

  useEffect(() => {
    api("/api/lessons").then(setLessons).catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!token) return;
    api("/api/progress", { token })
      .then(setProgress)
      .catch((err) => {
        setError(err.message);
        if (err.message.includes("session")) signOut();
      });
  }, [token]);

  function signOut() {
    sessionStorage.removeItem("tutor-token");
    sessionStorage.removeItem("tutor-user");
    setToken("");
    setUser(null);
    setProgress([]);
    setNotice("");
  }

  async function submitAuth(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const result = await api(`/api/auth/${mode === "register" ? "register" : "login"}`, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      sessionStorage.setItem("tutor-token", result.access_token);
      sessionStorage.setItem("tutor-user", JSON.stringify(result.user));
      setToken(result.access_token);
      setUser(result.user);
      setPassword("");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function markComplete(lessonId) {
    setError("");
    setNotice("");
    try {
      const result = await api(`/api/progress/${lessonId}`, {
        token,
        method: "PUT",
        body: JSON.stringify({ completed: !completed.has(lessonId), last_position: 1 }),
      });
      setProgress((current) => [
        ...current.filter((item) => item.lesson_id !== lessonId),
        result,
      ]);
      setNotice("Progress saved to your account.");
    } catch (err) {
      setError(err.message);
    }
  }

  const progressPercent = lessons.length
    ? Math.round((completed.size / lessons.length) * 100)
    : 0;

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="Northstar home">
          <span className="brand-mark">N</span>
          <span>northstar<span className="brand-dot">.</span></span>
        </a>
        <div className="topbar-right">
          <span className="pilot-label"><span className="status-dot" /> Learning space</span>
          {user && <button className="quiet-button" onClick={signOut}>Sign out</button>}
        </div>
      </header>

      {!token ? (
        <main className="auth-layout">
          <section className="welcome-panel">
            <div className="eyebrow"><span className="eyebrow-line" /> YOUR LEARNING, IN MOTION</div>
            <h1>Small steps.<br /><em>Bright futures.</em></h1>
            <p className="welcome-copy">A calm space to learn at your pace, practice what matters, and see how far you’ve come.</p>
            <div className="orbit-art" aria-hidden="true">
              <div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="orbit-core">✳</div>
              <span className="orbit-note note-one">curiosity</span><span className="orbit-note note-two">progress</span>
            </div>
            <p className="welcome-foot">A little learning, every day.</p>
          </section>

          <section className="auth-card">
            <div className="card-kicker">STUDENT PORTAL</div>
            <h2>{mode === "login" ? "Welcome back" : "Create your account"}</h2>
            <p className="card-copy">{mode === "login" ? "Pick up where your curiosity left off." : "Your learning journey starts here."}</p>
            <form onSubmit={submitAuth}>
              <label htmlFor="email">Email address</label>
              <input id="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
              <label htmlFor="password">Password</label>
              <input id="password" type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} minLength={10} required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 10 characters" />
              {error && <div className="error-message" role="alert">{error}</div>}
              <button className="primary-button auth-submit" disabled={busy}>{busy ? "One moment…" : mode === "login" ? "Sign in" : "Create account"} <span>→</span></button>
            </form>
            <p className="switch-mode">
              {mode === "login" ? "New to Northstar?" : "Already have an account?"}
              <button onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>
                {mode === "login" ? "Create an account" : "Sign in"}
              </button>
            </p>
            <div className="privacy-note"><span>⌑</span> Your progress is saved to your account.</div>
          </section>
        </main>
      ) : (
        <main className="dashboard">
          <section className="dashboard-heading">
            <div>
              <div className="eyebrow"><span className="eyebrow-line" /> YOUR LEARNING SPACE</div>
              <h1>Good to see you<span className="brand-dot">,</span><br /><em>{user?.email?.split("@")[0]}</em></h1>
              <p className="welcome-copy">A little progress adds up. Choose a lesson and keep going.</p>
            </div>
            <div className="progress-card">
              <div className="progress-head"><span>YOUR MOMENTUM</span><span>{completed.size} / {lessons.length}</span></div>
              <div className="progress-track"><div style={{ width: `${progressPercent}%` }} /></div>
              <strong>{progressPercent}% <small>of your path completed</small></strong>
              <span className="progress-caption">Every lesson is a step forward.</span>
            </div>
          </section>

          <section className="lesson-section">
            <div className="section-heading">
              <div><div className="card-kicker">A GOOD PLACE TO BEGIN</div><h2>Your learning path</h2></div>
              <span className="lesson-count">{lessons.length} short lessons</span>
            </div>
            {error && <div className="error-message inline-error" role="alert">{error}</div>}
            {notice && <div className="success-message" role="status">{notice}</div>}
            <div className="lesson-grid">
              {lessons.map((lesson, index) => {
                const isComplete = completed.has(lesson.id);
                return (
                  <article className={`lesson-card ${isComplete ? "is-complete" : ""}`} key={lesson.id}>
                    <div className="lesson-card-top">
                      <span className="lesson-number">{String(index + 1).padStart(2, "0")}</span>
                      <span className="lesson-duration">{lesson.duration}</span>
                    </div>
                    <div className="subject-pill">{lesson.subject}</div>
                    <h3>{lesson.title}</h3>
                    <p>{lesson.description}</p>
                    <button className={isComplete ? "complete-button done" : "complete-button"} onClick={() => markComplete(lesson.id)}>
                      <span className="check-icon">{isComplete ? "✓" : "○"}</span>
                      {isComplete ? "Completed" : "Mark complete"}
                      <span className="button-arrow">{isComplete ? "↺" : "→"}</span>
                    </button>
                  </article>
                );
              })}
            </div>
          </section>
          <section className="tutor-next">
            <div className="tutor-spark">✳</div>
            <div><span className="card-kicker">COMING UP</span><h2>Your AI tutor is getting ready.</h2><p>Next, we’ll add guided hints and explanations to each lesson.</p></div>
            <span className="tutor-next-tag">NEXT MILESTONE</span>
          </section>
        </main>
      )}
      <footer className="footer"><span>northstar<span className="brand-dot">.</span></span><span>Made for curious minds</span></footer>
    </div>
  );
}

export default App;
