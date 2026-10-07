/**
 * Predefined filters for the browse view.
 *
 * Each entry is a preset object with the following top-level keys:
 *
 *   label            {string}       – display name shown in the dropdown
 *   description      {string}       – tooltip text shown on hover
 *   icon             {string|null}  – URL of an icon image, or null for none
 *   tabs             {string[]}     – tab names to make visible for this preset
 *                                     (e.g. ["places", "items", "features"]);
 *                                     pass an empty array [] to show all tabs
 *   filter_parameters {object}      – filter state to apply (see keys below)
 *
 * Supported filter_parameters keys:
 *   - case_study_ids   {number[]}  – list of case-study entity IDs to restrict
 *                                    to (matches entities belonging to those
 *                                    case studies)
 *   - type_ids         {number[]}  – list of type IDs to select in the type
 *                                    tree (exact node match)
 *   - include_subtypes {boolean}   – when true, child types of the selected
 *                                    type_ids are included automatically
 *                                    (uses selectedNodeIdsWithChildren logic)
 *   - classes          {string[]}  – entity class names to restrict to
 *                                    (e.g. ["place", "artifact"])
 *   - begin_from       {string}    – ISO 8601 date string for the lower bound
 *                                    of the begin-date slider
 *                                    (e.g. "-0500-01-01" for 500 BC).
 *                                    The nearest available slider step is
 *                                    selected automatically via
 *                                    findNearestSliderValue().
 *   - begin_to         {string}    – ISO 8601 date string for the upper bound
 *                                    of the begin-date slider
 *   - end_from         {string}    – ISO 8601 date string for the lower bound
 *                                    of the end-date slider
 *   - end_to           {string}    – ISO 8601 date string for the upper bound
 *                                    of the end-date slider
 *   - include_no_begin {boolean}   – when false, entities without a begin date
 *                                    are excluded; defaults to true if omitted
 *   - include_no_end   {boolean}   – when false, entities without an end date
 *                                    are excluded; defaults to true if omitted
 */
const predefinedFilters = [
    {
        label: "Thanados",
        description: "Show only entities belonging to the Thanados project.",
        tabs: ["places", "features", "items"],
        filter_parameters: {
            case_study_ids: [181731],
            classes: ["place", "artifact", "feature"],
            include_subtypes: true,
            begin_from: "0399-01-01",
            include_no_begin: true,
            include_no_end: true
        }
    },
    {
        label: "Churches before 1300",
        description: "Churches before 1300",
        icon: null,
        tabs: ["places"],
        filter_parameters: {
            type_ids: [285],
            include_subtypes: true,
            begin_to: "1251-01-01",
            include_no_begin: false,
            include_no_end: true
        }
    }
];
