def change_outfilename_crop(old, crop_wdt, crop_hgt):
    tmp = old
    idx1 = tmp.find('_')
    tmp = tmp[idx1 + 1:]
    idx2 = tmp.find('_') + idx1 + 1
    new_resolution = str(crop_wdt) + "x" + str(crop_hgt)
    tmp = old
    return tmp[0:idx1+1] + new_resolution + tmp[idx2:]

def overwrite_params(params, args):
    return