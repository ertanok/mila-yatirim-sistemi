/*
 * agent_calistir_worker.mjs
 * agent_cagir.mjs tarafindan `spawn` ile baslatilan bagimsiz Node sureci.
 * Kullanim: node agent_calistir_worker.mjs <agent_adi> <gorev_dosyasi_yolu> <gorev_id>
 *
 * Sistem promptunu okur, gorev dosyasini ilk mesaj olarak kullanip query() cagirir,
 * Write tool cagrilarindan rapor yolunu tespit eder, agent_gorev_durumu/{gorev_id}.json'a
 * durum yazar. Hicbir durumda (basari/hata) durum dosyasi yazilmadan sonlanmaz.
 */
import 'dotenv/config';
import { readFileSync, existsSync } from 'node:fs';
import { writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { query } from '@anthropic-ai/claude-agent-sdk';

const [, , agentAdi, gorevDosyasiYolu, gorevId] = process.argv;

const REPO_ROOT = 'C:\\MilaYatirim\\mila-yatirim-sistemi';
const AGENTLAR_DIR = path.join(REPO_ROOT, 'Agentlar');
const GOREV_DURUMU_DIR = path.join(REPO_ROOT, 'Orkestrator', 'agent_gorev_durumu');

async function durumYaz(durum, raporYolu) {
  await mkdir(GOREV_DURUMU_DIR, { recursive: true });
  const icerik = {
    durum,
    rapor_yolu: raporYolu,
    tamamlanma_zamani: new Date().toISOString(),
  };
  await writeFile(path.join(GOREV_DURUMU_DIR, `${gorevId}.json`), JSON.stringify(icerik, null, 2), 'utf-8');
}

async function main() {
  if (!agentAdi || !gorevDosyasiYolu || !gorevId) {
    console.error('Kullanim: node agent_calistir_worker.mjs <agent_adi> <gorev_dosyasi_yolu> <gorev_id>');
    process.exit(1);
  }

  const sistemPromptuYolu = path.join(AGENTLAR_DIR, `${agentAdi}_system_prompt.md`);
  if (!existsSync(sistemPromptuYolu) || !existsSync(gorevDosyasiYolu)) {
    await durumYaz('hata', null);
    process.exit(1);
  }

  const systemPrompt = readFileSync(sistemPromptuYolu, 'utf-8');
  const gorevMesaji = readFileSync(gorevDosyasiYolu, 'utf-8');

  let sonRaporYolu = null;
  let basariliSonuc = false;

  try {
    for await (const message of query({
      prompt: gorevMesaji,
      options: {
        model: 'claude-sonnet-5',
        systemPrompt,
        cwd: REPO_ROOT,
        allowedTools: ['Bash', 'Read', 'Write', 'Glob', 'Grep'],
        permissionMode: 'dontAsk',
        maxTurns: 30,
      },
    })) {
      if (message.type === 'assistant' && message.message?.content) {
        for (const block of message.message.content) {
          if (block.type === 'tool_use' && block.name === 'Write' && block.input?.file_path) {
            sonRaporYolu = block.input.file_path;
          }
        }
      } else if (message.type === 'result') {
        basariliSonuc = message.subtype === 'success';
      }
    }
  } catch (e) {
    await durumYaz('hata', sonRaporYolu);
    process.exit(1);
  }

  await durumYaz(basariliSonuc && sonRaporYolu ? 'tamamlandi' : 'hata', sonRaporYolu);
}

main();
