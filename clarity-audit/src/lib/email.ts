// Transactional email via Resend (optional). Activates only when the human
// sets RESEND_API_KEY + EMAIL_FROM after configuring SPF/DKIM/DMARC.
// Until then every call is a logged no-op — the site never pretends mail sent.
export async function sendEmail(opts: { to: string; subject: string; text: string }): Promise<{ sent: boolean; reason?: string }> {
  const key = process.env.RESEND_API_KEY;
  const from = process.env.EMAIL_FROM;
  if (!key || !from) return { sent: false, reason: "email_not_configured" };
  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from, to: [opts.to], subject: opts.subject, text: opts.text }),
    });
    return res.ok ? { sent: true } : { sent: false, reason: `provider_${res.status}` };
  } catch {
    return { sent: false, reason: "network_error" };
  }
}

export function scanResultEmailText(score: number, grade: string, fixes: string[], resultUrl: string): string {
  return [
    `Your Clarity Score: ${score}/100 (${grade})`,
    ``,
    `Your top fixes:`,
    ...fixes.map((f, i) => `${i + 1}. ${f}`),
    ``,
    `Full result: ${resultUrl}`,
    `Fix #1 first — it's your quick win. Then rescan free to see your new score.`,
    ``,
    `— Clarity Audit (you asked for this email; unsubscribe anytime)`,
  ].join("\n");
}
