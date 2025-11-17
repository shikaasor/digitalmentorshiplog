/**
 * Thematic Areas for Specialist Assignments
 *
 * These are the predefined thematic areas from the ACE2 mentorship log form.
 * Users can be designated as specialists in one or more of these areas.
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
] as const;

export type ThematicArea = typeof THEMATIC_AREAS[number];

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
