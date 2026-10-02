const CARD_WIDTH = 1200;
const CARD_HEIGHT = 630;

const COLORS = {
  ink: "#151b26", panel: "#1d2534", line: "#313d52",
  paper: "#ede8d8", muted: "#9aa4b8", gold: "#c9a24b",
};

function wrapText(ctx, text, maxWidth) {
  const words = text.split(" ");
  const lines = [];
  let current = "";
  for (const word of words) {
    const test = current ? `${current} ${word}` : word;
    if (ctx.measureText(test).width > maxWidth && current) {
      lines.push(current);
      current = word;
    } else {
      current = test;
    }
  }
  if (current) lines.push(current);
  return lines;
}

export function drawPatternCard(report, userName) {
  const canvas = document.createElement("canvas");
  canvas.width = CARD_WIDTH;
  canvas.height = CARD_HEIGHT;
  const ctx = canvas.getContext("2d");

  ctx.fillStyle = COLORS.ink;
  ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT);
  ctx.fillStyle = COLORS.gold;
  ctx.fillRect(0, 0, CARD_WIDTH, 8);

  ctx.direction = "rtl";
  ctx.textAlign = "center";

  ctx.fillStyle = COLORS.gold;
  ctx.font = "500 26px 'IBM Plex Sans Arabic', sans-serif";
  ctx.fillText("نمط قرارك في الموارد البشرية", CARD_WIDTH / 2, 100);

  ctx.fillStyle = COLORS.paper;
  ctx.font = "700 58px 'IBM Plex Sans Arabic', sans-serif";
  ctx.fillText(report.dominant_archetype_ar, CARD_WIDTH / 2, 200);

  ctx.fillStyle = COLORS.muted;
  ctx.font = "400 28px 'IBM Plex Sans Arabic', sans-serif";
  ctx.direction = "ltr";
  ctx.fillText(report.dominant_archetype, CARD_WIDTH / 2, 245);
  ctx.direction = "rtl";

  ctx.strokeStyle = COLORS.line;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(280, 290);
  ctx.lineTo(920, 290);
  ctx.stroke();

  const namePart = userName && userName.trim() ? userName.trim() : "أنت";
  const sentence = `${namePart} ${namePart === "أنت" ? "تميل" : "يميل"} إلى النظر لقرارات الموارد البشرية بأسلوب ${report.dominant_archetype_ar}: ${report.traits}.`;

  ctx.fillStyle = COLORS.paper;
  ctx.font = "400 26px 'IBM Plex Sans Arabic', sans-serif";
  wrapText(ctx, sentence, 820).slice(0, 3).forEach((line, i) => {
    ctx.fillText(line, CARD_WIDTH / 2, 345 + i * 40);
  });

  ctx.fillStyle = COLORS.gold;
  ctx.font = "400 22px 'IBM Plex Sans Arabic', sans-serif";
  wrapText(ctx, `نقطة قوة: ${report.strengths}`, 800).slice(0, 1).forEach((line, i) => {
    ctx.fillText(line, CARD_WIDTH / 2, 490 + i * 34);
  });

  ctx.fillStyle = COLORS.muted;
  ctx.font = "500 22px 'IBM Plex Sans Arabic', sans-serif";
  ctx.fillText("HR Decision Lab — مختبر قرار الموارد البشرية", CARD_WIDTH / 2, CARD_HEIGHT - 50);

  return canvas;
}

export async function downloadPatternCard(report, userName) {
  if (document.fonts && document.fonts.ready) await document.fonts.ready;
  const canvas = drawPatternCard(report, userName);
  canvas.toBlob((blob) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "hr-decision-pattern.png";
    a.click();
    URL.revokeObjectURL(url);
  }, "image/png");
}
