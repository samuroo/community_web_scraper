import { formatDate } from '../dates.js';

export default function EventList({ date, events }) {
  return (
    <section className="events" aria-live="polite" aria-labelledby="selected-date">
      <h2 id="selected-date">{formatDate(date)}</h2>
      {events.length === 0 ? <p className="empty-state">No events.</p> : (
        <ul>{events.map((event) => (
          <li key={event.id}>
            <div className="event-time">
              <time dateTime={`${event.date}T${event.startTime}`}>{event.startTime}</time>
              {event.endTime && <>–<time>{event.endTime}</time></>}
            </div>
            <div>
              <h3>{event.title}</h3>
              <p>{event.venue}</p>
              <a href={event.url} target="_blank" rel="noopener noreferrer">More information<span className="sr-only"> about {event.title} (opens in a new tab)</span></a>
            </div>
          </li>
        ))}</ul>
      )}
    </section>
  );
}
