import { getDocumentId, getDocumentName } from "../services/api";

function Sidebar({
  documents,
  selectedDocument,
  loading,
  uploading,
  deletingId,
  onUpload,
  onSelect,
  onDelete,
}) {
  const selectedId = getDocumentId(selectedDocument);

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">R</div>
        <span>ResearchAI</span>
      </div>

      <label className="upload-button">
        <span>{uploading ? "Processing PDF..." : "+ Upload PDF"}</span>
        <input
          type="file"
          accept=".pdf,application/pdf"
          onChange={onUpload}
          disabled={uploading}
          hidden
        />
      </label>

      <div className="sidebar-section">
        <p className="section-title">YOUR LIBRARY</p>
        {loading ? (
          <div className="empty-library" role="status">
            <span className="spinner" />
            <p>Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="empty-library">
            <span>▱</span>
            <p>No documents yet</p>
            <small>Upload a PDF to get started</small>
          </div>
        ) : (
          <div className="document-list">
            {documents.map((document) => {
              const id = getDocumentId(document);
              return (
                <div
                  className={`document-item ${id === selectedId ? "selected" : ""}`}
                  key={id}
                >
                  <button
                    className="document-select"
                    type="button"
                    onClick={() => onSelect(document)}
                    aria-pressed={id === selectedId}
                  >
                    <span className="document-icon">▤</span>
                    <span className="document-info">
                      <strong>{getDocumentName(document)}</strong>
                      <small>{document.total_pages || 0} pages</small>
                    </span>
                  </button>
                  <button
                    className="delete-button"
                    type="button"
                    onClick={() => onDelete(document)}
                    disabled={deletingId === id}
                    aria-label={`Delete ${getDocumentName(document)}`}
                    title="Delete document"
                  >
                    {deletingId === id ? "…" : "×"}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <div className="avatar">A</div>
        <div>
          <strong>Akshay</strong>
          <small>Personal workspace</small>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
