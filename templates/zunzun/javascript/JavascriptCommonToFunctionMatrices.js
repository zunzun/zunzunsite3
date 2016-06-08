ns4 = (document.layers)? true:false
ie4 = (document.all)? true:false
if((ns4 == false) && (ie4 == false)){
    document.all = document.getElementsByTagName("*")
    ie4 = true
}

lg = "rgb(211,211,211)"
 w = "rgb(255,255,255)"
 ins = "inset"
 os = "outset"
 d = document
 c = "abcdfghijkmnpqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ".split("")
 maxCoeffs = 15
 warning = 'The limit is currently ' + maxCoeffs + ' selections.'
