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

# StatPrism Release Notes



### StatPrism 1.2.8 (4 Sep 2026)

* Descriptive: optional frequency table for ordinal variables (off by default; rows follow the ordinal order)
* Project files: routed by module identity (not a positional index) so reordering/adding modules no longer breaks older saves; opening a project made with a newer StatPrism is now refused with a clear message
* Project files: now saved as JSON + parquet (the raw dataset and each study's settings; results are recomputed on open). 1.2.8 still opens older pickle projects, so use it to re-save them in the new format - later versions will drop pickle
* Heatmaps: color-bar width slider; tick font shrinks automatically when there are many categories
* EFA: per-item MSA and the eigenvalues table are now optional (off by default, they get long); cleaner table titles ("Eigenvalues"; "Factor loadings" with no "(none)")
* EFA: "Create a CFA from this solution" now properly selects the new CFA (its settings panel shows)
* CFA/SEM path diagram: separate name-label font slider, smaller by default and auto-shrinking with model size
* CFA: modification suggestions (cross-loadings / correlated residuals) list only the top 6, with the total count shown
* Analyses: add per-analysis inline filters (Add filter on the card) - preview removed rows, combine with AND, no chain step needed
* Formula Column: double-click a column in the new column list to insert it into the formula
* Data-processing steps now always auto-update; the Auto-recalculate setting governs analyses only
* A column an earlier study renames/removes (or retypes) now shows bold red and stops the study instead of being silently dropped
* Preprocess: rename a column by clicking its name in place (Tab fills the original); Map values / type / order are now big aligned buttons that highlight when set, with a Reset in each pop-up
* Plot settings: clicking a slider now jumps to the clicked position instead of a large step
* Heatmaps: x-axis labels are upright (rotated 90 degrees) by default
* Inline filters: each shows its condition and the extra rows it removes, are included when copying, and open by clicking the row (highlighted like a result element); the broken-column picker now keeps missing columns so you can drag them out
* Plots: contingency and heatmap x-axis labels are upright by default; long tick labels and default axis titles are trimmed with an ellipsis to avoid overlap
* Plot settings: wider ranges for size, font, spacing and related sliders
* EFA: Create a CFA from this solution (same items/factors, items assigned by loading, oblique -> correlated factors)
* Replaced Reorder Columns with Arrange Columns: drag every column into order in one compact, color-tagged list (no column selector), listed right after Calculate Scale
* Transform Column: reworked layout (Map values + type side by side, bold when set, pop-up resets); rename hidden when multiple columns are selected
* Heatmaps: a "Trim long labels" option (on by default; hidden when labels are numbered)
* CFA / SEM path diagram: size fixed by Plot Size and Aspect, spacing sliders distribute items within it; cross-loadings (dashed) and freed residual correlations now shown
* About: fixed the banner showing as a black strip (it was drawn unscaled)
* Column names shown on a color tag now pick black or white text and the matching icon set by the tag's brightness, everywhere they appear (data viewer, column selectors, Arrange) and in both UI themes
* Formula Column: multiline formula field, with Tab to auto-complete column names



### StatPrism 1.2.7 (13 Aug 2026)

* Results: rename any result by clicking its title; exports and copy use the new name
* Calculate Scale: more normalization options (Z-score, Stanine, Center, Min-max, Log, Rank)
* Calculate Scale: an unset (transparent) color now leaves item color tags unchanged
* CFA: button to create one Calculate Scale step per factor, with that factor's items pre-selected
* CFA / SEM: use semopy's standardized loadings and fit indices; DWLS fit indices are now Satorra-Bentler (WLSMV) scaled
* Descriptive: Kolmogorov-Smirnov normality test now uses the Lilliefors significance correction
* Correlation: more accurate tetrachoric standard error
* Fix stanine normalization
* Recalculate All (Ctrl+R) now deselects the current study first
* Collapsed data-processing cards keep their summary on a single line
* Docs: keyboard shortcuts reference

### StatPrism 1.2.6 (11 Aug 2026)

* CFA: add item residual correlations
* CFA: use semopy's fit indexes
* MISC: ui alignment
* New reorder dp study


### StatPrism 1.2.5 (4 Aug 2026)

* Streamline UI
* Fix html rendering after grouping with non-UNICODE symbols


### StatPrism 1.2.4 (1 Aug 2026)

* Internal clean-up
* Fix spelling


### StatPrism 1.2.3 (5 Jul 2026)

* Reformat license file
* Clean up and update resources
* Remove dev tools
* Update copyright notice


### StatPrism 1.2.2 (3 Jul 2026)

* Remove sympy tests from build.


### StatPrism 1.2.1 (3 Jul 2026)

* Remove console from installed app run.


### StatPrism 1.2.0 (2 Jul 2026)

**Data Processing**

* Allow immediate question flipping in Calculate Scale.

**Data Analysis**

* Add SEM through semopy
* Use semopy in CFA
* Add new diagrams in regression/FA/SEM
* Improve verbal indicators and prose

**Miscellaneous**

* Prepare for CI nuitka build
* Overall alignment of modules


### StatPrism 1.1.0 (28 Jun 2026)

* Set up releases. 


### StatPrism 1.0.0 (20 June 2026)

**New data-processing steps**

* Transform Column — change type / mapping / order / normalisation, now over **multiple
  columns at once** (one shared spec; rename disabled for multi-select)
* One-hot encoding and Split Multi-Select for "select all that apply" data
* Group Values, Impute Missing, Select ID, and Bootstrap Sensitivity
* Outlier detection: grouped and 2-D variants, with ordinal support

**New & extended analyses**

* Confirmatory Factor Analysis (CFA), Cluster Analysis
* Partial/controlled correlation, paired correlation, logistic regression
* Power Analysis with confidence intervals and effect sizes
* Multiple Response summaries; question numbering for wide tables

**Interface**

* Dark mode, with a light/dark UI-theme switch in the menu
* Collapsible study cards with modern toggle switches and compact titles
* Settings-panel breadcrumbs and back-to-parent navigation
* Opt-in verbal (plain-text) interpretation across analyses
* Optional auto-recalculate, plus Ctrl+R to recalculate everything
* Restructured menus (File / Settings / Help)

**Under the hood**

* Plot theme and language are remembered between sessions (statprism.ini)
* Interface translations (i18n) with language switching
* Modules regrouped in the registry with shared, family-based icons
* HTML snapshot test suite and an online user guide (Read the Docs)
* Packaging prepared for Nuitka-built Windows executables
