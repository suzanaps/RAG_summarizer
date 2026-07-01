"use client";

import Link from "next/link";

export default function RegisterPage() {
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Criar Nova Conta</h2>
        
        <form style={styles.form} onSubmit={(e) => e.preventDefault()}>
          <div style={styles.inputGroup}>
            <label htmlFor="name" style={styles.label}>Nome Completo *</label>
            <input type="text" id="name" placeholder="Seu nome" style={styles.input} required />
          </div>

          <div style={styles.inputGroup}>
            <label htmlFor="username" style={styles.label}>Username *</label>
            <input type="text" id="username" placeholder="Escolha um username" style={styles.input} required />
          </div>

          <div style={styles.inputGroup}>
            <label htmlFor="email" style={styles.label}>E-mail *</label>
            <input type="email" id="email" placeholder="seu@email.com" style={styles.input} required />
          </div>

          <div style={styles.inputGroup}>
            <label htmlFor="password" style={styles.label}>Senha *</label>
            <input type="password" id="password" placeholder="Crie uma senha" style={styles.input} required />
          </div>

          {/* Campos Opcionais solicitados no escopo do projeto */}
          <div style={styles.inputGroup}>
            <label htmlFor="description" style={styles.label}>Descrição (Opcional)</label>
            <textarea id="description" placeholder="Fale um pouco sobre você" style={{...styles.input, resize: "none"}} rows={3} />
          </div>

          <button type="submit" style={styles.button}>Cadastrar</button>
        </form>

        <p style={styles.footerText}>
          Já possui uma conta? <Link href="/login" style={styles.link}>Faça Login</Link>
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: { display: "flex", minHeight: "100vh", padding: "2rem 0", alignItems: "center", justifyContent: "center", backgroundColor: "#f3f4f6", fontFamily: "sans-serif" },
  card: { padding: "2.5rem", background: "#fff", borderRadius: "10px", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)", width: "100%", maxWidth: "420px" },
  title: { textAlign: "center" as const, marginBottom: "2rem", color: "#111827", fontSize: "1.5rem", fontWeight: "bold" },
  form: { display: "flex", flexDirection: "column" as const, gap: "1.25rem" },
  inputGroup: { display: "flex", flexDirection: "column" as const, gap: "0.5rem" },
  label: { fontSize: "0.875rem", fontWeight: "500", color: "#374151" },
  input: { padding: "0.75rem", borderRadius: "6px", border: "1px solid #d1d5db", fontSize: "1rem", outline: "none" },
  button: { padding: "0.75rem", background: "#2563eb", color: "#fff", border: "none", borderRadius: "6px", fontSize: "1rem", cursor: "pointer", fontWeight: "600", marginTop: "0.5rem" },
  footerText: { textAlign: "center" as const, marginTop: "1.5rem", fontSize: "0.875rem", color: "#4b5563" },
  link: { color: "#2563eb", textDecoration: "none", fontWeight: "500" }
};