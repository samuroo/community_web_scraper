import { dateKey, formatDate } from '../dates.js';

const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export default function Calendar({ month, today, selectedDate, eventDates, onSelectDate, onChangeMonth }) {
  const year = month.getFullYear();
  const monthIndex = month.getMonth();
  const firstWeekday = (month.getDay() + 6) % 7;
  const daysInMonth = new Date(year, monthIndex + 1, 0).getDate();
  const cells = Array.from({ length: Math.ceil((firstWeekday + daysInMonth) / 7) * 7 }, (_, index) => {
    const day = index - firstWeekday + 1;
    return day > 0 && day <= daysInMonth ? day : null;
  });

  return (
    <section aria-label="Event calendar">
      <div className="month-navigation">
        <button type="button" aria-label="Previous month" onClick={() => onChangeMonth(-1)}>‹</button>
        <h1 aria-live="polite">{month.toLocaleDateString('en-GB', { month: 'long', year: 'numeric' })}</h1>
        <button type="button" aria-label="Next month" onClick={() => onChangeMonth(1)}>›</button>
      </div>
      <table className="calendar" aria-label={month.toLocaleDateString('en-GB', { month: 'long', year: 'numeric' })}>
        <thead><tr>{weekdays.map((day) => <th key={day} scope="col">{day}</th>)}</tr></thead>
        <tbody>{Array.from({ length: cells.length / 7 }, (_, row) => (
          <tr key={row}>{cells.slice(row * 7, row * 7 + 7).map((day, column) => {
            if (!day) return <td key={column} />;
            const key = dateKey(new Date(year, monthIndex, day));
            const hasEvents = eventDates.has(key);
            return (
              <td key={column}>
                <button type="button" className="day" aria-pressed={selectedDate === key}
                  aria-current={today === key ? 'date' : undefined}
                  aria-label={`${formatDate(key)} ${year}${hasEvents ? ', has events' : ''}`}
                  onClick={() => onSelectDate(key)}>
                  <span>{day}</span>
                  <span className={`event-dot${hasEvents ? ' visible' : ''}`} aria-hidden="true" />
                </button>
              </td>
            );
          })}</tr>
        ))}</tbody>
      </table>
    </section>
  );
}
