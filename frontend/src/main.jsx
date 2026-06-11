const API_BASE = "https://stock-ana-dmj1.onrender.com";

function token() {
  return localStorage.getItem("token") || "";
}

async function req(path, opt = {}) {
  const r = await fetch(`${API_BASE}${path}`, {
    ...opt,
    headers: {
      "Content-Type": "application/json",
      ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
      ...(opt.headers || {})
    }
  });

  if (!r.ok) {
    throw new Error(await r.text());
  }

  return r.json();
}
