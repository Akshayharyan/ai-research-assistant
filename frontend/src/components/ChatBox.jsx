import { getDocumentName } from "../services/api";

function ChatBox({ document, question, asking, onChange, onSubmit }) {
  const canSubmit = Boolean(document && question.trim() && !asking);

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSubmit();
    }
  }

  return (
    <div className="chat-area">
      <div className="chat-box">
        <textarea
          aria-label="Question"
          placeholder={document ? `Ask a question about ${getDocumentName(document)}...` : "Select a document first..."}
          rows="2"
          value={question}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          disabled={!document || asking}
        />
        <div className="chat-actions">
          <span>{document ? "Enter to send · Shift + Enter for a new line" : "Select a document to start asking questions"}</span>
          <button type="button" onClick={onSubmit} disabled={!canSubmit} aria-label="Send question">
            {asking ? <span className="button-spinner" /> : "↑"}
          </button>
        </div>
      </div>
      <p className="disclaimer">AI can make mistakes. Verify important information with your sources.</p>
    </div>
  );
}

export default ChatBox;
