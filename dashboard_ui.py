#!/usr/bin/env python3
"""
🚀 Qurrat-AI Dashboard UI
Real-time web interface for monitoring the AI Employee Vault
"""

import os
import subprocess
from datetime import datetime
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDERS = {
    'Needs_Action': '🚨 Needs Action',
    'Pending_Approval': '⏳ Pending Approval',
    'Approved': '✅ Approved',
    'Rejected': '❌ Rejected',
    'Plans': '📋 Plans',
    'Done': '✨ Done'
}

# --- HTML Template with Embedded CSS/JS ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Qurrat-AI Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-card: #1a1a25;
            --bg-card-hover: #222230;
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --accent-glow: rgba(99, 102, 241, 0.3);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --border: #2d2d3a;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Animated background gradient */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(ellipse at 20% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        /* Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 3rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border);
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logo {
            font-size: 2.5rem;
            animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .title h1 {
            font-size: 1.75rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-primary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .title p {
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }

        .timestamp {
            text-align: right;
        }

        .timestamp-label {
            color: var(--text-muted);
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .timestamp-value {
            color: var(--text-primary);
            font-size: 1rem;
            font-weight: 500;
            margin-top: 0.25rem;
        }

        .live-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: var(--bg-card);
            border-radius: 9999px;
            font-size: 0.75rem;
            color: var(--success);
            border: 1px solid var(--border);
        }

        .live-dot {
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }

        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            background: var(--bg-card-hover);
            border-color: var(--accent-primary);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 60px var(--accent-glow);
        }

        .stat-card:hover::before {
            opacity: 1;
        }

        .stat-icon {
            font-size: 2rem;
            margin-bottom: 0.75rem;
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        .stat-card.needs-action .stat-value { color: var(--danger); }
        .stat-card.pending .stat-value { color: var(--warning); }
        .stat-card.approved .stat-value { color: var(--success); }
        .stat-card.rejected .stat-value { color: var(--text-muted); }
        .stat-card.plans .stat-value { color: var(--accent-primary); }
        .stat-card.done .stat-value { color: var(--success); }

        /* Action Section */
        .action-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 3rem;
        }

        @media (max-width: 900px) {
            .action-section {
                grid-template-columns: 1fr;
            }
        }

        .panel {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }

        .panel-title {
            font-size: 1rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .file-count {
            background: var(--bg-primary);
            color: var(--text-secondary);
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .file-list {
            list-style: none;
            max-height: 300px;
            overflow-y: auto;
        }

        .file-list::-webkit-scrollbar {
            width: 6px;
        }

        .file-list::-webkit-scrollbar-track {
            background: var(--bg-primary);
            border-radius: 3px;
        }

        .file-list::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 3px;
        }

        .file-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem;
            border-radius: 8px;
            transition: all 0.2s ease;
            margin-bottom: 0.5rem;
        }

        .file-item:hover {
            background: var(--bg-primary);
            transform: translateX(4px);
        }

        .file-icon {
            font-size: 1.25rem;
        }

        .file-name {
            flex: 1;
            font-size: 0.875rem;
            color: var(--text-secondary);
            word-break: break-all;
        }

        .empty-state {
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
            font-size: 0.875rem;
        }

        /* CEO Briefing Button */
        .briefing-section {
            text-align: center;
            padding: 3rem;
            background: linear-gradient(135deg, var(--bg-card) 0%, rgba(99, 102, 241, 0.1) 100%);
            border: 1px solid var(--border);
            border-radius: 16px;
            margin-bottom: 2rem;
        }

        .briefing-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .briefing-subtitle {
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-bottom: 1.5rem;
        }

        .briefing-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem 2rem;
            background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px var(--accent-glow);
        }

        .briefing-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px var(--accent-glow);
        }

        .briefing-btn:active {
            transform: translateY(0);
        }

        .briefing-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .briefing-btn .spinner {
            display: none;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .briefing-btn.loading .spinner {
            display: block;
        }

        .briefing-btn.loading .btn-text {
            display: none;
        }

        /* Status Message */
        .status-message {
            margin-top: 1rem;
            padding: 1rem;
            border-radius: 8px;
            font-size: 0.875rem;
            display: none;
        }

        .status-message.success {
            display: block;
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
            border: 1px solid var(--success);
        }

        .status-message.error {
            display: block;
            background: rgba(239, 68, 68, 0.1);
            color: var(--danger);
            border: 1px solid var(--danger);
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
            font-size: 0.75rem;
            border-top: 1px solid var(--border);
        }

        .refresh-info {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }

            .header {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }

            .timestamp {
                text-align: center;
            }

            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .stat-value {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <div class="header-left">
                <span class="logo">🤖</span>
                <div class="title">
                    <h1>Qurrat-AI Dashboard</h1>
                    <p>Your Autonomous AI Employee Vault</p>
                </div>
            </div>
            <div class="timestamp">
                <div class="live-indicator">
                    <span class="live-dot"></span>
                    <span>LIVE</span>
                </div>
                <div class="timestamp-label">Last Updated</div>
                <div class="timestamp-value" id="lastUpdated">--</div>
            </div>
        </header>

        <!-- Stats Grid -->
        <div class="stats-grid" id="statsGrid">
            <!-- Populated by JavaScript -->
        </div>

        <!-- CEO Briefing Section -->
        <div class="briefing-section">
            <h2 class="briefing-title">📈 Generate CEO Briefing</h2>
            <p class="briefing-subtitle">Create an executive summary report with current stats and insights</p>
            <button class="briefing-btn" id="briefingBtn" onclick="generateBriefing()">
                <span class="btn-text">🚀 Generate Briefing</span>
                <span class="spinner"></span>
            </button>
            <div class="status-message" id="statusMessage"></div>
        </div>

        <!-- Action Panels -->
        <div class="action-section">
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">🚨 Needs Action</h3>
                    <span class="file-count" id="needsActionCount">0 files</span>
                </div>
                <ul class="file-list" id="needsActionList">
                    <li class="empty-state">Loading...</li>
                </ul>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">⏳ Pending Approval</h3>
                    <span class="file-count" id="pendingApprovalCount">0 files</span>
                </div>
                <ul class="file-list" id="pendingApprovalList">
                    <li class="empty-state">Loading...</li>
                </ul>
            </div>
        </div>

        <!-- Footer -->
        <footer class="footer">
            <p>Built with ❤️ for AI Employee Vault</p>
            <div class="refresh-info">
                <span>🔄 Auto-refreshing every 10 seconds</span>
            </div>
        </footer>
    </div>

    <script>
        const FOLDERS = {
            'Needs_Action': { icon: '🚨', label: 'Needs Action', class: 'needs-action' },
            'Pending_Approval': { icon: '⏳', label: 'Pending Approval', class: 'pending' },
            'Approved': { icon: '✅', label: 'Approved', class: 'approved' },
            'Rejected': { icon: '❌', label: 'Rejected', class: 'rejected' },
            'Plans': { icon: '📋', label: 'Plans', class: 'plans' },
            'Done': { icon: '✨', label: 'Done', class: 'done' }
        };

        function updateTimestamp() {
            const now = new Date();
            const options = { 
                weekday: 'short', 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            };
            document.getElementById('lastUpdated').textContent = now.toLocaleString('en-US', options);
        }

        function renderStats(stats) {
            const grid = document.getElementById('statsGrid');
            grid.innerHTML = '';

            for (const [folder, data] of Object.entries(FOLDERS)) {
                const count = stats[folder] || 0;
                const card = document.createElement('div');
                card.className = `stat-card ${data.class}`;
                card.innerHTML = `
                    <div class="stat-icon">${data.icon}</div>
                    <div class="stat-label">${data.label}</div>
                    <div class="stat-value">${count}</div>
                `;
                grid.appendChild(card);
            }
        }

        function renderFileList(folderId, files) {
            const list = document.getElementById(folderId + 'List');
            const count = document.getElementById(folderId + 'Count');
            
            count.textContent = `${files.length} file${files.length !== 1 ? 's' : ''}`;
            
            if (files.length === 0) {
                list.innerHTML = '<li class="empty-state">🎉 All clear! No files here.</li>';
                return;
            }

            list.innerHTML = files.map(file => `
                <li class="file-item">
                    <span class="file-icon">📄</span>
                    <span class="file-name">${file}</span>
                </li>
            `).join('');
        }

        async function fetchData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                renderStats(data.counts);
                renderFileList('needsAction', data.needs_action_files);
                renderFileList('pendingApproval', data.pending_approval_files);
                updateTimestamp();
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }

        async function generateBriefing() {
            const btn = document.getElementById('briefingBtn');
            const status = document.getElementById('statusMessage');
            
            btn.classList.add('loading');
            btn.disabled = true;
            status.className = 'status-message';
            status.textContent = '';

            try {
                const response = await fetch('/api/generate_briefing', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    status.className = 'status-message success';
                    status.textContent = `✅ ${result.message}`;
                    fetchData(); // Refresh data
                } else {
                    status.className = 'status-message error';
                    status.textContent = `❌ ${result.error}`;
                }
            } catch (error) {
                status.className = 'status-message error';
                status.textContent = `❌ Error: ${error.message}`;
            } finally {
                btn.classList.remove('loading');
                btn.disabled = false;
            }
        }

        // Initial load
        fetchData();

        // Auto-refresh every 10 seconds
        setInterval(fetchData, 10000);
    </script>
</body>
</html>
"""

# --- Helper Functions ---

def get_file_count(folder_name):
    """Get count of .md files in a folder."""
    folder_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(folder_path):
        return 0
    return len([f for f in os.listdir(folder_path) if f.endswith('.md')])

def get_files_list(folder_name):
    """Get list of .md files in a folder."""
    folder_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(folder_path):
        return []
    return sorted([f for f in os.listdir(folder_path) if f.endswith('.md')])

def run_ceo_briefing():
    """Run the CEO briefing script."""
    try:
        script_path = os.path.join(BASE_DIR, 'ceo_briefing.py')
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=BASE_DIR
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Briefing generation timed out"
    except Exception as e:
        return False, str(e)

# --- Routes ---

@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def api_data():
    """API endpoint to get folder statistics and file lists."""
    counts = {}
    for folder in FOLDERS.keys():
        counts[folder] = get_file_count(folder)
    
    return jsonify({
        'counts': counts,
        'needs_action_files': get_files_list('Needs_Action'),
        'pending_approval_files': get_files_list('Pending_Approval'),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/generate_briefing', methods=['POST'])
def api_generate_briefing():
    """API endpoint to generate CEO briefing."""
    success, message = run_ceo_briefing()
    
    if success:
        return jsonify({
            'success': True,
            'message': message.replace('✅ CEO Briefing generated: ', 'Briefing saved: ')
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Qurrat-AI Dashboard...")
    print("📊 Access at: http://localhost:5000")
    print("⏸️  Press Ctrl+C to stop")
    print("-" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
