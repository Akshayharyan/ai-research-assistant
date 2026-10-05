const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "The backend request failed.");
  }

  return data;
}

export function getDocumentId(document) {
  return document?.document_id || document?.id || document?._id;
}

export function getDocumentName(document) {
  return document?.filename || document?.name || "Untitled PDF";
}

export function getDocuments() {
  return request("/documents");
}

export function uploadDocument(file) {
  const body = new FormData();
  body.append("file", file);
  return request("/upload", { method: "POST", body });
}

export function deleteDocument(documentId) {
  return request(`/documents/${documentId}`, { method: "DELETE" });
}

export function askQuestion(question, documentId) {
  return request("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, document_id: documentId, top_k: 3 }),
  });
}
