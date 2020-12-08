// @ts-check

/** @typedef {import('./api').ScheduleMetadata} ScheduleMetadata */

/**
 * Mapping from schedule identifiers (e.g. "MOBIS") to
 * schedule labels (e.g. "874 - Legacy MOBIS").
 */
export const scheduleLabels = {};

/**
 * Populate scheduleLabels from schedule metadata.
 * 
 * @param {ScheduleMetadata[]} schedules 
 */
export function populateScheduleLabels(schedules) {
  Object.keys(scheduleLabels).forEach((label) => {
    delete scheduleLabels[label];
  });
  schedules.forEach((schedule) => {
    scheduleLabels[schedule.schedule] = schedule.full_name;
  });
}
