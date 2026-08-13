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
