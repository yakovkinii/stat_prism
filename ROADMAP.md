<style>
g{
  color: green;
}
y{
  color: #aa0;
}
r{
  color: #a00;
}
</style>

# Development roadmap

## <g>Early evaluation (before v0.5)</g> 

### <g>Required features for early evaluation:</g>

<details>
<summary></summary>

* <g>Delete results</g>
* <g>Save/load reports</g>
* <g>Export/copy reports</g>
* <g>Fully restore correlations</g> 
* <g>Minimally restore descriptives</g>
* <g>Add filters</g>
* <g>Ask to save and delete results on opening a new file</g>
* <g>Handle mixed types in the data</g>
* <g>Find a solution for HTML-related CTD</g>
* <g>Add UI for filters</g>
* <g>Polish interface</g>
* <g>Reimplement verbal results for descriptive statistics</g>
* <g>Add correlation plots</g>

</details>

### <g>Early evaluation feedback:</g>

<details>
<summary></summary>

* User interface: layout and general usability &ndash; <g>Positive feedback</g>
* User interface: color scheme and design &ndash; <g>Positive feedback</g>
* Feature-completeness of correlations &ndash; 
<r>
Need to add more options, especially filters.
Emphasis was put on that MVP should have all primary analysis types, with all options implemented.
</r>
* Any bugs or crashes &ndash; 
<g>
Flickering on first study creation. Overall, the app is stable. 
</g>
* Any manual adjustments left over &ndash;
<y>
Table slicing and rotated copying were requested. 
</y>
* Other &ndash;
<g>App updates should be incremental. Model specs will be provided on request. 
Need multiple representations of each analysis, but only one will typically be used. 
For plots, the customization is mostly regarding the color scheme.</g>

</details>

---

## Unfreezing Preparation (before v0.6) 

### Required features before unfreezing:

[//]: # (<details>)
<summary></summary>

* <g><s>Color column selector according to the column category</s></g>
* <g>Custom column inversion calibration</g>
* <g>UI for changing column type and dtype</g>
* <g>Advanced filters</g>
* <g>Group column values into custom categories</g>
* <g>Add plots and plot tools</g>
* <g>Unify result styles</g>
* <g>Refactor the modules</g>
* <g>Add some way of copying plots</g>
* <g>Fix plot size resetting</g>
* <g>Make correlations feature-complete</g>
* <g>Check and debug UI for filters</g>
* <g>Enhance UI for filters</g>
* <g>Edit table/figure captions</g>
* <g>Edit Figure axis titles</g>
* <g>Trace and remove message senders with no sender_id</g>
* (Optional) Add aliases for columns
* (Optional) Compile results to single report

[//]: # (</details>)

### Checklist for unfreezing:

[//]: # (<details>)
<summary></summary>

* <g>Correlations are fully functional and feature-complete, 
including customization.</g>
* <g>At least some way to export of each result element.</g>
* <g>Technical debt is mostly paid off.</g>
* Common UI elements are implemented to a reasonable extent.

[//]: # (</details>)

---

## After Unfreezing (v0.6+; September 2024 ME):

<details>
<summary></summary>

* Undo functionality
* All basic analyses (ANOVA, EFA, CFA, etc.)
* Table slicing on export and rotated copying
* Try-except handling

</details>
