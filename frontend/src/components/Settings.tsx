import { useState } from "react";

interface SettingsForm {
  twilioAccountSid: string;
  twilioAuthToken: string;
  stripeKey: string;
  claudeApiKey: string;
}

const STORAGE_KEY = "suportia_settings_draft";

function loadDraft(): SettingsForm {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    // ignora erros de parsing e usa o valor padrão
  }
  return { twilioAccountSid: "", twilioAuthToken: "", stripeKey: "", claudeApiKey: "" };
}

export default function Settings() {
  const [form, setForm] = useState<SettingsForm>(loadDraft);
  const [saved, setSaved] = useState(false);

  function update<K extends keyof SettingsForm>(key: K, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  }

  function handleSave() {
    // NOTA MVP: isto guarda apenas um rascunho local no navegador para facilitar
    // o preenchimento do .env. As chaves reais devem ser configuradas como
    // variáveis de ambiente no backend (Railway) e nunca ficar expostas no frontend.
    localStorage.setItem(STORAGE_KEY, JSON.stringify(form));
    setSaved(true);
  }

  return (
    <div>
      <h1>Configurações</h1>
      <p className="muted">
        Estes campos ajudam a organizar suas credenciais antes de colocá-las nas variáveis de
        ambiente do backend (arquivo <code>.env</code> ou secrets do Railway). Por segurança, as
        chaves reais de produção não devem ser armazenadas no frontend.
      </p>

      <div className="card settings-form" style={{ maxWidth: 480 }}>
        <label>Twilio Account SID</label>
        <input
          value={form.twilioAccountSid}
          onChange={(e) => update("twilioAccountSid", e.target.value)}
          placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        />

        <label>Twilio Auth Token</label>
        <input
          type="password"
          value={form.twilioAuthToken}
          onChange={(e) => update("twilioAuthToken", e.target.value)}
        />

        <label>Stripe Key</label>
        <input
          type="password"
          value={form.stripeKey}
          onChange={(e) => update("stripeKey", e.target.value)}
          placeholder="sk_live_… (usado na Fase 3)"
        />

        <label>Claude API Key</label>
        <input
          type="password"
          value={form.claudeApiKey}
          onChange={(e) => update("claudeApiKey", e.target.value)}
          placeholder="sk-ant-…"
        />

        <div style={{ marginTop: 20 }}>
          <button className="btn btn-primary" onClick={handleSave}>
            Salvar rascunho local
          </button>
          {saved && <span className="muted" style={{ marginLeft: 10 }}>Rascunho salvo neste navegador.</span>}
        </div>
      </div>
    </div>
  );
}
