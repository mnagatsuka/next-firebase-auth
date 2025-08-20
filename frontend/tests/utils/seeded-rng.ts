// Deterministic PRNG (Mulberry32)
export function createRng(seed = 1) {
	let t = seed >>> 0 || 1;
	return function next() {
		t += 0x6d2b79f5;
		let r = Math.imul(t ^ (t >>> 15), 1 | t);
		r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
		return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
	};
}

export function int(rng: () => number, min: number, max: number) {
	return Math.floor(rng() * (max - min + 1)) + min;
}

export function pick<T>(rng: () => number, arr: T[]): T {
	return arr[Math.floor(rng() * arr.length)]!;
}

export function makeId(rng: () => number, prefix: string) {
	const n = int(rng, 100, 999);
	return `${prefix}-${n}`;
}

export function word(rng: () => number) {
	const words = [
		"next",
		"react",
		"query",
		"openapi",
		"msw",
		"orval",
		"firebase",
		"auth",
		"typescript",
		"frontend",
		"schema",
		"mock",
	];
	return pick(rng, words);
}

export function sentence(rng: () => number, count = 8) {
	const parts: string[] = [];
	for (let i = 0; i < count; i++) parts.push(word(rng));
	const s = parts.join(" ");
	return s.charAt(0).toUpperCase() + s.slice(1) + ".";
}
