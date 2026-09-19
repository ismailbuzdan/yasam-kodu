/* Research adapter only: execute pinned external mapping/topology in temporary
 * files. No third-party implementation is vendored or installed. The common
 * PyHD astronomy input is explicit: this is NOT two independent full charts. */
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const { pathToFileURL } = require('node:url');
const root = path.resolve(__dirname, '../tests/fixtures');
const sha = data => crypto.createHash('sha256').update(data).digest('hex');
const freeCommit = 'a5cefd371efcec79811eadff157511c39c199c8b';
const wheelCommit = 'ea673ad2614b7968ddf1c93670b6cbf20ab26eed';

async function main() {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'yasam-hd-compare-'));
  const provenance = [];
  async function get(repo, commit, file, local) {
    const url = `https://raw.githubusercontent.com/${repo}/${commit}/${file}`;
    const response = await fetch(url, { signal: AbortSignal.timeout(30000) });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = Buffer.from(await response.arrayBuffer());
    provenance.push({url, retrieved_at: new Date().toISOString(), sha256: sha(data)});
    fs.writeFileSync(path.join(temp, local), data);
    return data.toString('utf8');
  }
  try {
    for (const [repo, commit, filename] of [
      ['adamblvck/free-human-design', freeCommit, 'free-LICENSE'],
      ['domalhambra/hd-chart-engine', wheelCommit, 'wheel-LICENSE']]) {
      if (!(await get(repo, commit, 'LICENSE', filename)).startsWith('MIT License'))
        throw new Error('Unexpected license');
    }
    await get('adamblvck/free-human-design', freeCommit, 'src/calc/mandala.js', 'mandala.cjs');
    await get('adamblvck/free-human-design', freeCommit, 'src/hd/bodygraph.js', 'bodygraph.cjs');
    await get('domalhambra/hd-chart-engine', wheelCommit, 'src/wheel.ts', 'wheel.ts');
    await get('domalhambra/hd-chart-engine', wheelCommit, 'src/activation.ts', 'activation.ts');
    await get('domalhambra/hd-chart-engine', wheelCommit, 'src/ephemeris/types.ts', 'types.ts');
    // The activation module imports ./wheel extensionlessly. Node's temporary
    // research adapter adds the extension only; arithmetic is unchanged.
    const activationPath = path.join(temp, 'activation.ts');
    fs.writeFileSync(activationPath, fs.readFileSync(activationPath, 'utf8')
      .replace("from './wheel'", "from './wheel.ts'").replace("from './ephemeris/types'", "from './types.ts'"));
    const mapping = require(path.join(temp, 'mandala.cjs'));
    const graph = require(path.join(temp, 'bodygraph.cjs'));
    const wheel = await import(pathToFileURL(activationPath).href);
    const inputBytes = fs.readFileSync(path.join(root, 'human_design_sources/pyhd.json'));
    const input = JSON.parse(inputBytes);
    const bodyNames = {north_node:'north_node', south_node:'south_node'};
    const cases = input.cases.map(row => {
      const activations = {};
      const disagreements = [];
      for (const side of ['personality', 'design']) {
        activations[side] = row[side].map(a => {
          const mapped = mapping.mapLongitudeDegrees(a.longitude);
          const alternate = wheel.longitudeToActivation(a.longitude);
          if (a.gate !== mapped.hexagram || a.line !== mapped.line || a.gate !== alternate.g || a.line !== alternate.l)
            disagreements.push({side, body:a.body, pyhd:[a.gate,a.line], free:[mapped.hexagram,mapped.line], wheel:[alternate.g,alternate.l]});
          return {body:bodyNames[a.body] || a.body, gate:mapped.hexagram, line:mapped.line};
        });
      }
      const result = graph.computeBodygraph(activations);
      return {case_id:row.case_id, activations, type:result.type, authority:result.authority,
        profile:result.profile, active_gates:result.activatedGates,
        defined_channels:result.definedChannels.map(c=>c.gates), defined_centers:result.definedCenters,
        upstream_definitionCount:result.definitionCount, activation_disagreements:disagreements};
    });
    // Deliberate structural probes, not person charts.
    const probes = [[20,34],[1,8,25,51],[25,51],[],[1,8,4,63],[1,8,13,33]].map(gates => {
      const r = graph.computeBodygraph({personality:gates.map(gate=>({body:'probe',gate,line:1})),design:[]});
      return {gates,type:r.type,authority:r.authority,upstream_definitionCount:r.definitionCount};
    });
    const boundaries = [302,302.000001,307.624999,307.625,302.9375,359.999999,0,30,90,180,270,360].map(longitude => {
      const f=mapping.mapLongitudeDegrees(longitude), w=wheel.longitudeToActivation(longitude);
      return {longitude,free:[f.hexagram,f.line],wheel:[w.g,w.l]};
    });
    const result = {status:'candidate_not_approved', source_files:provenance,
      astronomy_input_sha256:sha(inputBytes), independence:'Independent gate/graph implementations; SAME upstream PyHD longitudes and design moment. No second end-to-end astronomical calculation.',
      adapter:'Node 24 native TypeScript stripping; only local wheel/types import paths changed in temporary file.',
      structural:{gate_centers:graph.GATE_CENTER,channels:graph.CHANNELS.map(c=>c.gates)},
      cases, probes, boundaries};
    fs.writeFileSync(path.join(root,'human_design_sources/comparison.json'),JSON.stringify(result,null,2)+'\n');
    console.log(`Compared ${cases.length} candidates, ${boundaries.length} boundaries, ${probes.length} graph probes`);
  } finally {
    // Exact mkdtemp-owned directory only.
    fs.rmSync(temp,{recursive:true,force:true});
  }
}
main().catch(error=>{console.error(error.message);process.exitCode=1;});
