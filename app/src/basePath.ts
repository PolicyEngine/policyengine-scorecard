export function withBasePath(
  path: string,
  basePath: string = import.meta.env.BASE_URL,
): string {
  const normalizedBase = basePath.endsWith("/") ? basePath : `${basePath}/`;
  return `${normalizedBase}${path.replace(/^\/+/, "")}`;
}
