const PROMPTS = {
  brandAsset: `Task: Create a high-resolution digital brand asset with fixed size 208px * 232px, fixed aspect ratio (104x116).
Background: The background is a single, uniform, solid fill of [Pick from image].
Isolating logo: Retain any texts if there in logo, do not remove anything except background.
There are no gradients, textures, soft blurs, or shadows on this layer; it is perfectly flat and consistent from top to bottom.
Logo Placement: Centered horizontally and vertically within the top 30 percent of the canvas. The logo must have a fully transparent background (no cards, panels, or bounding boxes). It should occupy approximately 70 percent of the frame width.
Logo Styling: Render the logo in a high-contrast color [pick intelligently] to ensure it is perfectly legible against the solid background—no subtext, taglines, or decorative elements.
Subject: The subject [Pick from image] is anchored to the bottom edge of the canvas.
The final output is premium, clean, and editorial with no visible dividers or borders.`,
};
