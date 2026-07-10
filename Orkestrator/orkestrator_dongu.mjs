/*
 * orkestrator_dongu.mjs
 * Orkestrator'un surekli/otonom calisan sureci. mevcut OCR/MT5/Sync agent deseniyle ayni:
 * sonsuz dongu + sleep, Task Scheduler'a AtLogOn tetikleyicisiyle baglanir (bkz.
 * setup_orkestrator_task.ps1) - Session 0 izolasyonuna karsi guvenli (Interactive logon).
 *
 * Her dongude (2 dk):
 *   1. taraGorevDurumu() -- KOD TABANLI, hicbir LLM/API cagrisi yok
 *   2. Yeni tamamlanmis/hatali gorev bulunursa -> Orkestrator'un gercek query() cagrisi
 *      tetiklenir (Agent SDK, orkestrator_system_prompt.md) - o, sonraki adima kendi karar verir
 *   3. Bulunamazsa -> hicbir API cagrisi yapilmadan sessizce (sadece heartbeat log) tekrar uyur
 *
 * Kapsam: sadece Arastirmaci->Stratejist->Backtest Muhendisi->Risk Analisti pipeline
 * devamliligi. Gozetleme/Ekonomik Takvim/OCR-MT5 saglik izleme bu surecin disinda.
 */
import 'dotenv/config';
import { readFileSync } from 'node:fs';
import { appendFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { query } from '@anthropic-ai/claude-agent-sdk';
import {
  taraGorevDurumu,
  orkestratorAracSunucusu,
  gorevBasariylaTamamlandi,
  gorevDenemeBasarisizOldu,
} from './agent_cagir.mjs';

const REPO_ROOT = 'C:\\MilaYatirim\\mila-yatirim-sistemi';
const LOGLAR_DIR = 'C:\\MilaYatirim\\Orkestrator_Loglar';
const LOG_FILE = path.join(LOGLAR_DIR, 'orkestrator_log.txt');
const DONGU_ARALIGI_MS = 2 * 60 * 1000; // 2 dk - sync agent'la ayni
const MAX_TURNS = 20;

const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

function zamanDamgasi() {
  return new Date().toISOString().replace('T', ' ').slice(0, 19);
}

async function log(msg) {
  const satir = `[${zamanDamgasi()}] ${msg}`;
  console.log(satir);
  try {
    await mkdir(LOGLAR_DIR, { recursive: true });
    await appendFile(LOG_FILE, satir + '\n', 'utf-8');
  } catch (e) {
    console.error('Log yazma hatasi:', e.message);
  }
}

async function telegramBildir(msg) {
  if (!TELEGRAM_TOKEN || !TELEGRAM_CHAT_ID) return;
  try {
    const url = `https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`;
    const params = new URLSearchParams({ chat_id: TELEGRAM_CHAT_ID, text: msg });
    await fetch(`${url}?${params.toString()}`, { signal: AbortSignal.timeout(5000) });
  } catch (e) {
    await log(`Telegram gonderme hatasi (yok sayildi): ${e.message}`);
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function orkestratoruCagir(sonuclar) {
  const systemPrompt = readFileSync(path.join(REPO_ROOT, 'Agentlar', 'orkestrator_system_prompt.md'), 'utf-8');
  const userMessage = `Su gorev(ler) tamamlandi/hata verdi (agent_gorev_durumu_tara taramasi, ${zamanDamgasi()}):

${JSON.stringify(sonuclar, null, 2)}

Bu bilgiye dayanarak Yol1 pipeline'inin (Arastirmaci -> Stratejist -> Backtest Muhendisi -> Risk Analisti) bir sonraki adimina karar ver ve gerekiyorsa agent_cagir ile tetikle. Kararini ve gerekceni kisaca ozetle.`;

  let ozet = '';
  try {
    for await (const message of query({
      prompt: userMessage,
      options: {
        model: 'claude-sonnet-5',
        systemPrompt,
        cwd: REPO_ROOT,
        mcpServers: { 'orkestrator-araclari': orkestratorAracSunucusu },
        allowedTools: ['Read', 'Glob', 'Grep', 'Write', 'mcp__orkestrator-araclari__agent_cagir'],
        permissionMode: 'dontAsk',
        maxTurns: MAX_TURNS,
      },
    })) {
      if (message.type === 'assistant' && message.message?.content) {
        for (const block of message.message.content) {
          if (block.type === 'text') {
            await log(`[Orkestrator] ${block.text}`);
            ozet += block.text + '\n';
          } else if (block.type === 'tool_use') {
            await log(`[Orkestrator-TOOL] ${block.name} -> ${JSON.stringify(block.input).slice(0, 300)}`);
          }
        }
      } else if (message.type === 'result') {
        await log(`[Orkestrator] Oturum sonuc: ${message.subtype} | turns: ${message.num_turns}`);
      }
    }
  } catch (e) {
    await log(`HATA (Orkestrator cagrisi): ${e.message}`);
    return { basarili: false, hataMesaji: e.message };
  }

  await telegramBildir(
    `[Orkestrator] ${sonuclar.length} gorev basariyla islendi (${sonuclar.map((s) => s.gorev_id).join(', ')}).\n${ozet.slice(0, 500) || '(metin yaniti yok, sadece tool kullanimi)'}`
  );
  return { basarili: true };
}

async function dongu() {
  await log(`Orkestrator surekli/otonom sureci basladi (dongu araligi: ${DONGU_ARALIGI_MS / 1000}sn).`);
  await telegramBildir('[Orkestrator] Surekli/otonom surec baslatildi (Yol1 pipeline devamliligi izleniyor).');

  while (true) {
    try {
      const sonuclar = await taraGorevDurumu();
      if (sonuclar.length > 0) {
        await log(
          `${sonuclar.length} yeni tamamlanmis/hatali gorev bulundu: ${sonuclar.map((s) => s.gorev_id).join(', ')}`
        );
        const { basarili, hataMesaji } = await orkestratoruCagir(sonuclar);
        if (basarili) {
          for (const sonuc of sonuclar) {
            await gorevBasariylaTamamlandi(sonuc);
          }
          await log(`${sonuclar.length} gorev basariyla islendi, islenmis/ klasorune tasindi.`);
        } else {
          for (const sonuc of sonuclar) {
            const { tasindi, denemeSayisi } = await gorevDenemeBasarisizOldu(sonuc, hataMesaji);
            if (tasindi) {
              await log(`${sonuc.gorev_id}: ${denemeSayisi}. basarisiz denemeden sonra basarisiz/ klasorune tasindi.`);
              await telegramBildir(
                `[Orkestrator] ${sonuc.gorev_id}: ${denemeSayisi} kez denendi, basarisiz oldu, manuel incele. Son hata: ${(hataMesaji || '').slice(0, 200)}`
              );
            } else {
              await log(`${sonuc.gorev_id}: ${denemeSayisi}. deneme basarisiz, bir sonraki dongude tekrar denenecek.`);
            }
          }
        }
      } else {
        await log('Heartbeat: yeni gorev yok, API cagrisi yapilmadi.');
      }
    } catch (e) {
      await log(`HATA (dongu): ${e.message}`);
    }
    await sleep(DONGU_ARALIGI_MS);
  }
}

dongu();
