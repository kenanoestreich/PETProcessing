## 0.1.0 (2025-03-19)

### Feat

- add overrides to default tacs
- change out_image_path to str | None
- replace nib with ants
- change decay_correct() to ants
- change register function to ants
- change undo_decay_correction() to ants
- make output writing optional + minor fixes
- use ants write instead of nibabel in reg
- finished draft of stitch command; testing
- add more metadata tweaks
- file-writing in stitch_broken_scans()
- allow metadata arg for undecay()
- retool wss function, write pet2pet register
- first draft of decay_correct() and reverse
- starting to make PETPAL-friendly stitching
- add function to binarize image
- make edits from PR
- streamline; move to testing
- add autocrop step before moco
- add skip flags and parallelization
- use --skip-command flags
- add pib one liner
- add BIDS dir navigation logic to process
- progress on one-liner

### Fix

- nifty-to-nifti rename
- change half-life type to float from str
- change verbose default to false
- revert defaults change to wss per PR
- minor changes
- change stitch function to only use ants
- remove unexpected half_life in stitch()
- fix circular imports how Noah did in his PR
- remove half_life getting from stitch...()
- minor changes from PR
- remove outdated todos and use enumerate()
- fix duration logica and incorrect import
- make generate_outfile_path non-protected
- imageIO load_nii change
- unbound local variables
- too many values to unpack
- incorrect call arguments
- require half-life when necessary in moco
- removed some auto-added imports
- suvr cli takes ref region
- replace List/Tuple with List/Tuple as needed

### Refactor

- use dict '|' operator
- change signature to work w/ pipeline
