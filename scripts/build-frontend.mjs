import { cp, mkdir, readdir, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const allowedApps = new Set(['admin-web', 'customer-web', 'mobile']);
const appName = process.argv[2];
if (!allowedApps.has(appName)) {
  throw new Error(`Choose one of: ${[...allowedApps].join(', ')}`);
}

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const appRoot = path.join(repoRoot, 'apps', appName);
const outputRoot = path.join(appRoot, 'dist');
if (path.dirname(outputRoot) !== appRoot || path.basename(outputRoot) !== 'dist') {
  throw new Error('Refusing to clean an unexpected build output path');
}
await rm(outputRoot, { recursive: true, force: true });
await mkdir(outputRoot, { recursive: true });
await cp(path.join(appRoot, 'index.html'), path.join(outputRoot, 'index.html'));

for (const directory of ['src', 'public']) {
  const source = path.join(appRoot, directory);
  try {
    const entries = await readdir(source);
    if (directory === 'src' && entries.length) {
      await cp(source, path.join(outputRoot, directory), { recursive: true, force: true });
    } else if (directory === 'public') {
      for (const entry of entries) {
        await cp(path.join(source, entry), path.join(outputRoot, entry), { recursive: true, force: true });
      }
    }
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
}

console.log(`Static frontend copied to ${path.relative(repoRoot, outputRoot)}`);
