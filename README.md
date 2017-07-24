# EE_LT-IDL_patchify
IDL scripts to patchify change events found in LandTrendr segmentation outputs derived in Google Earth Engine

# TODO
* _post_processing/label/lt_label.pro_ has hardcoded parameter values as arguments to _post_processing/label/lt_addon_filter_mask.pro_ - these parameters need to added to the run file template _scripts/lt_label_batch_static.txt_ and _scripts/label_filter_params_template.txt_
* _scripts/tiles/make_labfilt_mosaics.py_ needs to be made terminal friendly - the parameter arguments are currently hardcoded
