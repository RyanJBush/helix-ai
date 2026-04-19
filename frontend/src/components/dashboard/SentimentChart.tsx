interface SentimentChartProps {
  title: string;
  values: number[];
}

function SentimentChart({ title, values }: SentimentChartProps) {
  const points = values
    .map((value, index) => {
      const x = (index / Math.max(values.length - 1, 1)) * 100;
      const y = 100 - value * 100;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <article className="panel">
      <h3>{title}</h3>
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="sentiment-chart">
        <polyline points={points} fill="none" stroke="url(#gradient)" strokeWidth="2" />
        <defs>
          <linearGradient id="gradient" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#38bdf8" />
            <stop offset="100%" stopColor="#22c55e" />
          </linearGradient>
        </defs>
      </svg>
    </article>
  );
}

export default SentimentChart;
