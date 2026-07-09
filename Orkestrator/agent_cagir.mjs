import { spawn } from 'node:child_process';
import { readdir, rename, mkdir, readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { tool, createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

const REPO_ROOT = 'C:\\MilaYatirim\\mila-yatirim-sistemi';
const AGENTLAR_DIR = path.join(REPO_ROOT, 'Agentlar');
const ORK_DIR = path.join(REPO_ROOT, 'Orkestrator');
const GOREV_DURUMU_DIR = path.join(ORK_DIR, 'agent_gorev_durumu');
const ISLENMIS_DIR = path.join(GOREV_DURUMU_DIR, 'islenmis');
const WORKER_SCRIPT = path.join(ORK_DIR, 'agent_calistir_worker.mjs');

const ES_ZAMANLI_SINIR = 2;

let acikCagriSayisi = 0;
const bekleyenKuyruk = []; // { agentAdi, gorevDosyasiYolu, gorevId }

function gorevIdUret(agentAdi) {
  const simdi = new Date();
  const iki = (n) => String(n).padStart(2, '0');
  const damga = `${simdi.getFullYear()}${iki(simdi.getMonth() + 1)}${iki(simdi.getDate())}_${iki(simdi.getHours())}${iki(simdi.getMinutes())}`;
  return `${agentAdi}_${damga}`;
}

function workerBaslat(agentAdi, gorevDosyasiYolu, gorevId) {
  acikCagriSayisi++;
  const child = spawn(process.execPath, [WORKER_SCRIPT, agentAdi, gorevDosyasiYolu, gorevId], {
    cwd: ORK_DIR,
    stdio: 'ignore',
  });
  const biti = () => {
    acikCagriSayisi--;
    kuyruguIsle();
  };
  child.on('exit', biti);
  child.on('error', biti);
}

function kuyruguIsle() {
  if (acikCagriSayisi < ES_ZAMANLI_SINIR && bekleyenKuyruk.length > 0) {
    const sonraki = bekleyenKuyruk.shift();
    workerBaslat(sonraki.agentAdi, sonraki.gorevDosyasiYolu, sonraki.gorevId);
  }
}

export const agentCagirTool = tool(
  'agent_cagir',
  "Bir agent'i (orn. arastirmaci, stratejici) ayri, bagimsiz bir Node surecinde baslatir. " +
    'Non-blocking: hemen bir gorev_id doner, agent isini bitirene kadar beklemez. ' +
    `Ayni anda en fazla ${ES_ZAMANLI_SINIR} agent calisir; fazlasi kuyruga alinir ve sira geldiginde otomatik baslar. ` +
    'Agent isini bitirdiginde agent_gorev_durumu/{gorev_id}.json dosyasina durum yazar ' +
    '(bu dosyalari agent_gorev_durumu_tara tool ile kontrol et).',
  {
    agent_adi: z
      .string()
      .describe(
        "Agent'in dosya-adi kimligi (orn. 'arastirmaci', 'stratejici') - Agentlar/{agent_adi}_system_prompt.md ile eslesmeli"
      ),
    gorev_dosyasi_yolu: z
      .string()
      .describe('orkestrator_cagri_sablonu.md formatinda doldurulmus gorev dosyasinin tam yolu'),
  },
  async ({ agent_adi, gorev_dosyasi_yolu }) => {
    if (!existsSync(gorev_dosyasi_yolu)) {
      return {
        content: [{ type: 'text', text: `HATA: gorev dosyasi bulunamadi: ${gorev_dosyasi_yolu}` }],
        isError: true,
      };
    }
    const sistemPromptuYolu = path.join(AGENTLAR_DIR, `${agent_adi}_system_prompt.md`);
    if (!existsSync(sistemPromptuYolu)) {
      return {
        content: [{ type: 'text', text: `HATA: sistem promptu bulunamadi: ${sistemPromptuYolu}` }],
        isError: true,
      };
    }

    const gorevId = gorevIdUret(agent_adi);
    await mkdir(GOREV_DURUMU_DIR, { recursive: true });

    if (acikCagriSayisi < ES_ZAMANLI_SINIR) {
      workerBaslat(agent_adi, gorev_dosyasi_yolu, gorevId);
      return {
        content: [
          {
            type: 'text',
            text: `${agent_adi} baslatildi (gorev_id: ${gorevId}). Durum icin agent_gorev_durumu_tara tool'unu kullan.`,
          },
        ],
      };
    }

    bekleyenKuyruk.push({ agentAdi: agent_adi, gorevDosyasiYolu: gorev_dosyasi_yolu, gorevId });
    return {
      content: [
        {
          type: 'text',
          text:
            `${agent_adi} kuyruga alindi (gorev_id: ${gorevId}) - su an ${acikCagriSayisi} agent calisiyor ` +
            `(sinir: ${ES_ZAMANLI_SINIR}). Sira geldiginde otomatik baslar.`,
        },
      ],
    };
  }
);

export const agentGorevDurumuTaraTool = tool(
  'agent_gorev_durumu_tara',
  "agent_gorev_durumu/ klasorunu tarar, 'tamamlandi' veya 'hata' durumundaki gorev dosyalarini bulur, " +
    'iceriklerini rapor olarak doner ve islenmis/ alt-klasorune tasir (bir sonraki taramada tekrar gelmesinler diye). ' +
    'Bunu her turda cagirip donen gorevler icin gerekirse Ertan a bilgi notu / sonraki adim degerlendirmesi yap.',
  {},
  async () => {
    await mkdir(GOREV_DURUMU_DIR, { recursive: true });
    await mkdir(ISLENMIS_DIR, { recursive: true });

    const tumDosyalar = await readdir(GOREV_DURUMU_DIR, { withFileTypes: true });
    const jsonDosyalari = tumDosyalar.filter((d) => d.isFile() && d.name.endsWith('.json')).map((d) => d.name);

    const sonuclar = [];
    for (const dosyaAdi of jsonDosyalari) {
      const tamYol = path.join(GOREV_DURUMU_DIR, dosyaAdi);
      let icerik;
      try {
        icerik = JSON.parse(await readFile(tamYol, 'utf-8'));
      } catch {
        continue; // bozuk/yaziliyor olabilecek dosyayi atla, sonraki taramada tekrar denenir
      }
      if (icerik.durum === 'tamamlandi' || icerik.durum === 'hata') {
        sonuclar.push({ gorev_id: dosyaAdi.replace(/\.json$/, ''), ...icerik });
        await rename(tamYol, path.join(ISLENMIS_DIR, dosyaAdi));
      }
    }

    return {
      content: [
        {
          type: 'text',
          text:
            sonuclar.length > 0
              ? `${sonuclar.length} tamamlanmis/hatali gorev bulundu:\n${JSON.stringify(sonuclar, null, 2)}`
              : 'Yeni tamamlanmis gorev yok.',
        },
      ],
    };
  }
);

export const orkestratorAracSunucusu = createSdkMcpServer({
  name: 'orkestrator-araclari',
  version: '1.0.0',
  tools: [agentCagirTool, agentGorevDurumuTaraTool],
});
