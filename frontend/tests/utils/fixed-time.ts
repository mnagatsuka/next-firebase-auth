// Fixed time helpers for deterministic tests
const DEFAULT_ISO = "2024-01-15T10:30:00Z";

export function fixedDate(iso: string = DEFAULT_ISO) {
	return new Date(iso);
}

export function fixedIso(iso: string = DEFAULT_ISO) {
	return fixedDate(iso).toISOString();
}

export function addMinutesIso(iso: string, minutes: number) {
	const d = new Date(iso);
	d.setMinutes(d.getMinutes() + minutes);
	return d.toISOString();
}
