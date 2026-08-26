const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export function createAnalysis(inputText) {
  return request("/analyses", {
    method: "POST",
    body: JSON.stringify({ input_text: inputText }),
  });
}

export function fetchHistory() {
  return request("/analyses?limit=20");
}

export function fetchAnalysis(id) {
  return request(`/analyses/${id}`);
}

export function fetchDemos() {
  return request("/demos");
}
