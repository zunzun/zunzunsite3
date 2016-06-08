 function cT(id)
 {
    if (ns4)
    {
        len = d.layers.length;
        count = 0;
        for (i=0; i<len; i++)
        {
            if ((d.layers[i].id.toString().substring(0,3) == "CPX") && (d.layers[i].style.backgroundColor.replace(/\s/g, '') == w))
            {
                count += 1;
            }
        }
        if ((count >= maxCoeffs) && (d.layers[id].style.backgroundColor.replace(/\s/g, '') == lg))
        {
            alert(warning);
            return;
        }

        if (d.layers[id].style.backgroundColor.replace(/\s/g, '') == lg)
        {
            d.layers[id].style.backgroundColor = w;
            d.layers[id].borderStyle = ins;
        }
        else
        {
            d.layers[id].style.backgroundColor = lg;
            d.layers[id].borderStyle = os;
        }

        tstr = "<B>y = &nbsp; (</B>";
        str = "";
        count = 0;
        totalCount = 0;
        for (i=0; i<len; i++) // Numerator
        {
            if (d.layers[i].id.toString().substring(0,5) != "CPX_N")
            {
                continue;
            }

            if (d.layers[i].style.backgroundColor.replace(/\s/g, '') == w)
            {
                if (count > 0)
                    tstr += "&nbsp+ ";
                if (d.layers[i].id.toString().substring(5,6) == "0")
                    tstr += '<B>' + c[totalCount] + '</B>';
                else
                    tstr += '<B>' + c[totalCount] + '(&nbsp;</B>' + d.all[i].innerHTML + '<B>&nbsp;)</B>';
                count += 1;
                totalCount += 1;
            }
        }
        tstr += "<B>) &nbsp; / &nbsp; (1.0 + </B>";
        count = 0;
        for (i=0; i<len; i++) // Denominator
        {
            if (d.layers[i].id.toString().substring(0,5) != "CPX_D")
            {
                continue;
            }

            if (d.layers[i].style.backgroundColor.replace(/\s/g, '') == w)
            {
                if (count > 0)
                    tstr += "&nbsp+ ";
                if (d.layers[i].id.toString().substring(5,6) == "0")
                    tstr += '<B>' + c[totalCount] + '</B>';
                else
                    tstr += '<B>' + c[totalCount] + '(&nbsp;</B>' + d.all[i].innerHTML + '<B>&nbsp;)</B>';
                count += 1;
                totalCount += 1;
            }
        }
        tstr += "<B>)</B>";
        
        for (i=0; i<len; i++) // Offset
        {
            if (d.layers[i].id.toString().substring(0,5) != "CPX_O")
            {
                continue;
            }

            if (d.layers[i].style.backgroundColor.replace(/\s/g, '') == w)
            {
                tstr += ' &nbsp; + &nbsp; <B>' + c[totalCount] + '</B>';
            }
        }
        
        d.layers['FUNCTION'].innerHTML = tstr;
    }

    if (ie4)
    {
        len = d.all.length;
        count = 0;
        for (i=0; i<len; i++)
        {
            if ((d.all[i].id.toString().substring(0,3) == "CPX") && (d.all[i].style.backgroundColor.replace(/\s/g, '') == w))
            {
                count += 1;
            }
        }
        if ((count >= maxCoeffs) && (d.all[id].style.backgroundColor.replace(/\s/g, '') == lg))
        {
            alert(warning);
            return;
        }

        if (d.all[id].style.backgroundColor.replace(/\s/g, '') == lg)
        {
            d.all[id].style.backgroundColor = w;
            d.all[id].style.borderStyle = ins;
        }
        else
        {
            d.all[id].style.backgroundColor = lg;
            d.all[id].style.borderStyle = os;
        }

        tstr = "<B>y = &nbsp; (</B>";
        str = "";
        count = 0;
        totalCount = 0;
        for (i=0; i<len; i++) // Numerator
        {
            if (d.all[i].id.toString().substring(0,5) != "CPX_N")
            {
                continue;
            }

            if (d.all[i].style.backgroundColor.replace(/\s/g, '') == w)
            {
                if (count > 0)
                    tstr += "&nbsp+ ";
                if (d.all[i].id.toString().substring(5,6) == "0")
                    tstr += '<B>' + c[totalCount] + '</B>';
                else
                    tstr += '<B>' + c[totalCount] + '(&nbsp;</B>' + d.all[i].innerHTML + '<B>&nbsp;)</B>';
                count += 1;
                totalCount += 1;
            }
        }
        tstr += "<B>) &nbsp; / &nbsp; (1.0 + </B>";
        count = 0;
        for (i=0; i<len; i++) // Denominator
        {
            if (d.all[i].id.toString().substring(0,5) != "CPX_D")
            {
                continue;
            }

            if (d.all[i].style.backgroundColor.replace(/\s/g, '') == w)
            {
                if (count > 0)
                    tstr += "&nbsp+ ";
                if (d.all[i].id.toString().substring(5,6) == "0")
                    tstr += '<B>' + c[totalCount] + '</B>';
                else
                    tstr += '<B>' + c[totalCount] + '(&nbsp;</B>' + d.all[i].innerHTML + '<B>&nbsp;)</B>';
                count += 1;
                totalCount += 1;
            }
        }
        tstr += "<B>)</B>";
        
        for (i=0; i<len; i++) // Offset
        {
            if (d.all[i].id.toString().substring(0,5) != "CPX_O")
            {
                continue;
            }

            if (d.all[i].style.backgroundColor.replace(/\s/g, '') == w)
            {
                tstr += ' &nbsp; + &nbsp; <B>' + c[totalCount] + '</B>';
            }
        }

        d.all['FUNCTION'].innerHTML = tstr;
    }
 }

 function readPolyFlags()
 {
    if (ns4)
    {
        len = document.layers.length;
        for (i=0; i<len; i++)
        {
        	if(document.layers[i].id.toString().substring(0,5) == 'CPX_N')
        	{
	            if (document.layers[i].style.backgroundColor.replace(/\s/g, '') == w)
	            {
	                eval("document.forms[0].elements.polyRational_X_N" + document.layers[i].id.toString().substring(5) + ".value = 'True'");
	            }
	            else
	            {
	                eval("document.forms[0].elements.polyRational_X_N" + document.layers[i].id.toString().substring(5) + ".value = 'False'");
	            }
	        }
        	if(document.layers[i].id.toString().substring(0,5) == 'CPX_D')
        	{
	            if (document.layers[i].style.backgroundColor.replace(/\s/g, '') == w)
	            {
	                eval("document.forms[0].elements.polyRational_X_D" + document.layers[i].id.toString().substring(5) + ".value = 'True'");
	            }
	            else
	            {
	                eval("document.forms[0].elements.polyRational_X_D" + document.layers[i].id.toString().substring(5) + ".value = 'False'");
	            }
	        }
        	if(document.layers[i].id.toString().substring(0,5) == 'CPX_O')
        	{
	            if (document.layers[i].style.backgroundColor.replace(/\s/g, '') == w)
	            {
	                eval("document.forms[0].elements.polyRational_OFFSET.value = 'True'");
	            }
	            else
	            {
	                eval("document.forms[0].elements.polyRational_OFFSET.value = 'False'");
	            }
	        }
        }
    }

    if (ie4)
    {
        len = document.all.length;
        for (i=0; i<len; i++)
        {
        	if(document.all[i].id.toString().substring(0,5) == 'CPX_N')
        	{
	            if (document.all[i].style.backgroundColor.replace(/\s/g, '') == w)
	            {
	                eval("document.forms[0].elements.polyRational_X_N" + document.all[i].id.toString().substring(5) + ".value = 'True'");
	            }
	            else
	            {
	                eval("document.forms[0].elements.polyRational_X_N" + document.all[i].id.toString().substring(5) + ".value = 'False'");
	            }
            }
        	if(document.all[i].id.toString().substring(0,5) == 'CPX_D')
        	{
	            if (document.all[i].style.backgroundColor.replace(/\s/g, '') == w)
	            {
	                eval("document.forms[0].elements.polyRational_X_D" + document.all[i].id.toString().substring(5) + ".value = 'True'");
	            }
	            else
	            {
	                eval("document.forms[0].elements.polyRational_X_D" + document.all[i].id.toString().substring(5) + ".value = 'False'");
	            }
            }
        	if(document.all[i].id.toString().substring(0,5) == 'CPX_O')
        	{
	            if (document.all[i].style.backgroundColor.replace(/\s/g, '') == w)
	            {
	                eval("document.forms[0].elements.polyRational_OFFSET.value = 'True'");
	            }
	            else
	            {
	                eval("document.forms[0].elements.polyRational_OFFSET.value = 'False'");
	            }
            }
        }
    }
 }
