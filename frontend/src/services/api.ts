export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(path);
  return response.json() as Promise<T>;
}
