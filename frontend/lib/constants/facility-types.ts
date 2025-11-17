/**
 * Facility Types (Healthcare Facility Levels)
 *
 * Limited to three categories for streamlined classification:
 * - Primary: Primary Health Centers, Health Posts
 * - Secondary: General Hospitals, Specialist Hospitals
 * - Tertiary: Teaching Hospitals, Federal Medical Centers
 */

export const FACILITY_TYPES = [
  'Primary',
  'Secondary',
  'Tertiary',
] as const;

export type FacilityType = typeof FACILITY_TYPES[number];

/**
 * Check if a string is a valid facility type
 */
export function isValidFacilityType(type: string): type is FacilityType {
  return FACILITY_TYPES.includes(type as FacilityType);
}

/**
 * Get description for facility type
 */
export function getFacilityTypeDescription(type: FacilityType): string {
  const descriptions: Record<FacilityType, string> = {
    'Primary': 'Primary Health Centers, Health Posts, Clinics',
    'Secondary': 'General Hospitals, Specialist Hospitals',
    'Tertiary': 'Teaching Hospitals, Federal Medical Centers',
  };
  return descriptions[type];
}
