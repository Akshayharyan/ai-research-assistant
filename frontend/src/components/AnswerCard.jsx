function AnswerCard({ answer, sources, asking }) {
  return (
    <section className="answer-section" aria-live="polite">
      <div className="answer-header">
        <span className="answer-icon">✦</span>
        <strong>ResearchAI</strong>
        {asking && <span className="thinking"><span /> Thinking</span>}
      </div>
      <div className="answer-content">
        {asking ? "Reading your document and preparing an answer..." : answer}
      </div>
      {!asking && sources.length > 0 && (
        <div className="sources">
          <div className="sources-heading">
            <h3>Sources</h3>
            <span>{sources.length} passages</span>
          </div>
          {sources.map((source, index) => (
            <article className="source-card" key={`${source.page}-${index}`}>
              <div className="source-header">
                <span>Source {String(index + 1).padStart(2, "0")}</span>
                <span>Page {source.page} · Relevance {typeof source.score === "number" ? source.score.toFixed(2) : "N/A"}</span>
              </div>
              <p>“{source.text}”</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default AnswerCard;
