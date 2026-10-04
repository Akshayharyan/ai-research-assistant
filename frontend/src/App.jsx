import { useEffect, useState } from "react";
import "./App.css";

function App() {
  // =====================================================
  // STATE
  // =====================================================

  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [loadingDocuments, setLoadingDocuments] = useState(true);

  const [selectedDocument, setSelectedDocument] = useState(null);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [asking, setAsking] = useState(false);

  const API_URL = "http://127.0.0.1:8000";


  // =====================================================
  // GET DOCUMENT ID
  // =====================================================

  const getDocumentId = (document) => {
    return (
      document.document_id ||
      document.id ||
      document._id
    );
  };


  // =====================================================
  // FETCH DOCUMENTS
  // =====================================================

  const fetchDocuments = async () => {
    try {
      setLoadingDocuments(true);

      const response = await fetch(
        `${API_URL}/documents`
      );

      if (!response.ok) {
        throw new Error(
          "Failed to fetch documents"
        );
      }

      const data = await response.json();

      console.log(
        "Documents:",
        data
      );

      setDocuments(
        data.documents || []
      );

    } catch (error) {

      console.error(
        "Error fetching documents:",
        error
      );

    } finally {

      setLoadingDocuments(false);

    }
  };


  // =====================================================
  // LOAD DOCUMENTS WHEN PAGE OPENS
  // =====================================================

  useEffect(() => {
    fetchDocuments();
  }, []);


  // =====================================================
  // UPLOAD PDF
  // =====================================================

  const handleUpload = async (event) => {

    const file =
      event.target.files[0];

    if (!file) {
      return;
    }


    // Validate PDF

    if (
      file.type !==
      "application/pdf"
    ) {

      alert(
        "Please select a PDF file."
      );

      event.target.value = "";

      return;
    }


    setUploading(true);


    const formData =
      new FormData();

    formData.append(
      "file",
      file
    );


    try {

      const response =
        await fetch(
          `${API_URL}/upload`,
          {
            method: "POST",
            body: formData,
          }
        );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Upload failed"
        );

      }


      console.log(
        "Upload response:",
        data
      );


      alert(
        "PDF uploaded successfully!"
      );


      // Refresh library

      await fetchDocuments();


    } catch (error) {

      console.error(
        "Upload error:",
        error
      );


      alert(
        `Upload failed: ${error.message}`
      );


    } finally {

      setUploading(false);

      event.target.value = "";

    }
  };


  // =====================================================
  // ASK AI
  // =====================================================

  const handleAsk = async () => {

    if (!selectedDocument) {

      alert(
        "Please select a document first."
      );

      return;
    }


    if (!question.trim()) {
      return;
    }


    setAsking(true);

    setAnswer("");

    setSources([]);


    try {

      const documentId =
        getDocumentId(
          selectedDocument
        );


      console.log(
        "Asking about document:",
        documentId
      );


      const response =
        await fetch(
          `${API_URL}/ask`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              question:
                question.trim(),

              document_id:
                documentId,

              top_k: 3,
            }),
          }
        );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to get answer"
        );

      }


      console.log(
        "AI response:",
        data
      );


      setAnswer(
        data.answer || ""
      );


      setSources(
        data.sources || []
      );


    } catch (error) {

      console.error(
        "Ask error:",
        error
      );


      alert(
        `Failed to get answer: ${error.message}`
      );


    } finally {

      setAsking(false);

    }
  };


  // =====================================================
  // ENTER KEY
  // =====================================================

  const handleKeyDown = (event) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      handleAsk();

    }
  };


  // =====================================================
  // SELECT DOCUMENT
  // =====================================================

  const handleSelectDocument = (
    document
  ) => {

    console.log(
      "Selected document:",
      document
    );


    setSelectedDocument(
      document
    );


    // Clear previous conversation

    setAnswer("");

    setSources("");

  };


  // =====================================================
  // UI
  // =====================================================

  return (
    <div className="app">


      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside className="sidebar">


        {/* BRAND */}

        <div className="brand">

          <div className="brand-icon">
            R
          </div>

          <span>
            ResearchAI
          </span>

        </div>


        {/* UPLOAD */}

        <label className="new-chat">

          {uploading
            ? "Uploading..."
            : "+ Upload PDF"
          }


          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleUpload}
            hidden
            disabled={uploading}
          />

        </label>


        {/* =================================================
            LIBRARY
        ================================================= */}

        <div className="sidebar-section">

          <p className="section-title">
            YOUR LIBRARY
          </p>


          {/* Loading */}

          {loadingDocuments ? (

            <div className="empty-library">

              <span>
                ⏳
              </span>

              <p>
                Loading documents...
              </p>

            </div>


          ) : documents.length === 0 ? (


            /* No documents */

            <div className="empty-library">

              <span>
                📄
              </span>

              <p>
                No documents yet
              </p>

              <small>
                Upload a PDF to get started
              </small>

            </div>


          ) : (


            /* Document list */

            <div className="document-list">

              {documents.map(
                (document, index) => {

                  const documentId =
                    getDocumentId(
                      document
                    );


                  const selectedId =
                    selectedDocument
                      ? getDocumentId(
                          selectedDocument
                        )
                      : null;


                  const isSelected =
                    documentId &&
                    selectedId &&
                    documentId ===
                      selectedId;


                  return (

                    <div
                      className={`document-item ${
                        isSelected
                          ? "selected"
                          : ""
                      }`}

                      key={
                        documentId ||
                        index
                      }

                      onClick={() =>
                        handleSelectDocument(
                          document
                        )
                      }
                    >


                      {/* Document icon */}

                      <span className="document-icon">
                        📄
                      </span>


                      {/* Document info */}

                      <div className="document-info">

                        <strong>

                          {document.filename ||
                            document.name ||
                            "Untitled PDF"}

                        </strong>


                        <small>
                          PDF
                        </small>

                      </div>

                    </div>

                  );

                }
              )}

            </div>

          )}

        </div>


        {/* =================================================
            USER
        ================================================= */}

        <div className="sidebar-footer">

          <div className="avatar">
            A
          </div>


          <div>

            <strong>
              Akshay
            </strong>

            <small>
              Personal workspace
            </small>

          </div>

        </div>

      </aside>


      {/* =================================================
          MAIN
      ================================================= */}

      <main className="main">


        {/* =================================================
            TOP BAR
        ================================================= */}

        <header className="topbar">

          <span>

            Workspace /{" "}

            <strong>

              {selectedDocument
                ? selectedDocument.filename ||
                  selectedDocument.name ||
                  "Selected document"
                : "New conversation"
              }

            </strong>

          </span>


          <span className="status">

            <span className="status-dot"></span>

            AI Assistant

          </span>

        </header>


        {/* =================================================
            WELCOME
        ================================================= */}

        {!answer &&
          !asking && (

            <section className="welcome">


              <div className="welcome-icon">
                ✳
              </div>


              <h1>

                Your research,{" "}

                <span>
                  simplified.
                </span>

              </h1>


              <p>

                Upload your documents,
                ask questions, and explore
                insights with answers
                grounded in your sources.

              </p>


              {/* Suggestions */}

              <div className="suggestions">


                <div className="suggestion">

                  <span>
                    ⌕
                  </span>

                  <div>

                    <strong>
                      Understand a document
                    </strong>

                    <small>
                      Summarize key ideas and arguments
                    </small>

                  </div>

                </div>


                <div className="suggestion">

                  <span>
                    ✧
                  </span>

                  <div>

                    <strong>
                      Find specific information
                    </strong>

                    <small>
                      Search across your research papers
                    </small>

                  </div>

                </div>


                <div className="suggestion">

                  <span>
                    ▤
                  </span>

                  <div>

                    <strong>
                      Explore your sources
                    </strong>

                    <small>
                      Get answers with supporting passages
                    </small>

                  </div>

                </div>


              </div>

            </section>

          )}


        {/* =================================================
            AI LOADING
        ================================================= */}

        {asking && (

          <section className="answer-section">


            <div className="answer-header">

              <span className="answer-icon">
                ✦
              </span>

              <strong>
                ResearchAI
              </strong>

            </div>


            <div className="answer-content">

              Thinking about your question...

            </div>

          </section>

        )}


        {/* =================================================
            AI ANSWER
        ================================================= */}

        {answer && (

          <section className="answer-section">


            {/* Answer header */}

            <div className="answer-header">

              <span className="answer-icon">
                ✦
              </span>

              <strong>
                ResearchAI
              </strong>

            </div>


            {/* Answer */}

            <div className="answer-content">

              {answer}

            </div>


            {/* =================================================
                SOURCES
            ================================================= */}

            {sources.length > 0 && (

              <div className="sources">

                <h3>
                  Sources
                </h3>


                {sources.map(
                  (source, index) => (

                    <div
                      className="source-card"
                      key={`${source.page}-${index}`}
                    >


                      <div className="source-header">

                        <span>
                          Page {source.page}
                        </span>


                        <span>

                          Score:{" "}

                          {typeof source.score ===
                            "number"
                            ? source.score.toFixed(
                                3
                              )
                            : "N/A"
                          }

                        </span>

                      </div>


                      <p>
                        {source.text}
                      </p>

                    </div>

                  )
                )}

              </div>

            )}

          </section>

        )}


        {/* =================================================
            CHAT
        ================================================= */}

        <div className="chat-area">


          <div className="chat-box">


            <textarea

              placeholder={
                selectedDocument
                  ? `Ask a question about ${
                      selectedDocument.filename ||
                      selectedDocument.name ||
                      "this document"
                    }...`
                  : "Select a document first..."
              }

              rows="1"

              value={question}

              onChange={(event) =>
                setQuestion(
                  event.target.value
                )
              }

              onKeyDown={
                handleKeyDown
              }

              disabled={
                !selectedDocument ||
                asking
              }

            />


            <div className="chat-actions">


              <span>

                {selectedDocument
                  ? "Answers are based on your selected document"
                  : "Select a document to start asking questions"
                }

              </span>


              <button

                onClick={
                  handleAsk
                }

                disabled={
                  !selectedDocument ||
                  !question.trim() ||
                  asking
                }

              >

                {asking
                  ? "..."
                  : "↑"
                }

              </button>


            </div>

          </div>


          <p className="disclaimer">

            AI can make mistakes.
            Verify important information
            with your sources.

          </p>


        </div>

      </main>

    </div>
  );
}

export default App;