import { createReadStream } from 'node:fs';
import { access, stat } from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const allowedApps = new Set(['admin-web', 'customer-web', 'mobile']);
const appName = process.argv[2];
if (!allowedApps.has(appName)) {
  throw new Error(`Choose one of: ${[...allowedApps].join(', ')}`);
}

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const appRoot = path.join(repoRoot, 'apps', appName);
const serveDist = process.argv.includes('--dist');
const root = serveDist ? path.join(appRoot, 'dist') : appRoot;
if (serveDist) await access(path.join(root, 'index.html'));

const contentTypes = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

const server = http.createServer(async (request, response) => {
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    response.writeHead(405, { Allow: 'GET, HEAD' }).end();
    return;
  }
  try {
    const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const relativePath = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
    const filePath = path.resolve(root, relativePath);
    if (filePath !== root && !filePath.startsWith(root + path.sep)) {
      response.writeHead(400).end('Invalid path');
      return;
    }
    const info = await stat(filePath);
    if (!info.isFile()) {
      response.writeHead(404).end('Not found');
      return;
    }
    response.writeHead(200, {
      'Content-Type': contentTypes[path.extname(filePath)] || 'application/octet-stream',
      'Content-Length': info.size,
      'X-Content-Type-Options': 'nosniff',
    });
    if (request.method === 'HEAD') response.end();
    else createReadStream(filePath).pipe(response);
  } catch (error) {
    response.writeHead(error.code === 'ENOENT' ? 404 : 400).end('Not found');
  }
});

const port = Number(process.env.PORT || 5173);
server.listen(port, '127.0.0.1', () => {
  console.log(`${appName} ${serveDist ? 'preview' : 'dev server'} at http://127.0.0.1:${port}`);
});
