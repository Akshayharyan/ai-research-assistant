function WelcomeScreen({ hasDocuments }) {
  return (
    <section className="welcome">
      <div className="welcome-icon">✳</div>
      <p className="eyebrow">AI RESEARCH WORKSPACE</p>
      <h1>Your research, <span>simplified.</span></h1>
      <p>
        Upload your documents, ask focused questions, and explore insights
        grounded in the sources you have provided.
      </p>
      {!hasDocuments && (
        <div className="welcome-note">Upload your first PDF to begin.</div>
      )}
      <div className="suggestions">
        <div className="suggestion"><span>⌕</span><div><strong>Understand a document</strong><small>Summarize key ideas and arguments</small></div></div>
        <div className="suggestion"><span>✧</span><div><strong>Find specific information</strong><small>Ask about details in your research</small></div></div>
        <div className="suggestion"><span>▤</span><div><strong>Explore your sources</strong><small>Get answers with supporting passages</small></div></div>
      </div>
    </section>
  );
}

export default WelcomeScreen;
