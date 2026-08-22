const BASE = "http://localhost:8000";

export async function fetchAchievements() {
  const res = await fetch(`${BASE}/achievements`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updateState(api_name, state) {
  const res = await fetch(`${BASE}/achievements/${encodeURIComponent(api_name)}/state`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
