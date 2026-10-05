import { useCallback, useEffect, useState } from "react";
import "./App.css";
import AnswerCard from "./components/AnswerCard";
import ChatBox from "./components/ChatBox";
import Sidebar from "./components/Sidebar";
import WelcomeScreen from "./components/WelcomeScreen";
import {
  askQuestion,
  deleteDocument,
  getDocumentId,
  getDocumentName,
  getDocuments,
  uploadDocument,
} from "./services/api";

function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const fetchDocuments = useCallback(async () => {
    setLoadingDocuments(true);
    try {
      const data = await getDocuments();
      setDocuments(data.documents || []);
      setError("");
    } catch (requestError) {
      setError(`Could not load your library: ${requestError.message}`);
    } finally {
      setLoadingDocuments(false);
    }
  }, []);

  // Initial library loading synchronizes the component with the backend.
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { fetchDocuments(); }, [fetchDocuments]);

  async function handleUpload(event) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please select a PDF file.");
      return;
    }
    setUploading(true);
    setError("");
    setNotice("Processing your PDF...");
    try {
      const uploaded = await uploadDocument(file);
      await fetchDocuments();
      setSelectedDocument(uploaded);
      setNotice("Document ready.");
    } catch (requestError) {
      setNotice("");
      setError(`Upload failed: ${requestError.message}`);
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(document) {
    const name = getDocumentName(document);
    if (!window.confirm(`Delete “${name}”? This cannot be undone.`)) return;
    const documentId = getDocumentId(document);
    setDeletingId(documentId);
    setError("");
    try {
      await deleteDocument(documentId);
      if (getDocumentId(selectedDocument) === documentId) {
        setSelectedDocument(null);
        setAnswer("");
        setSources([]);
      }
      setNotice("Document deleted.");
      await fetchDocuments();
    } catch (requestError) {
      setError(`Could not delete document: ${requestError.message}`);
    } finally {
      setDeletingId(null);
    }
  }

  async function handleAsk() {
    if (!selectedDocument || !question.trim()) return;
    setAsking(true);
    setAnswer("");
    setSources([]);
    setError("");
    try {
      const data = await askQuestion(question.trim(), getDocumentId(selectedDocument));
      setAnswer(data.answer || "No answer was returned.");
      setSources(data.sources || []);
      setQuestion("");
    } catch (requestError) {
      setError(`Could not get an answer: ${requestError.message}`);
    } finally {
      setAsking(false);
    }
  }

  function handleSelect(document) {
    setSelectedDocument(document);
    setQuestion("");
    setAnswer("");
    setSources([]);
    setError("");
    setNotice("");
  }

  const hasResult = asking || Boolean(answer);

  return (
    <div className="app">
      <Sidebar
        documents={documents}
        selectedDocument={selectedDocument}
        loading={loadingDocuments}
        uploading={uploading}
        deletingId={deletingId}
        onUpload={handleUpload}
        onSelect={handleSelect}
        onDelete={handleDelete}
      />
      <main className="main">
        <header className="topbar">
          <span>Workspace / <strong>{selectedDocument ? getDocumentName(selectedDocument) : "New conversation"}</strong></span>
          <span className="status"><span className="status-dot" /> AI Assistant</span>
        </header>
        {(error || notice) && (
          <div className={`feedback ${error ? "feedback-error" : "feedback-success"}`} role={error ? "alert" : "status"}>
            <span>{error || notice}</span>
            <button type="button" onClick={() => { setError(""); setNotice(""); }} aria-label="Dismiss message">×</button>
          </div>
        )}
        {!hasResult && <WelcomeScreen hasDocuments={documents.length > 0} />}
        {hasResult && <AnswerCard answer={answer} sources={sources} asking={asking} />}
        <ChatBox
          document={selectedDocument}
          question={question}
          asking={asking}
          onChange={setQuestion}
          onSubmit={handleAsk}
        />
      </main>
    </div>
  );
}

export default App;
