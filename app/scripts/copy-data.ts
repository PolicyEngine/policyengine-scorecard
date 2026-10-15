import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";

mkdirSync("public/data", { recursive: true });
for (const name of ["comparison.json", "lanes.json", "exhibits.json", "populations.json"])
  cpSync(`../data/${name}`, `public/data/${name}`);

const directory = "populations-pmd";
rmSync(`public/data/${directory}`, { recursive: true, force: true });
if (existsSync(`../data/${directory}`))
  cpSync(`../data/${directory}`, `public/data/${directory}`, { recursive: true });
