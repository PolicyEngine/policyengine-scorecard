import type { Country } from "./types";

/** What each country instance is compared against — the page subtitle. */
export const COUNTERPART: Record<Country, string> = {
  US: "PolicyEngine US against Urban Institute's State of the Safety Net",
  UK: "PolicyEngine UK against DWP, HMRC, OBR and UKMOD",
  BE: "PolicyEngine Belgium against SPF Finances, Cour des comptes and JRC EUROMOD-BE",
  NZ: "PolicyEngine New Zealand against official budget scores",
};
