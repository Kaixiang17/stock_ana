import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const API_BASE = "https://stock-ana-dmj1.onrender.com";

function token() {
  return localStorage.getItem("token") || "";
}

async function req(path, opt = {}) {
  const r = await fetch(API_BASE + path, {
    ...opt,
    headers: {
      "Content-Type": "application/json",
      ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
      ...(opt.headers || {}),
    },
  });

  if (!r.ok) {
    throw new Error(await r.text());
  }

  return r.json();
}

function Login({ setAuthed }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({
    email: "demo@bullstreet.ai",
    password: "demo123",
  });
  const [err, setErr] = useState("");

  async function submit(e) {
    e.preventDefault();
    setErr("");

    try {
      const data = await req(
        mode === "login" ? "/auth/login" : "/auth/register",
        {
          method: "POST",
          body: JSON.stringify(form),
        }
      );

      localStorage.setItem("token", data.access_token);
      setAuthed(true);
    } catch (e) {
      setErr("帳密錯誤或帳號已存在");
    }
  }

  return (
    <main className="login">
      <section className="loginCard">
        <div className="brand">
          <div className="logo">B</div>
          <div>
            <h1>BullStreet AI</h1>
            <p>Portfolio intelligence terminal</p>
          </div>
        </div>

        <h2>{mode === "login" ? "登入投資儀表板" : "建立帳號"}</h2>

        <form onSubmit={submit}>
          <input
            placeholder="Email"
            value={form.email}
            onChange={(e) =>
              setForm({
                ...form,
                email: e.target.value,
              })
            }
          />

          <input
            placeholder="Password"
            type="password"
            value={form.password}
            onChange={(e) =>
              setForm({
                ...form,
                password: e.target.value,
              })
            }
          />

          <button>{mode === "login" ? "登入" : "註冊"}</button>
        </form>

        {err && <p className="err">{err}</p>}

        <p
          className="switch"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
        >
          {mode === "login" ? "沒有帳號？建立一個" : "已有帳號？返回登入"}
        </p>

        <small>Demo：demo@bullstreet.ai / demo123</small>
      </section>
    </main>
  );
}

function Dashboard({ setAuthed }) {
  return (
    <main className="login">
      <section className="loginCard">
        <div className="brand">
          <div className="logo">B</div>
          <div>
            <h1>BullStreet AI</h1>
            <p>登入成功</p>
          </div>
        </div>

        <h2>後台已登入</h2>

        <button
          onClick={() => {
            localStorage.removeItem("token");
            setAuthed(false);
          }}
        >
          登出
        </button>
      </section>
    </main>
  );
}

function App() {
  const [authed, setAuthed] = useState(!!token());

  if (!authed) {
    return <Login setAuthed={setAuthed} />;
  }

  return <Dashboard setAuthed={setAuthed} />;
}

createRoot(document.getElementById("root")).render(<App />);
