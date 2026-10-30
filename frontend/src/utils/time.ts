/**
 * Transit Time and Schedule Formatting Utilities for Raahi.
 * Provides clean 12-hour AM/PM representations, quick increment calculations,
 * and arrival/departure schedule synchronizations.
 */

export function formatTime12(timeStr?: string): string {
  if (!timeStr) return '';
  const trimmed = timeStr.trim();
  if (trimmed.includes('AM') || trimmed.includes('PM') || trimmed.includes('am') || trimmed.includes('pm')) {
    return trimmed;
  }

  // Handle ISO format if full timestamp is passed
  let rawTime = trimmed;
  if (trimmed.includes('T')) {
    const afterT = trimmed.split('T')[1];
    rawTime = afterT.substring(0, 5);
  }

  const parts = rawTime.split(':');
  if (parts.length < 2) return rawTime;

  let hours = parseInt(parts[0], 10);
  const minutes = parts[1].substring(0, 2).padStart(2, '0');
  if (isNaN(hours)) return rawTime;

  const period = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  if (hours === 0) hours = 12;

  return `${hours}:${minutes} ${period}`;
}

export function getCurrentTime24(): string {
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, '0');
  const mm = String(now.getMinutes()).padStart(2, '0');
  return `${hh}:${mm}`;
}

export function addMinutesToTime(timeStr: string, minutesToAdd: number): string {
  try {
    let [hh, mm] = timeStr.split(':').map(Number);
    if (isNaN(hh) || isNaN(mm)) {
      const now = new Date();
      hh = now.getHours();
      mm = now.getMinutes();
    }
    const totalMinutes = (hh * 60 + mm + minutesToAdd + 1440) % 1440;
    const newHh = String(Math.floor(totalMinutes / 60)).padStart(2, '0');
    const newMm = String(totalMinutes % 60).padStart(2, '0');
    return `${newHh}:${newMm}`;
  } catch {
    return getCurrentTime24();
  }
}
