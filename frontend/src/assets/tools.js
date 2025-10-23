export const formatDate = (date) => {
  if (!date) return 'N/A';
  return new Date(date).toLocaleDateString('en-UK', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    second: 'numeric',
  });
};

/**
 * Converts a string into a URL-friendly slug
 * @param {string} str - The string to slugify
 * @returns {string} The slugified string
 *
 * Example:
 * slugify("Hello World!") => "hello-world"
 * slugify("This & That") => "this-and-that"
 * slugify("Über Café") => "uber-cafe"
 */
export function slugify(str) {
  /* eslint-disable no-useless-escape */
  return (
    str
      // Convert to lowercase
      .toLowerCase()
      // Replace special characters with their simpler equivalents
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      // Replace common special characters with text equivalents
      .replace(/&/g, '-and-')
      .replace(/[^a-z0-9\-\s]/g, '')
      // Replace spaces and repeated dashes with single dash
      .replace(/[\s\-]+/g, '-')
      // Remove leading and trailing dashes
      .replace(/^-+|-+$/g, '')
  );
}

export function removeTrailingSlashes(str) {
  if (typeof str !== 'string') {
    console.error('Input must be a string.');
    return str;
  }
  return str.replace(/\/+$/, '');
}