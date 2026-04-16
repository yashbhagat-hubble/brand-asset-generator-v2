module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.REPLICATE_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'REPLICATE_API_KEY not configured' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) {
      return res.status(400).json({ error: 'Invalid JSON body' });
    }
  }

  const { image } = body || {};
  if (!image) {
    return res.status(400).json({ error: 'image field is required' });
  }

  // Create prediction — ask Replicate to wait synchronously (fast model, ~3–8s)
  const createResp = await fetch('https://api.replicate.com/v1/models/bria/remove-background/predictions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      'Prefer': 'wait=55',
    },
    body: JSON.stringify({ input: { image } }),
  });

  if (!createResp.ok) {
    const e = await createResp.json().catch(() => ({}));
    return res.status(createResp.status).json({ error: e?.detail || `Replicate HTTP ${createResp.status}` });
  }

  let prediction = await createResp.json();

  // If not yet complete (Prefer: wait timed out), poll
  let attempts = 0;
  while (
    prediction.status !== 'succeeded' &&
    prediction.status !== 'failed' &&
    prediction.status !== 'canceled' &&
    attempts < 20
  ) {
    await new Promise(r => setTimeout(r, 1500));
    const pollResp = await fetch(`https://api.replicate.com/v1/predictions/${prediction.id}`, {
      headers: { 'Authorization': `Bearer ${apiKey}` },
    });
    if (!pollResp.ok) {
      return res.status(500).json({ error: `Poll failed: HTTP ${pollResp.status}` });
    }
    prediction = await pollResp.json();
    attempts++;
  }

  if (prediction.status !== 'succeeded') {
    return res.status(500).json({
      error: `Prediction ${prediction.status}${prediction.error ? ': ' + prediction.error : ''}`,
    });
  }

  // Fetch the transparent PNG from Replicate CDN and pipe it back
  const outputUrl = Array.isArray(prediction.output) ? prediction.output[0] : prediction.output;
  const imgResp = await fetch(outputUrl);
  if (!imgResp.ok) {
    return res.status(500).json({ error: 'Failed to fetch output image from Replicate' });
  }

  const buffer = await imgResp.arrayBuffer();
  res.setHeader('Content-Type', 'image/png');
  res.setHeader('Cache-Control', 'no-store');
  res.status(200).send(Buffer.from(buffer));
};
