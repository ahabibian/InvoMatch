import { useState } from "react";
import type { FormEvent } from "react";
import { useAuthSession } from "../auth/useAuthSession";

export default function PilotLogin() {
  const { login } = useAuthSession();
  const [credential, setCredential] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(credential);
      setCredential("");
    } catch {
      setError("The pilot credential was rejected or the session could not be established.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main style={{ margin: "80px auto", maxWidth: 420, padding: 24 }}>
      <h1>InvoMatch Pilot</h1>
      <p>Enter the credential supplied by the pilot operator. It is exchanged for an HttpOnly session and is not stored by the UI.</p>
      <form onSubmit={submit}>
        <label htmlFor="pilot-credential">Pilot credential</label>
        <input
          id="pilot-credential"
          type="password"
          autoComplete="current-password"
          value={credential}
          onChange={(event) => setCredential(event.target.value)}
          required
          style={{ boxSizing: "border-box", display: "block", margin: "8px 0 16px", padding: 8, width: "100%" }}
        />
        <button disabled={submitting} type="submit">
          {submitting ? "Signing in..." : "Sign in"}
        </button>
      </form>
      {error && <p role="alert" style={{ color: "red" }}>{error}</p>}
    </main>
  );
}
