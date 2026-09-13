import { useState } from "react";
import { login } from "../lib/api";
import { setToken } from "../lib/auth";

interface Props {
  onLoginSuccess: () => void;
}

export default function Login({ onLoginSuccess }: Props) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const token = await login(username, password);
      setToken(token);
      onLoginSuccess();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh" }}>
      <div className="card" style={{ width: 320 }}>
        <h1>SuportIA</h1>
        <p className="muted">Gerenciador de Suporte com IA</p>
        <form onSubmit={handleSubmit} style={{ marginTop: 24 }}>
          <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 4 }}>
            Usuário
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ marginBottom: 16, width: "100%" }}
          />

          <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 4 }}>
            Senha
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ marginBottom: 16, width: "100%" }}
          />

          {error && <p style={{ color: "#dc2626", marginBottom: 12, fontSize: 13 }}>{error}</p>}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: "100%" }}
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>

          <p className="muted" style={{ marginTop: 12, fontSize: 12, textAlign: "center" }}>
            Demo: admin / admin
          </p>
        </form>
      </div>
    </div>
  );
}
