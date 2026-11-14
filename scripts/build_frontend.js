const fs = require('fs');
const path = require('path');
const esbuild = require('../frontend/node_modules/esbuild');

const staticDir = path.join(__dirname, '..', 'backend', 'app', 'static');
const distDir = path.join(__dirname, '..', 'frontend', 'dist');
const indexPath = path.join(staticDir, 'index.html');
const srcJsxPath = path.join(__dirname, '..', 'frontend', 'src', 'App.standalone.jsx');

async function build() {
    console.log('--- Building Optimized Frontend Bundle ---');
    let jsxCode = '';

    if (fs.existsSync(srcJsxPath)) {
        jsxCode = fs.readFileSync(srcJsxPath, 'utf-8');
    } else {
        const html = fs.readFileSync(indexPath, 'utf-8');
        const scriptMatch = html.match(/<script type="text\/babel">([\s\S]*?)<\/script>/);
        if (scriptMatch) {
            jsxCode = scriptMatch[1];
            fs.writeFileSync(srcJsxPath, jsxCode, 'utf-8');
        }
    }

    if (!jsxCode) {
        console.log('Bundle already precompiled. Re-verifying existing bundle.');
        const bundlePath = path.join(staticDir, 'app.bundle.js');
        if (fs.existsSync(bundlePath)) {
            console.log(`✓ Bundle verified: ${bundlePath} (${fs.statSync(bundlePath).size} bytes)`);
            return;
        }
        console.error('No JSX source or bundle found.');
        return;
    }

    console.log(`Transpiling ${jsxCode.length} bytes of JSX via esbuild...`);
    const result = await esbuild.transform(jsxCode, {
        loader: 'jsx',
        minify: true,
        target: 'es2020',
        jsxFactory: 'React.createElement',
        jsxFragment: 'React.Fragment'
    });

    const bundlePath = path.join(staticDir, 'app.bundle.js');
    fs.writeFileSync(bundlePath, result.code, 'utf-8');
    console.log(`✓ Generated precompiled bundle: ${bundlePath} (${result.code.length} bytes)`);

    // Sync to frontend/dist
    if (!fs.existsSync(distDir)) {
        fs.mkdirSync(distDir, { recursive: true });
    }
    const html = fs.readFileSync(indexPath, 'utf-8');
    fs.writeFileSync(path.join(distDir, 'index.html'), html, 'utf-8');
    fs.writeFileSync(path.join(distDir, 'app.bundle.js'), result.code, 'utf-8');
    console.log(`✓ Synced to ${distDir}`);
}

build().catch(err => {
    console.error('Build error:', err);
    process.exit(1);
});
