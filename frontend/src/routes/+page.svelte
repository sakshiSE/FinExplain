<script>
  let fileInput, filename = '', question = '', messages = [], loading = false, error = '';
  let showOverviewModal = false;

  function toggleOverview() {
    showOverviewModal = !showOverviewModal;
  }

  async function upload(e) {
    const file = e.target.files[0];
    if (!file) return;
    loading = true; error = '';
    const fd = new FormData(); fd.append('file', file);
    try {
      const res = await fetch('http://127.0.0.1:8000/upload', { method: 'POST', body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');
      filename = data.filename; 
      messages = [];
    } catch (err) { error = err.message; }
    finally { loading = false; }
  }

  async function ask() {
    if (!question || !filename) return;
    const q = question; question = ''; loading = true; error = '';
    messages = [...messages, { role: 'user', text: q }];
    try {
      const res = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ question: q })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to fetch answer');
      
      messages = [...messages, { 
        role: 'bot', 
        text: data.answer || 'No answer generated.', 
        pages: data.pages || [], 
        calc: data.calculation 
      }];
    } catch (err) { 
      error = err.message;
      messages = [...messages, { role: 'bot', text: 'Error connecting to backend server.' }];
    }
    finally { loading = false; }
  }
</script>

<div class="main-wrapper">
  <!-- Top Navigation Bar -->
  <nav class="navbar">
    <div class="logo">
      <span class="logo-badge">F</span>
      <span class="brand-name">FinExplain AI</span>
    </div>
    <div class="nav-links">
      <button class="nav-btn" on:click={toggleOverview}>Overview</button>
      <button class="project-badge">MSc AI Project</button>
    </div>
  </nav>

  <!-- Overview Popup Modal -->
  {#if showOverviewModal}
    <div class="modal-backdrop" on:click={toggleOverview}>
      <div class="modal-card" on:click|stopPropagation>
        <div class="modal-header">
          <h3>📊 What is FinExplain?</h3>
          <button class="close-btn" on:click={toggleOverview}>✕</button>
        </div>
        <div class="modal-body">
          <p><strong>FinExplain</strong> is an AI-powered financial report assistant designed to simplify complex company annual reports and financial statements for non-specialists.</p>
          
          <div class="feature-list">
            <div class="feature-item">
              <span class="f-icon">🔍</span>
              <div>
                <strong>Grounded QA:</strong> Extracts specific passages directly from uploaded PDF reports and cites exact source page numbers.
              </div>
            </div>
            <div class="feature-item">
              <span class="f-icon">🧮</span>
              <div>
                <strong>Deterministic Math Engine:</strong> Evaluates percentage growth, profit margins, and net differences using Python to prevent AI arithmetic hallucinations.
              </div>
            </div>
            <div class="feature-item">
              <span class="f-icon">⚡</span>
              <div>
                <strong>QLoRA Fine-Tuned Model:</strong> Fine-tuned on financial reasoning datasets (FinQA) for domain-specific language understanding.
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-close-action" on:click={toggleOverview}>Got it!</button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Hero Section -->
  <section class="hero-container">
    <div class="hero-text">
      <h1>Simplifying Your Financial Report Analysis</h1>
      <p>Upload annual reports, analyze revenue metrics, verify statements, and perform zero-hallucination grounded QA with AI intelligence.</p>
      
      <div class="upload-box">
        <input type="file" accept=".pdf" bind:this={fileInput} on:change={upload} style="display:none;" />
        <button class="cta-btn" on:click={() => fileInput.click()} disabled={loading}>
          {loading ? 'Processing Document...' : 'UPLOAD REPORT PDF ➔'}
        </button>
        {#if filename}
          <div class="file-loaded">
            ✓ Loaded: <strong>{filename}</strong>
          </div>
        {/if}
      </div>
    </div>

    <!-- Hero Feature Card -->
    <div class="hero-card">
      <div class="card-inner">
        <div class="card-header">
          <span class="dot-green"></span> Grounded BM25 Search
        </div>
        <div class="card-metric">US $2.3B</div>
        <div class="card-sub">AI & Digital Services Revenue</div>
        <div class="card-chart">
          <div class="bar bar-1"></div>
          <div class="bar bar-2"></div>
          <div class="bar bar-3"></div>
          <div class="bar bar-4"></div>
        </div>
      </div>
    </div>
  </section>

  {#if error}
    <div class="error-toast">⚠️ {error}</div>
  {/if}

  <!-- Interactive Q&A Workspace -->
  <section class="workspace-section">
    <div class="workspace-card">
      <div class="workspace-header">
        <h3>💬 Financial Report Query Workspace</h3>
        <p>Ask about revenue, profits, debt ratios, or specific financial figures.</p>
      </div>

      <div class="chat-viewport">
        {#if messages.length === 0}
          <div class="empty-prompt">
            <div class="prompt-icon">📈</div>
            <h4>No Questions Asked Yet</h4>
            <p>Upload your report PDF above and enter a query below to retrieve verified financial passages.</p>
          </div>
        {/if}

        {#each messages as m}
          <div class="chat-row {m.role}">
            <div class="avatar">{m.role === 'user' ? 'YOU' : 'AI'}</div>
            <div class="chat-bubble">
              <div class="sender-name">{m.role === 'user' ? 'You' : 'FinExplain Assistant'}</div>
              <p>{m.text}</p>

              {#if m.calc}
                <div class="calc-panel">
                  <strong>⚡ Grounded Calculation:</strong>
                  <p>Formula: <code>{m.calc.formula}</code> = <span class="highlight">{m.calc.result}</span> (Diff: {m.calc.diff})</p>
                </div>
              {/if}

              {#if m.pages && m.pages.length > 0}
                <div class="source-pills">
                  <span>Source Citations:</span>
                  {#each m.pages as p}
                    <span class="pill">Page {p}</span>
                  {/each}
                </div>
              {/if}
            </div>
          </div>
        {/each}
      </div>

      <!-- Input Bar -->
      <div class="input-container">
        <input 
          type="text" 
          bind:value={question} 
          on:keydown={(e) => e.key === 'Enter' && ask()}
          placeholder={filename ? "Ask a question (e.g. 'What is the revenue?')..." : "Please upload a PDF report first..."} 
          disabled={!filename || loading}
        />
        <button on:click={ask} disabled={!filename || loading} class="send-action">
          SEND
        </button>
      </div>
    </div>
  </section>
</div>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

  :global(body) {
    margin: 0;
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
    background-color: #f7f9fc;
    color: #1e293b;
  }

  .main-wrapper {
    min-height: 100vh;
    padding-bottom: 4rem;
  }

  /* Navbar */
  .navbar {
    background: #0f2027;
    padding: 1.2rem 3rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: white;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }

  .logo-badge {
    background: #f2994a;
    color: white;
    font-weight: 800;
    padding: 0.3rem 0.7rem;
    border-radius: 8px;
    font-size: 1.1rem;
  }

  .brand-name {
    font-size: 1.2rem;
    font-weight: 700;
  }

  .nav-links {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .nav-btn {
    background: none;
    border: none;
    color: #cbd5e1;
    font-size: 0.95rem;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: color 0.2s ease;
  }

  .nav-btn:hover {
    color: #f2994a;
  }

  .project-badge {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
  }

  /* Modal Popup Design */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(15, 32, 39, 0.75);
    backdrop-filter: blur(6px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-card {
    background: white;
    width: 90%;
    max-width: 500px;
    border-radius: 20px;
    padding: 1.8rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.3);
    animation: fadeIn 0.2s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.8rem;
  }

  .modal-header h3 {
    margin: 0;
    color: #0f2027;
    font-size: 1.25rem;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 1.2rem;
    color: #94a3b8;
    cursor: pointer;
  }

  .modal-body {
    padding: 1.2rem 0;
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.6;
  }

  .feature-list {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
  }

  .feature-item {
    display: flex;
    gap: 0.8rem;
    align-items: flex-start;
    background: #f8fafc;
    padding: 0.75rem;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
  }

  .f-icon {
    font-size: 1.2rem;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    padding-top: 0.8rem;
    border-top: 1px solid #e2e8f0;
  }

  .modal-close-action {
    background: #0f2027;
    color: white;
    border: none;
    padding: 0.6rem 1.4rem;
    border-radius: 10px;
    font-weight: 700;
    cursor: pointer;
  }

  /* Hero Section */
  .hero-container {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    padding: 3.5rem 3rem 5rem 3rem;
    color: white;
    display: grid;
    grid-template-columns: 1.3fr 0.7fr;
    gap: 2rem;
    align-items: center;
  }

  .badge-tag {
    background: rgba(242, 153, 74, 0.2);
    color: #f2994a;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    letter-spacing: 0.05em;
  }

  .hero-text h1 {
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1.2;
    margin: 1rem 0;
  }

  .hero-text p {
    color: #94a3b8;
    font-size: 1.05rem;
    max-width: 550px;
    line-height: 1.6;
  }

  .upload-box {
    margin-top: 2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .cta-btn {
    background: #f2994a;
    color: white;
    font-weight: 800;
    border: none;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-size: 0.95rem;
    cursor: pointer;
    box-shadow: 0 10px 20px rgba(242, 153, 74, 0.3);
    transition: transform 0.2s ease;
  }

  .cta-btn:hover {
    transform: translateY(-2px);
  }

  .file-loaded {
    background: rgba(255, 255, 255, 0.1);
    padding: 0.6rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #4ade80;
  }

  /* Hero Feature Card */
  .hero-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2rem;
  }

  .card-inner {
    background: #ffffff;
    color: #1e293b;
    padding: 1.5rem;
    border-radius: 16px;
    box-shadow: 0 15px 30px rgba(0,0,0,0.2);
  }

  .card-header {
    font-size: 0.8rem;
    font-weight: 700;
    color: #64748b;
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }

  .dot-green {
    width: 8px;
    height: 8px;
    background: #22c55e;
    border-radius: 50%;
  }

  .card-metric {
    font-size: 2.2rem;
    font-weight: 800;
    color: #0f2027;
    margin-top: 0.5rem;
  }

  .card-sub {
    font-size: 0.85rem;
    color: #64748b;
  }

  .card-chart {
    display: flex;
    align-items: flex-end;
    gap: 0.5rem;
    height: 40px;
    margin-top: 1rem;
  }

  .bar {
    flex: 1;
    background: #f2994a;
    border-radius: 4px;
  }
  .bar-1 { height: 40%; }
  .bar-2 { height: 70%; }
  .bar-3 { height: 55%; }
  .bar-4 { height: 95%; }

  /* Workspace Section */
  .workspace-section {
    max-width: 1000px;
    margin: -2rem auto 0 auto;
    padding: 0 1.5rem;
  }

  .workspace-card {
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
    padding: 2rem;
  }

  .workspace-header h3 {
    margin: 0;
    font-size: 1.3rem;
    color: #0f2027;
  }

  .workspace-header p {
    margin: 0.3rem 0 1.5rem 0;
    color: #64748b;
    font-size: 0.9rem;
  }

  /* Chat Box */
  .chat-viewport {
    min-height: 280px;
    max-height: 420px;
    overflow-y: auto;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .empty-prompt {
    margin: auto;
    text-align: center;
    color: #94a3b8;
  }

  .prompt-icon {
    font-size: 2.5rem;
  }

  .chat-row {
    display: flex;
    gap: 0.8rem;
  }

  .chat-row.user {
    flex-direction: row-reverse;
  }

  .avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #0f2027;
    color: white;
    font-size: 0.7rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .chat-row.user .avatar {
    background: #f2994a;
  }

  .chat-bubble {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.8rem 1rem;
    max-width: 80%;
  }

  .chat-row.user .chat-bubble {
    background: #0f2027;
    color: white;
  }

  .sender-name {
    font-size: 0.7rem;
    font-weight: 700;
    color: #64748b;
    margin-bottom: 0.3rem;
  }

  .chat-row.user .sender-name {
    color: #f2994a;
  }

  .calc-panel {
    background: #fff7ed;
    border-left: 3px solid #f2994a;
    padding: 0.5rem;
    border-radius: 4px;
    margin-top: 0.5rem;
    font-size: 0.85rem;
    color: #1e293b;
  }

  .source-pills {
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: #64748b;
  }

  .pill {
    background: #e2e8f0;
    color: #0f2027;
    padding: 0.15rem 0.5rem;
    border-radius: 10px;
    font-weight: 600;
    margin-left: 0.3rem;
  }

  /* Input Bar */
  .input-container {
    display: flex;
    gap: 0.8rem;
    margin-top: 1.2rem;
  }

  input {
    flex: 1;
    padding: 0.9rem 1.2rem;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    font-size: 0.95rem;
  }

  .send-action {
    background: #0f2027;
    color: white;
    font-weight: 800;
    border: none;
    padding: 0 1.8rem;
    border-radius: 10px;
    cursor: pointer;
  }

  .error-toast {
    max-width: 1000px;
    margin: 1rem auto;
    background: #fee2e2;
    color: #991b1b;
    padding: 0.8rem 1.2rem;
    border-radius: 8px;
  }
</style>