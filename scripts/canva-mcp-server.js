#!/usr/bin/env node
/**
 * canva-mcp-server.js
 *
 * Local MCP server that binds this agent to Canva. Exposes Canva operations
 * as MCP tools so the agent can create designs, export assets, and interact
 * with Canva via its API (requires CANVA_API_KEY) or via browser automation.
 *
 * Transport: stdio (JSON-RPC), matching the pattern used by other local
 * MCP servers in opencode.jsonc (e.g. playwright, remotion).
 *
 * NOTE: Canva is a web application. Real API calls require a CANVA_API_KEY
 * (set in environment). Without a key, tools return guidance on what is
 * needed rather than making unauthenticated requests.
 */

const https = require('https');

const CANVA_API_BASE = 'https://api.canva.com/rest/v1';

// ---------------------------------------------------------------------------
// Minimal MCP stdio transport
// ---------------------------------------------------------------------------

let nextId = 1;
const pending = new Map();

function send(obj) {
  process.stdout.write(JSON.stringify(obj) + '\n');
}

function onMessage(obj) {
  if (obj.jsonrpc !== '2.0') return;

  if (obj.id !== undefined && pending.has(obj.id)) {
    const { resolve, reject } = pending.get(obj.id);
    pending.delete(obj.id);
    if (obj.error) reject(new Error(obj.error.message || 'MCP error'));
    else resolve(obj.result);
    return;
  }

  handleRequest(obj);
}

async function handleRequest(req) {
  const { method, params, id } = req;

  try {
    let result;

    switch (method) {
      case 'initialize':
        result = {
          protocolVersion: '2024-11-05',
          capabilities: { tools: {} },
          serverInfo: { name: 'canva-mcp', version: '1.0.0' },
        };
        break;

      case 'initialized':
        return;

      case 'tools/list':
        result = { tools: listTools() };
        break;

      case 'tools/call':
        result = await callTool(params.name, params.arguments || {});
        break;

      default:
        throw new Error(`Method not found: ${method}`);
    }

    if (id !== undefined) {
      send({ jsonrpc: '2.0', id, result });
    }
  } catch (err) {
    if (id !== undefined) {
      send({
        jsonrpc: '2.0',
        id,
        error: { code: -32603, message: err.message },
      });
    }
  }
}

// ---------------------------------------------------------------------------
// Stdio loop
// ---------------------------------------------------------------------------

let buffer = '';
process.stdin.on('data', (chunk) => {
  buffer += chunk.toString();
  let idx;
  while ((idx = buffer.indexOf('\n')) !== -1) {
    const line = buffer.slice(0, idx);
    buffer = buffer.slice(idx + 1);
    if (line.trim()) {
      try {
        onMessage(JSON.parse(line));
      } catch (_) {
        // ignore malformed lines
      }
    }
  }
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function hasApiKey() {
  return Boolean(process.env.CANVA_API_KEY);
}

function canvaRequest(method, path, body) {
  return new Promise((resolve, reject) => {
    if (!hasApiKey()) {
      reject(
        new Error(
          'CANVA_API_KEY is not set. Set it in your environment and restart the MCP server to make live Canva API calls.'
        )
      );
      return;
    }

    const url = new URL(path, CANVA_API_BASE);
    const data = body ? JSON.stringify(body) : null;

    const req = https.request(
      url,
      {
        method,
        headers: {
          Authorization: `Bearer ${process.env.CANVA_API_KEY}`,
          'Content-Type': 'application/json',
          'Content-Length': data ? Buffer.byteLength(data) : 0,
        },
      },
      (res) => {
        let raw = '';
        res.on('data', (d) => (raw += d));
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            try {
              resolve(raw ? JSON.parse(raw) : {});
            } catch (_) {
              resolve({ raw });
            }
          } else {
            reject(
              new Error(
                `Canva API returned ${res.statusCode}: ${raw || res.statusMessage}`
              )
            );
          }
        });
      }
    );

    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

// ---------------------------------------------------------------------------
// Tool registry
// ---------------------------------------------------------------------------

function listTools() {
  return [
    {
      name: 'canva_info',
      description: 'Check Canva connection status and API key availability.',
      inputSchema: {
        type: 'object',
        properties: {},
        additionalProperties: false,
      },
    },
    {
      name: 'canva_designs_list',
      description: 'List your Canva designs (requires CANVA_API_KEY).',
      inputSchema: {
        type: 'object',
        properties: {
          page: { type: 'number', description: 'Page number', default: 1 },
          per_page: { type: 'number', description: 'Items per page', default: 10 },
        },
        additionalProperties: false,
      },
    },
    {
      name: 'canva_design_get',
      description: 'Get details of a specific Canva design (requires CANVA_API_KEY).',
      inputSchema: {
        type: 'object',
        properties: {
          designId: { type: 'string', description: 'Canva design ID' },
        },
        required: ['designId'],
        additionalProperties: false,
      },
    },
    {
      name: 'canva_design_export',
      description: 'Export a Canva design to an image/video format (requires CANVA_API_KEY).',
      inputSchema: {
        type: 'object',
        properties: {
          designId: { type: 'string', description: 'Canva design ID' },
          format: {
            type: 'string',
            enum: ['png', 'jpg', 'pdf', 'mp4', 'gif'],
            description: 'Export format',
            default: 'png',
          },
        },
        required: ['designId'],
        additionalProperties: false,
      },
    },
    {
      name: 'canva_exec',
      description:
        'Run an arbitrary Canva API request (requires CANVA_API_KEY).',
      inputSchema: {
        type: 'object',
        properties: {
          method: {
            type: 'string',
            enum: ['GET', 'POST', 'PUT', 'DELETE'],
            description: 'HTTP method',
          },
          path: {
            type: 'string',
            description: 'API path (e.g. /designs or /designs/{id}/exports)',
          },
          body: {
            type: 'object',
            description: 'Request body (for POST/PUT)',
          },
        },
        required: ['method', 'path'],
        additionalProperties: false,
      },
    },
  ];
}

// ---------------------------------------------------------------------------
// Tool implementations
// ---------------------------------------------------------------------------

const callTool = async (name, args) => {
  switch (name) {
    case 'canva_info': {
      return {
        provider: 'Canva',
        baseUrl: CANVA_API_BASE,
        apiKeyConfigured: hasApiKey(),
        message: hasApiKey()
          ? 'Canva API key is configured. Live calls are available.'
          : 'No CANVA_API_KEY set. Set it in your environment to enable live Canva API calls.',
      };
    }

    case 'canva_designs_list': {
      const { page = 1, per_page = 10 } = args;
      const data = await canvaRequest(
        'GET',
        `/designs?page=${page}&per_page=${per_page}`
      );
      return { ok: true, designs: data };
    }

    case 'canva_design_get': {
      const { designId } = args;
      const data = await canvaRequest('GET', `/designs/${encodeURIComponent(designId)}`);
      return { ok: true, design: data };
    }

    case 'canva_design_export': {
      const { designId, format = 'png' } = args;
      const data = await canvaRequest('POST', `/designs/${encodeURIComponent(designId)}/exports`, {
        format,
      });
      return { ok: true, export: data };
    }

    case 'canva_exec': {
      const { method, path, body } = args;
      const data = await canvaRequest(method, path, body);
      return { ok: true, result: data };
    }

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
};
