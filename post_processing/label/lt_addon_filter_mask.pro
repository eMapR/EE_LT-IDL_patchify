
function lt_addon_filter_mask, this_image, startYear, endYear, firstYearLoss, endYearLoss

  yod = this_image[*,*,0]
  mag = this_image[*,*,1]
  dur = this_image[*,*,2]
  startYearMask = yod eq startYear and mag gt firstYearLoss or yod gt startYear or dur gt 1
  endYearMask = yod eq endYear and mag gt endYearLoss or yod lt endYear
  return, startYearMask * endYearMask

end
  
  





