import { useState } from 'react';
import Calendar from './components/Calendar.jsx';
import EventList from './components/EventList.jsx';
import events from './data/events.json';
import { dateKey } from './dates.js';

const eventDates = new Set(events.map((event) => event.date));

export default function App() {
  const [today] = useState(() => new Date());
  const [month, setMonth] = useState(() => new Date(today.getFullYear(), today.getMonth(), 1));
  const [selectedDate, setSelectedDate] = useState(() => dateKey(today));

  function changeMonth(offset) {
    const next = new Date(month.getFullYear(), month.getMonth() + offset, 1);
    setMonth(next);
    setSelectedDate(next.getFullYear() === today.getFullYear() && next.getMonth() === today.getMonth()
      ? dateKey(today) : null);
  }

  const selectedEvents = events
    .filter((event) => event.date === selectedDate)
    .sort((a, b) => a.startTime.localeCompare(b.startTime));

  return (
    <main>
      <Calendar month={month} today={dateKey(today)} selectedDate={selectedDate}
        eventDates={eventDates} onSelectDate={setSelectedDate} onChangeMonth={changeMonth} />
      <p className="example-note">Check the original listing for event details and availability.</p>
      {selectedDate ? <EventList date={selectedDate} events={selectedEvents} />
        : <p className="empty-state">Select a date to see events.</p>}
    </main>
  );
}
