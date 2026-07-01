"use client";

import Link from "next/link";

export default function LoginPage() {
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Acessar RAG Summarizer</h2>
        
        <form style={styles.form} onSubmit={(e) => e.preventDefault()}>
          <div style={styles.inputGroup}>
            <label htmlFor="email" style={styles.label}>E-mail ou Username</label>
            <input type="text" id="email" placeholder="Seu e-mail ou username" style={styles.input} />
          </div>

          <div style={styles.inputGroup}>
            <label htmlFor="password" style={styles.label}>Senha</label>
            <input type="password" id="password" placeholder="Sua senha" style={styles.input} />
          </div>

          <button type="submit" style={styles.button}>Entrar</button>
        </form>

        <p style={styles.footerText}>
          Não tem uma conta? <Link href="/register" style={styles.link}>Cadastre-se</Link>
        </p>
      </div>
    </div>
  );
}

// Estilos rápidos inline para você visualizar imediatamente sem quebrar o layout
const styles = {
  container: { display: "flex", height: "100vh", alignItems: "center", justifyContent: "center", backgroundColor: "#f3f4f6", fontFamily: "sans-serif" },
  card: { padding: "2.5rem", background: "#fff", borderRadius: "10px", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)", width: "100%", maxWidth: "400px" },
  title: { textAlign: "center" as const, marginBottom: "2rem", color: "#111827", fontSize: "1.5rem", fontWeight: "bold" },
  form: { display: "flex", flexDirection: "column" as const, gap: "1.25rem" },
  inputGroup: { display: "flex", flexDirection: "column" as const, gap: "0.5rem" },
  label: { fontSize: "0.875rem", fontWeight: "500", color: "#374151" },
  input: { padding: "0.75rem", borderRadius: "6px", border: "1px solid #d1d5db", fontSize: "1rem", outline: "none" },
  button: { padding: "0.75rem", background: "#2563eb", color: "#fff", border: "none", borderRadius: "6px", fontSize: "1rem", cursor: "pointer", fontWeight: "600", marginTop: "0.5rem" },
  footerText: { textAlign: "center" as const, marginTop: "1.5rem", fontSize: "0.875rem", color: "#4b5563" },
  link: { color: "#2563eb", textDecoration: "none", fontWeight: "500" }
};