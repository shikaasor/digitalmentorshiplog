/**
 * Thematic Areas Constants
 *
 * IMPORTANT: This list MUST match backend/app/constants.py ThematicArea class exactly!
 *
 * Two versions:
 * - THEMATIC_AREAS: Full list including "Other" (for mentorship logs)
 * - SPECIALIZATION_AREAS: Without "Other" (for user specializations)
 */

/**
 * Full list of thematic areas for mentorship logs
 * Includes "Other" option for cases not covered by predefined areas
 */
export const THEMATIC_AREAS = [
  'General HIV care and treatment',
  'Care and Support',
  'Pediatric HIV management',
  'PMTCT',
  'TB/HIV',
  'Laboratory services',
  'Supply chain',
  'Strategic Information',
  'Quality improvement',
  'Other',
] as const;

/**
 * Filtered list for user specializations
 * Excludes "Other" because specialists need specific expertise areas
 */
export const SPECIALIZATION_AREAS = [
  'General HIV care and treatment',
  'Care and Support',
  'Pediatric HIV management',
  'PMTCT',
  'TB/HIV',
  'Laboratory services',
  'Supply chain',
  'Strategic Information',
  'Quality improvement',
] as const;

export type ThematicArea = typeof THEMATIC_AREAS[number];
export type SpecializationArea = typeof SPECIALIZATION_AREAS[number];

/**
 * Get display label for a thematic area
 */
export function getThematicAreaLabel(area: string): string {
  return area;
}

/**
 * Check if a string is a valid thematic area
 */
export function isValidThematicArea(area: string): area is ThematicArea {
  return THEMATIC_AREAS.includes(area as ThematicArea);
}

/**
 * Check if a string is a valid specialization area
 */
export function isValidSpecializationArea(area: string): area is SpecializationArea {
  return SPECIALIZATION_AREAS.includes(area as SpecializationArea);
}
