import React, { useState, useRef, useEffect } from 'react';
import { Cpu, CheckCircle, Activity } from 'lucide-react';

interface TerminalRow {
  type: 'input' | 'output' | 'system' | 'log' | 'success' | 'sub-tool' | 'sub-done';
  content: string | React.ReactNode;
}

export const TerminalSimulator: React.FC = () => {
  const [history, setHistory] = useState<TerminalRow[]>([
    { type: 'system', content: 'n8n CLI Agent Shell [v1.0.0]' },
    { type: 'system', content: 'Powered by Google ADK & NVIDIA NIM (LiteLLM)' },
    { type: 'system', content: 'Connected to local n8n instance at http://localhost:5678' },
    { type: 'system', content: 'Type /help to list available commands, or prompt your automation goals.' },
    { type: 'output', content: '' }
  ]);
  const [inputVal, setInputVal] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const terminalEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const focusInput = () => {
    inputRef.current?.focus();
  };

  const handleCommandSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const command = inputVal.trim();
    if (!command) return;

    const newHistory = [...history, { type: 'input' as const, content: command }];
    setHistory(newHistory);
    setInputVal('');
    setIsProcessing(true);

    const response = await processCommand(command);
    
    if (response) {
      setHistory(prev => [...prev, ...response]);
    }
    setIsProcessing(false);
  };

  const processCommand = async (cmd: string): Promise<TerminalRow[]> => {
    const lowerCmd = cmd.toLowerCase().trim();
    const parts = lowerCmd.split(' ');
    const mainCommand = parts[0];

    await new Promise(resolve => setTimeout(resolve, 350));

    if (mainCommand === '/clear') {
      setHistory([]);
      return [];
    }

    if (mainCommand === '/help') {
      return [
        {
          type: 'output',
          content: (
            <div style={{ color: '#aaaaaa', marginTop: '4px' }}>
              <div style={{ color: '#dc2626', fontWeight: 700, marginBottom: '8px', fontFamily: 'var(--sans)' }}>
                AVAILABLE CLI AGENT COMMANDS
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '8px 16px', fontSize: '12.5px' }}>
                <span style={{ color: '#ffffff', fontWeight: 600 }}>/list</span>
                <span>List all workflows on n8n instance</span>
                
                <span style={{ color: '#ffffff', fontWeight: 600 }}>/get &lt;id&gt;</span>
                <span>Retrieve full JSON schema of a workflow</span>
                
                <span style={{ color: '#ffffff', fontWeight: 600 }}>/activate &lt;id&gt;</span>
                <span>Activate an inactive workflow on n8n</span>
                
                <span style={{ color: '#ffffff', fontWeight: 600 }}>/deactivate &lt;id&gt;</span>
                <span>Deactivate an active workflow</span>
                
                <span style={{ color: '#ffffff', fontWeight: 600 }}>/history</span>
                <span>View recent workflow execution logs</span>
                
                <span style={{ color: '#ffffff', fontWeight: 600 }}>/clear</span>
                <span>Clear console screen history</span>
              </div>
              <div style={{ marginTop: '12px', fontSize: '11px', color: '#666666', fontStyle: 'italic' }}>
                Or describe a goal: "Fetch sql data and remind team on Slack every morning"
              </div>
            </div>
          )
        }
      ];
    }

    if (mainCommand === '/list') {
      return [
        {
          type: 'output',
          content: (
            <div style={{ color: '#ffffff', marginTop: '4px' }}>
              <div style={{ color: '#dc2626', fontWeight: 700, marginBottom: '8px', fontFamily: 'var(--sans)' }}>
                N8N ACTIVE WORKFLOWS
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(220,38,38,0.2)', color: '#dc2626' }}>
                    <th style={{ padding: '6px 0' }}>ID</th>
                    <th>WORKFLOW NAME</th>
                    <th>STATUS</th>
                    <th style={{ textAlign: 'center' }}>NODES</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{ padding: '6px 0', color: '#aaaaaa' }}>1R79s3KvM</td>
                    <td style={{ fontWeight: 600 }}>Slack Daily Reminder</td>
                    <td style={{ color: '#22c55e' }}>● Active</td>
                    <td style={{ textAlign: 'center' }}>3</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '6px 0', color: '#aaaaaa' }}>9Wsk2Ko1S</td>
                    <td style={{ fontWeight: 600 }}>Database Sync Webhook</td>
                    <td style={{ color: '#ff4444' }}>○ Inactive</td>
                    <td style={{ textAlign: 'center' }}>4</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '6px 0', color: '#aaaaaa' }}>wKloP92Ld</td>
                    <td style={{ fontWeight: 600 }}>LLM Customer Support Agent</td>
                    <td style={{ color: '#22c55e' }}>● Active</td>
                    <td style={{ textAlign: 'center' }}>7</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )
        }
      ];
    }

    if (mainCommand === '/history') {
      return [
        {
          type: 'output',
          content: (
            <div style={{ color: '#ffffff', marginTop: '4px' }}>
              <div style={{ color: '#dc2626', fontWeight: 700, marginBottom: '8px', fontFamily: 'var(--sans)' }}>
                RECENT EXECUTIONS LOG
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(220,38,38,0.2)', color: '#dc2626' }}>
                    <th style={{ padding: '6px 0' }}>EXEC ID</th>
                    <th>WORKFLOW ID</th>
                    <th>STATUS</th>
                    <th style={{ textAlign: 'right' }}>DURATION</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{ padding: '6px 0', color: '#aaaaaa' }}>#901</td>
                    <td style={{ fontWeight: 600 }}>1R79s3KvM</td>
                    <td style={{ color: '#22c55e' }}>✔ Success</td>
                    <td style={{ textAlign: 'right', color: '#dc2626' }}>142ms</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '6px 0', color: '#aaaaaa' }}>#900</td>
                    <td style={{ fontWeight: 600 }}>wKloP92Ld</td>
                    <td style={{ color: '#22c55e' }}>✔ Success</td>
                    <td style={{ textAlign: 'right', color: '#dc2626' }}>1580ms</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '6px 0', color: '#aaaaaa' }}>#899</td>
                    <td style={{ fontWeight: 600 }}>9Wsk2Ko1S</td>
                    <td style={{ color: '#ff4444' }}>✘ Failed</td>
                    <td style={{ textAlign: 'right', color: '#dc2626' }}>24ms</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )
        }
      ];
    }

    if (mainCommand === '/get') {
      const id = parts[1] || '1R79s3KvM';
      return [
        {
          type: 'output',
          content: (
            <div style={{ color: '#ffffff', marginTop: '4px' }}>
              <span style={{ color: '#666666' }}>// Schema template: {id}</span>
              <pre style={{ fontSize: '11px', color: '#dc2626', background: 'rgba(0,0,0,0.4)', padding: '12px', borderRadius: '6px', border: '1px solid rgba(220,38,38,0.1)', marginTop: '6px', overflowX: 'auto' }}>
{`{
  "name": "Slack Daily Reminder",
  "active": true,
  "nodes": [
    {
      "parameters": { "rule": { "interval": [ { "field": "cronExpression", "value": "0 9 * * 1-5" } ] } },
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [ 250, 300 ],
      "name": "Schedule Trigger"
    },
    {
      "parameters": { "message": "Daily automation compiles successfully." },
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2,
      "position": [ 500, 300 ],
      "name": "Slack"
    }
  ]
}`}
              </pre>
            </div>
          )
        }
      ];
    }

    if (mainCommand === '/activate') {
      const id = parts[1] || '1R79s3KvM';
      return [
        { type: 'success', content: `✓ Workflow '${id}' activated successfully!` }
      ];
    }

    if (mainCommand === '/deactivate') {
      const id = parts[1] || '1R79s3KvM';
      return [
        { type: 'log', content: `✓ Workflow '${id}' deactivated successfully.` }
      ];
    }

    const simulatedLogs: TerminalRow[] = [];
    simulatedLogs.push({ type: 'log', content: '⚙ DELEGATE Spawning dedicated Developer Subagent...' });
    simulatedLogs.push({ type: 'sub-tool', content: '⚙ SUB-TOOL [n8n_developer] get_credentials()' });
    simulatedLogs.push({ type: 'sub-done', content: '✔ SUB-DONE Completed [get_credentials] -> [{"id": "slack-cred-id", "name": "Corporate Slack", "type": "slack"}]' });
    simulatedLogs.push({ type: 'sub-tool', content: '⚙ SUB-TOOL [n8n_developer] get_multiple_nodes_summary(node_names=["scheduleTrigger", "slack"])' });
    simulatedLogs.push({ type: 'sub-done', content: '✔ SUB-DONE Completed [get_multiple_nodes_summary] -> Resolving node parameters.' });
    simulatedLogs.push({ type: 'sub-tool', content: `⚙ SUB-TOOL [n8n_developer] create_workflow(name="Autonomous ${cmd.slice(0, 15)}...")` });
    simulatedLogs.push({ type: 'sub-done', content: '✔ SUB-DONE Completed [create_workflow] -> Workflow generated successfully!' });
    simulatedLogs.push({ type: 'success', content: '✓ Workflow successfully compiled and activated!' });

    simulatedLogs.push({
      type: 'output',
      content: (
        <div style={{ color: '#ffffff', borderLeft: '2px solid var(--accent-color)', paddingLeft: '12px', margin: '4px 0' }}>
          <div style={{ color: '#dc2626', fontWeight: 700, fontSize: '11px', textTransform: 'uppercase', marginBottom: '4px' }}>
            N8N AGENT RESPONSE
          </div>
          Successfully designed, compiled, and deployed your automation task: **"{cmd}"**!
          <br /><br />
          1. **Scheduler Trigger**: Configured `n8n-nodes-base.scheduleTrigger` at coordinate `[250, 300]`.
          2. **API Endpoint**: Wired `n8n-nodes-base.slack` action node using credentials **"Corporate Slack"** at coordinate `[500, 300]`.
          3. **Self-Healing Check**: Connection routing verified, diagnostic checks passed successfully.
        </div>
      )
    });

    await new Promise(resolve => setTimeout(resolve, 800));
    return simulatedLogs;
  };

  return (
    <div className="terminal-window" onClick={focusInput} style={{ cursor: 'text' }}>
      <div className="terminal-header">
        <div className="terminal-buttons">
          <div className="terminal-btn terminal-btn-close"></div>
          <div className="terminal-btn terminal-btn-minimize"></div>
          <div className="terminal-btn terminal-btn-maximize"></div>
        </div>
        <div className="terminal-title">n8n-agent CLI Shell</div>
        <div className="terminal-info">
          <Activity size={12} style={{ color: '#dc2626' }} />
          <span>ACTIVE</span>
        </div>
      </div>
      
      <div className="terminal-body">
        <div className="terminal-history">
          {history.map((row, idx) => {
            if (row.type === 'input') {
              return (
                <div key={idx} className="terminal-row-input">
                  <span className="terminal-prompt" style={{ color: '#dc2626' }}>n8n-agent ❯</span>
                  <span>{row.content}</span>
                </div>
              );
            }
            if (row.type === 'system') {
              return (
                <div key={idx} style={{ color: '#666666', fontSize: '11.5px' }}>
                  {row.content}
                </div>
              );
            }
            if (row.type === 'log') {
              return (
                <div key={idx} style={{ color: '#eab308', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
                  <Cpu size={12} style={{ color: '#dc2626' }} />
                  <span>{row.content}</span>
                </div>
              );
            }
            if (row.type === 'sub-tool') {
              return (
                <div key={idx} style={{ color: '#c084fc', paddingLeft: '16px', fontSize: '11.5px' }}>
                  {row.content}
                </div>
              );
            }
            if (row.type === 'sub-done') {
              return (
                <div key={idx} style={{ color: '#dc2626', paddingLeft: '16px', fontSize: '11.5px' }}>
                  {row.content}
                </div>
              );
            }
            if (row.type === 'success') {
              return (
                <div key={idx} style={{ color: '#22c55e', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12.5px', fontWeight: 600 }}>
                  <CheckCircle size={13} />
                  <span>{row.content}</span>
                </div>
              );
            }
            return (
              <div key={idx} style={{ padding: '2px 0' }}>
                {row.content}
              </div>
            );
          })}
        </div>

        {isProcessing && (
          <div style={{ color: '#666666', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
            <span style={{ color: '#dc2626', animation: 'cursor-blink 1s infinite' }}>■</span>
            <span>Compiling workflow spec...</span>
          </div>
        )}

        <form onSubmit={handleCommandSubmit} style={{ marginTop: 'auto' }}>
          <div className="terminal-row-input">
            <span className="terminal-prompt" style={{ color: '#dc2626' }}>n8n-agent ❯</span>
            <input
              ref={inputRef}
              type="text"
              className="terminal-caret-input"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              disabled={isProcessing}
              placeholder="Type /help or describe automation goal..."
              style={{ caretColor: '#dc2626' }}
            />
          </div>
        </form>
        <div ref={terminalEndRef} />
      </div>
    </div>
  );
};
