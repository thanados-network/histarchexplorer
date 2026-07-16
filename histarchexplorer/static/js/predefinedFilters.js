/**
 * Predefined filters for the browse view.
 *
 * Each entry describes a named filter preset that maps directly to the
 * filter parameters consumed by applyCombinedFilter() / Tabulator's
 * setFilter().
 *
 * Supported filter_parameters keys:
 *   - case_study_ids   {number[]}  – list of case-study entity IDs
 *   - type_ids         {number[]}  – list of type IDs (exact match)
 *   - include_subtypes {boolean}   – when true, subtypes of type_ids are
 *                                    included (uses selectedNodeIdsWithChildren
 *                                    logic in the tree)
 *   - classes          {string[]}  – entity class names to restrict to
 *   - begin_from       {string}    – earliest begin date (ISO 8601 or
 *                                    slider string, e.g. "-0500-01-01")
 *   - begin_to         {string}    – latest begin date
 *   - end_from         {string}    – earliest end date
 *   - end_to           {string}    – latest end date
 *   - include_no_begin {boolean}   – include entities without a begin date
 *   - include_no_end   {boolean}   – include entities without an end date
 *
 * tabs {string[]} – list of tab names to show for this preset
 *                   (e.g. ["places", "items", "features"])
 */
const predefinedFilters = [
    {
        label: "Thanados",
        description: "Show only entities belonging to the Thanados project.",
        icon: "https://thanados.net/static/images/icons/logo_big.png",
        tabs: ["places", "items", "features"],
        filter_parameters: {
            case_study_ids: [181731]
        }
    },
    {
        label: "Type 285 (incl. subtypes)",
        description: "Show only entities of type 285 and all its subtypes.",
        icon: null,
        tabs: [],
        filter_parameters: {
            type_ids: [285],
            include_subtypes: true,
            begin_from: "-0800-01-01",
            begin_to: "-0400-01-01",
            end_from: "-0800-01-01",
            end_to: "-0400-01-01",
            include_no_begin: true,
            include_no_end: true
        }
    }
];
