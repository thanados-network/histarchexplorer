
/**
 * Fetches a PresentationView model from the Flask backend.
 * @param {number} id - The entity ID.
 * @returns {Promise<Object>} The JSON response.
 */
async function fetchPresentationView(id) {
  try {
    const response = await fetch(`/presentation_view/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch PresentationView ${id}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching presentation view:", error);
    return null;
  }
}
