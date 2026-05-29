import React, { useState } from 'react';
import { Play, Copy, Check, Info, FileCode } from 'lucide-react';

export const WorkflowBuilder: React.FC = () => {
  const [workflowName, setWorkflowName] = useState('Production Automation Spec');
  const [goalDesc, setGoalDesc] = useState('Every Friday at 5pm, compile all SQL database records and dispatch a corporate Slack alert');
  const [isCompiling, setIsCompiling] = useState(false);
  const [copied, setCopied] = useState(false);
  const [compiledJSON, setCompiledJSON] = useState<string>(`{
  "name": "Production Automation Spec",
  "active": true,
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "value": "0 17 * * 5"
            }
          ]
        }
      },
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [ 250, 300 ],
      "name": "Every Friday 5pm"
    },
    {
      "parameters": {
        "operation": "getAll",
        "databaseId": "sql-invoice-db"
      },
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 4,
      "position": [ 500, 300 ],
      "name": "Fetch SQL Records",
      "credentials": {
        "postgres": {
          "id": "postgres-primary-cred",
          "name": "Corporate Postgres DB"
        }
      }
    },
    {
      "parameters": {
        "message": "⚠️ Status Report: All outstanding database records fetched successfully!"
      },
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2.1,
      "position": [ 750, 300 ],
      "name": "Slack Sender",
      "credentials": {
        "slackApi": {
          "id": "slack-primary-account",
          "name": "Workspace Slack"
        }
      }
    }
  ],
  "connections": {
    "Every Friday 5pm": {
      "main": [
        [
          {
            "node": "Fetch SQL Records",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Fetch SQL Records": {
      "main": [
        [
          {
            "node": "Slack Sender",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}`);

  const handleCompile = (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalDesc.trim()) return;

    setIsCompiling(true);

    setTimeout(() => {
      const generated = generateMockWorkflow(workflowName, goalDesc);
      setCompiledJSON(JSON.stringify(generated, null, 2));
      setIsCompiling(false);
    }, 1200);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(compiledJSON);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const generateMockWorkflow = (name: string, desc: string) => {
    const lowerDesc = desc.toLowerCase();
    const cleanName = name.trim() || 'Untitled Automation Spec';

    if (lowerDesc.includes('slack') && (lowerDesc.includes('database') || lowerDesc.includes('sql') || lowerDesc.includes('postgres'))) {
      return {
        name: cleanName,
        active: true,
        nodes: [
          {
            parameters: { rule: { interval: [{ field: 'cronExpression', value: '0 9 * * 1-5' }] } },
            type: 'n8n-nodes-base.scheduleTrigger',
            typeVersion: 1,
            position: [250, 300],
            name: 'Daily Schedule Trigger'
          },
          {
            parameters: { operation: 'getAll', databaseId: 'sql-production-db' },
            type: 'n8n-nodes-base.postgres',
            typeVersion: 4,
            position: [500, 300],
            name: 'Fetch SQL Records',
            credentials: { postgres: { id: 'postgres-primary-cred', name: 'Corporate Postgres DB' } }
          },
          {
            parameters: { message: `Automated Notification: Fetch successful!\nDetails: ={{ $json.records }}` },
            type: 'n8n-nodes-base.slack',
            typeVersion: 2.1,
            position: [750, 300],
            name: 'Slack Sender',
            credentials: { slackApi: { id: 'slack-primary-account', name: 'Workspace Slack' } }
          }
        ],
        connections: {
          'Daily Schedule Trigger': { main: [[{ node: 'Fetch SQL Records', type: 'main', index: 0 }]] },
          'Fetch SQL Records': { main: [[{ node: 'Slack Sender', type: 'main', index: 0 }]] }
        }
      };
    }

    if (lowerDesc.includes('webhook') || lowerDesc.includes('api') || lowerDesc.includes('http') || lowerDesc.includes('post')) {
      return {
        name: cleanName,
        active: true,
        nodes: [
          {
            parameters: { path: 'automation-hook', responseMode: 'onReceived' },
            type: 'n8n-nodes-base.webhook',
            typeVersion: 1.5,
            position: [250, 300],
            name: 'Production Webhook'
          },
          {
            parameters: { method: 'POST', url: 'https://api.corporate-service.com/v1/ingest', sendBody: true, bodyParameters: { data: '={{ $json.body }}' } },
            type: 'n8n-nodes-base.httpRequest',
            typeVersion: 4.1,
            position: [500, 300],
            name: 'API POST Target'
          }
        ],
        connections: {
          'Production Webhook': { main: [[{ node: 'API POST Target', type: 'main', index: 0 }]] }
        }
      };
    }

    return {
      name: cleanName,
      active: true,
      nodes: [
        {
          parameters: { rule: { interval: [{ field: 'hours', value: 1 }] } },
          type: 'n8n-nodes-base.scheduleTrigger',
          typeVersion: 1,
          position: [250, 300],
          name: 'Hourly Automation Check'
        },
        {
          parameters: { url: 'https://api.github.com/repos/AbhishekC1005/n8n-cli' },
          type: 'n8n-nodes-base.httpRequest',
          typeVersion: 4,
          position: [500, 300],
          name: 'Check Github Repo Status'
        }
      ],
      connections: {
        'Hourly Automation Check': { main: [[{ node: 'Check Github Repo Status', type: 'main', index: 0 }]] }
      }
    };
  };

  const syntaxHighlight = (json: string) => {
    if (!json) return '';
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g, (match) => {
      let cls = 'json-number';
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'json-key';
        } else {
          cls = 'json-string';
        }
      } else if (/true|false/.test(match)) {
        cls = 'json-boolean';
      }
      return `<span class="${cls}">${match}</span>`;
    });
  };

  return (
    <div className="compiler-layout" style={{ background: 'transparent' }}>
      {/* Input Form */}
      <form onSubmit={handleCompile} className="compiler-form card-green" style={{ background: '#111111', border: '1px solid rgba(220, 38, 38, 0.12)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px' }}>
          <FileCode size={20} style={{ color: '#dc2626' }} />
          <h3 style={{ fontSize: '18px', color: '#ffffff', fontFamily: 'var(--sans)' }}>n8n WORKFLOW SPEC COMPILER</h3>
        </div>
        
        <div className="form-group">
          <label className="form-label" style={{ color: '#aaaaaa' }}>Workflow Title</label>
          <input
            type="text"
            className="form-input-green"
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            disabled={isCompiling}
            placeholder="e.g. Daily SQL compiler"
          />
        </div>

        <div className="form-group">
          <label className="form-label" style={{ color: '#aaaaaa' }}>Describe your automation goal</label>
          <textarea
            className="form-input-green form-textarea-green"
            value={goalDesc}
            onChange={(e) => setGoalDesc(e.target.value)}
            disabled={isCompiling}
            placeholder="Describe triggers, timing, and integration details..."
          />
        </div>

        <div className="form-group" style={{ display: 'flex', gap: '8px', alignItems: 'center', background: '#070707', padding: '12px', borderRadius: '8px', border: '1px solid rgba(220, 38, 38, 0.05)' }}>
          <Info size={16} style={{ color: '#dc2626', flexShrink: 0 }} />
          <p style={{ fontSize: '11.5px', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
            The Google ADK engine maps inputs into structured nodes using active templates and parameters in real time.
          </p>
        </div>

        <button type="submit" disabled={isCompiling} className="compiler-submit-btn" style={{ marginTop: 'auto', background: '#dc2626', color: '#fff', fontWeight: 700, borderRadius: '8px', border: 'none' }}>
          {isCompiling ? (
            <div style={{ display: 'flex', alignItems: 'center', justifySelf: 'center', gap: '8px' }}>
              <div style={{ width: '12px', height: '12px', border: '2px solid transparent', borderTopColor: '#fff', borderRadius: '50%', animation: 'cursor-blink 0.5s infinite linear' }}></div>
              <span>COMPILING SPEC...</span>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifySelf: 'center', gap: '8px' }}>
              <Play size={12} fill="#fff" stroke="none" />
              <span>COMPILE n8n SPEC</span>
            </div>
          )}
        </button>
      </form>

      {/* Output preview */}
      <div className="compiler-preview card-green" style={{ background: '#111111', border: '1px solid rgba(220, 38, 38, 0.12)' }}>
        <div className="preview-header" style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
          <div className="preview-header-left">
            <div className="preview-dot" style={{ background: '#dc2626', boxShadow: '0 0 8px #dc2626' }}></div>
            <div className="preview-header-title" style={{ color: '#ffffff' }}>compiled_workflow.json</div>
          </div>
          <button type="button" onClick={handleCopy} className="preview-actions-btn" style={{ color: '#aaaaaa' }}>
            {copied ? (
              <>
                <Check size={13} style={{ color: '#dc2626' }} />
                <span style={{ color: '#dc2626' }}>COPIED!</span>
              </>
            ) : (
              <>
                <Copy size={13} />
                <span>COPY SPEC</span>
              </>
            )}
          </button>
        </div>

        <div 
          className="preview-body" 
          style={{ background: '#020202', borderBottomLeftRadius: '12px', borderBottomRightRadius: '12px' }}
          dangerouslySetInnerHTML={{ __html: syntaxHighlight(compiledJSON) }}
        />
      </div>
    </div>
  );
};
