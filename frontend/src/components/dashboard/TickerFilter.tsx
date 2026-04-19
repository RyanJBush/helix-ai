interface TickerFilterProps {
  options: string[];
  selected: string;
  onChange: (ticker: string) => void;
}

function TickerFilter({ options, selected, onChange }: TickerFilterProps) {
  return (
    <label className="ticker-filter">
      Ticker
      <select value={selected} onChange={(event) => onChange(event.target.value)}>
        {options.map((ticker) => (
          <option key={ticker} value={ticker}>
            {ticker}
          </option>
        ))}
      </select>
    </label>
  );
}

export default TickerFilter;
