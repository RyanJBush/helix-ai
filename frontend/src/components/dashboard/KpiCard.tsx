interface KpiCardProps {
  label: string;
  value: string;
  delta?: string;
  tone?: 'positive' | 'negative' | 'neutral';
}

function KpiCard({ label, value, delta, tone = 'neutral' }: KpiCardProps) {
  return (
    <article className="kpi-card">
      <p className="kpi-label">{label}</p>
      <h3>{value}</h3>
      {delta ? <span className={`badge ${tone}`}>{delta}</span> : null}
    </article>
  );
}

export default KpiCard;
