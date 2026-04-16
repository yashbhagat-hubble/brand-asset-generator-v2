module.exports = function handler(req, res) {
  const key = process.env.REPLICATE_API_KEY;
  if (!key) {
    return res.status(500).json({ error: 'REPLICATE_API_KEY not configured' });
  }
  res.status(200).json({ key });
};
