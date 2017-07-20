
function lt_addon_filter_mask, labelimage,

  firstYearLoss = 300 ;make this a parameter
  startYear = 1985 ;make this a parameter
  yod = this_image[*,*,0]
  mag = this_image[*,*,1]
  dur = this_image[*,*,2]
  mask = yod eq startYear and mag gt firstYearLoss or yod gt startYear or dur gt 1
  return, mask

end
  
  





