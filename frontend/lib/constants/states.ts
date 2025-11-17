/**
 * States for Facility Locations
 *
 * These are the three states where the 91 facilities are located.
 * This list is limited to ensure data consistency.
 */

export const STATES = [
  'Kano',
  'Jigawa',
  'Bauchi',
] as const;

export type State = typeof STATES[number];

/**
 * Check if a string is a valid state
 */
export function isValidState(state: string): state is State {
  return STATES.includes(state as State);
}
