export default function handler(req, res) {
  const key = process.env.GEMINI_API_KEY;
  if (!key) {
    return res.status(500).json({ error: 'GEMINI_API_KEY not configured' });
  }
  res.status(200).json({ key });
}
