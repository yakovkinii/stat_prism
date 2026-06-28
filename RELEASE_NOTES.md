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
