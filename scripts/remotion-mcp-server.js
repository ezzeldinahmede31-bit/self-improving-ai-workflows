#!/usr/bin/env node
/**
 * remotion-mcp-server.js
 *
 * Local MCP server that binds this agent to the Remotion project at
 * video-production/ai-automation-motion. Exposes Remotion operations as
 * MCP tools so the agent can render videos, start the studio, and inspect
 * compositions without leaving the OpenCode harness.
 *
 * Transport: stdio (JSON-RPC), matching the pattern used by other local
 * MCP servers in opencode.jsonc (e.g. playwright).
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const PROJECT_DIR = path.resolve(
  __dirname,
  '..',
  'video-production',
  'ai-automation-motion'
);

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

  // Response to a previous request
  if (obj.id !== undefined && pending.has(obj.id)) {
    const { resolve, reject } = pending.get(obj.id);
    pending.delete(obj.id);
    if (obj.error) reject(new Error(obj.error.message || 'MCP error'));
    else resolve(obj.result);
    return;
  }

  // Incoming request
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
          serverInfo: { name: 'remotion-mcp', version: '1.0.0' },
        };
        break;

      case 'initialized':
        // Notification, no response needed
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
// Tool registry
// ---------------------------------------------------------------------------

function listTools() {
  return [
    {
      name: 'remotion_info',
      description:
        'Get info about the Remotion project (compositions, duration, fps, dimensions).',
      inputSchema: {
        type: 'object',
        properties: {},
        additionalProperties: false,
      },
    },
    {
      name: 'remotion_render',
      description:
        'Render a Remotion composition to an MP4 video file.',
      inputSchema: {
        type: 'object',
        properties: {
          compositionId: {
            type: 'string',
            description:
              'ID of the composition to render (default: AIAutomationMotion)',
          },
          output: {
            type: 'string',
            description:
              'Output MP4 path (default: out/video.mp4 relative to project)',
          },
          codec: {
            type: 'string',
            description: 'Video codec (default: h264)',
          },
          frames: {
            type: 'number',
            description: 'Override frame count (optional)',
          },
        },
        additionalProperties: false,
      },
    },
    {
      name: 'remotion_studio',
      description: 'Start the Remotion Studio in the background.',
      inputSchema: {
        type: 'object',
        properties: {},
        additionalProperties: false,
      },
    },
    {
      name: 'remotion_scaffold',
      description:
        'Scaffold a new scene or component inside the Remotion project.',
      inputSchema: {
        type: 'object',
        properties: {
          type: {
            type: 'string',
            enum: ['scene', 'component'],
            description: 'What to scaffold',
          },
          name: {
            type: 'string',
            description: 'Name of the new file (e.g. Scene7)',
          },
        },
        required: ['type', 'name'],
        additionalProperties: false,
      },
    },
    {
      name: 'remotion_exec',
      description:
        'Run an arbitrary `npx remotion <command>` inside the project directory.',
      inputSchema: {
        type: 'object',
        properties: {
          command: {
            type: 'string',
            description: 'Remotion CLI command (e.g. "render", "studio")',
          },
          args: {
            type: 'array',
            items: { type: 'string' },
            description: 'Additional CLI arguments',
          },
        },
        required: ['command'],
        additionalProperties: false,
      },
    },
  ];
}

// ---------------------------------------------------------------------------
// Tool implementations
// ---------------------------------------------------------------------------

function runCmd(cmd, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, {
      cwd: PROJECT_DIR,
      stdio: ['ignore', 'pipe', 'pipe'],
      ...options,
    });

    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('close', (code) => {
      if (code === 0) resolve({ stdout, stderr, code });
      else
        reject(
          new Error(
            `Command "${cmd} ${args.join(' ')}" exited ${code}:\n${stderr ||
              stdout}`
          )
        );
    });
    child.on('error', reject);
  });
}

async callTool = async (name, args) => {
  switch (name) {
    case 'remotion_info': {
      const pkg = JSON.parse(
        fs.readFileSync(path.join(PROJECT_DIR, 'package.json'), 'utf8')
      );
      const tsconfig = JSON.parse(
        fs.readFileSync(path.join(PROJECT_DIR, 'tsconfig.json'), 'utf8')
      );
      const files = fs.readdirSync(path.join(PROJECT_DIR, 'src'));
      const scenes = fs
        .readdirSync(path.join(PROJECT_DIR, 'src/scenes'))
        .filter((f) => f.endsWith('.tsx'));

      return {
        projectDir: PROJECT_DIR,
        package: {
          name: pkg.name,
          version: pkg.version,
          description: pkg.description,
        },
        scripts: pkg.scripts,
        srcFiles: files,
        scenes,
        tsconfig,
      };
    }

    case 'remotion_render': {
      const {
        compositionId = 'AIAutomationMotion',
        output = 'out/video.mp4',
        codec = 'h264',
        frames,
      } = args;

      const outputPath = path.isAbsolute(output)
        ? output
        : path.join(PROJECT_DIR, output);

      const cliArgs = [
        'remotion',
        'render',
        compositionId,
        outputPath,
        '--codec',
        codec,
      ];
      if (frames) cliArgs.push('--frames', String(frames));

      const res = await runCmd('npx', cliArgs, {
        maxBuffer: 50 * 1024 * 1024,
      });

      return {
        ok: true,
        output: outputPath,
        stdout: res.stdout,
        stderr: res.stderr,
      };
    }

    case 'remotion_studio': {
      // Launch studio detached (background) so it doesn't block the MCP loop
      const child = spawn('npx', ['remotion', 'studio'], {
        cwd: PROJECT_DIR,
        stdio: 'ignore',
        detached: true,
      });
      child.unref();

      return {
        ok: true,
        message: 'Remotion Studio launched in background',
        pid: child.pid,
      };
    }

    case 'remotion_scaffold': {
      const { type, name } = args;
      const scenesDir = path.join(PROJECT_DIR, 'src/scenes');
      const componentsDir = path.join(PROJECT_DIR, 'src/components');

      if (type === 'scene') {
        const file = path.join(scenesDir, `${name}.tsx`);
        if (fs.existsSync(file)) {
          return { ok: false, message: `Scene ${name} already exists` };
        }
        fs.mkdirSync(scenesDir, { recursive: true });
        fs.writeFileSync(
          file,
          `import React from 'react';\nimport { interpolate } from 'remotion';\nimport { COLORS } from '../constants';\nimport { Typography } from '../components/Typography';\n\nexport const ${name}: React.FC = () => {\n  const frame = 0;\n  return (\n    <div style={{ position: 'absolute', inset: 0, background: COLORS.black }}>\n      <Typography size="title" color={COLORS.white} style={{ textAlign: 'center' }}>\n        {${JSON.stringify(name)}}\n      </Typography>\n    </div>\n  );\n};\n`
        );
        return { ok: true, file };
      }

      if (type === 'component') {
        const file = path.join(componentsDir, `${name}.tsx`);
        if (fs.existsSync(file)) {
          return { ok: false, message: `Component ${name} already exists` };
        }
        fs.mkdirSync(componentsDir, { recursive: true });
        fs.writeFileSync(
          file,
          `import React from 'react';\n\nexport const ${name}: React.FC<{ children?: React.ReactNode }> = ({ children }) => (\n  <div>{children}</div>\n);\n`
        );
        return { ok: true, file };
      }

      throw new Error(`Unknown scaffold type: ${type}`);
    }

    case 'remotion_exec': {
      const { command, args: extraArgs = [] } = args;
      const res = await runCmd('npx', ['remotion', command, ...extraArgs], {
        maxBuffer: 50 * 1024 * 1024,
      });
      return { ok: true, stdout: res.stdout, stderr: res.stderr };
    }

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
};
