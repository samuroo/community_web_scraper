export default function SourceFilter({ sources, selectedSources, onToggle }) {
  return (
    <aside className="source-sidebar">
      <fieldset className="source-filter">
        <legend>SOURCES</legend>
        {sources.map(({ label, venue }) => (
          <label key={venue}>
            <input type="checkbox" checked={selectedSources.has(venue)}
              onChange={() => onToggle(venue)} />
            <span>{label}</span>
          </label>
        ))}
      </fieldset>
    </aside>
  );
}
