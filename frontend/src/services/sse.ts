export function connectSSE(url: string) {
  return new EventSource(url);
}
