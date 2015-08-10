import scraperwiki
import lxml.html

year = "2013"
baseurl = "http://www.inc.com/inc5000/list/"

#for yr in xrange
batch = ["/800"]
for i in xrange (9, 50):
    batch.append("/"+str(i*100))

for group in batch:
    url = baseurl+year+group
    page = scraperwiki.scrape(url)

    root = lxml.html.fromstring(page)

    for tr in root.cssselect("div#inc5000_table tr"):
      
      tds = tr.cssselect("td")
      if len(tds) == 8:
        co_url = tr.cssselect("a")
        co_url = co_url[0].attrib["href"]
        co_page = scraperwiki.scrape(co_url)
        if co_url[len(co_url)-1] == '/':
            base_rev = -1.0
            jobadd = 0
            website = "NA"
            weburl = "NA"
            desc = "NO PROFILE PAGE"
        else:
           co_root = lxml.html.fromstring(co_page)
        
           d = co_root.cssselect("p")
           desc = d[0].text_content()
           for cd in co_root.cssselect("div.inc5000companydata p"):
              t=cd.text_content()
              if t.find("2009 Rev") != -1:
                  base_revst = t.rsplit(":")[1] 
                  base_revst = base_revst.lstrip("$")
                  base_revst = base_revst.replace(",", "")
                  if base_revst.find("million") != -1:
                      base_revst = base_revst.rstrip("million")
                      base_rev = int(float(base_revst)*1000000.0)
                  elif base_revst.find("billion") != -1:
                      base_revst = base_revst.rstrip("billion")
                      print "2009 ", base_revst
                      base_rev = int(float(base_revst)*1000000000.0)
                  else :
                      base_rev = int(base_revst)
            
              if t.find("Jobs") != -1:
                  jobadd = int(t.rsplit(":")[1])
              if t.find("Web") != -1:
                  u = cd.cssselect("a")
                  weburl = u[0].attrib["href"]
                  website = t.rsplit(":")[1]

      if len(tds)==8:
            incomplete_data = [""]   #Create repository for memoes on data that was unavailable

            rank = int(tds[0].text_content())
            company = tds[1].text_content()

            # convert from string like "8,234%" to a floating point.  divide by 100 to convert to decimal
            revgrowth_st = tds[2].text_content().rstrip("%")
            revgrowth_st = revgrowth_st.replace(",", "")
            revgrowth = float(revgrowth_st)/100.0

            # convert revenue from string like "$128.9 million" to integer 128,900,000
            curr_revst = tds[3].text_content().lstrip("$")
            curr_revst = curr_revst.replace(",", "")
            if curr_revst.find("million") != -1:
                curr_revst = curr_revst.rstrip("million")
                curr_rev = int(float(curr_revst)*1000000.0)
            elif curr_revst.find("billion") != -1:
                print "2012 ", curr_revst
                curr_revst = curr_revst.rstrip("billion")
                curr_rev = int(float(curr_revst)*1000000000.0)
            else:
                curr_rev = int(float(curr_revst))

            industry = tds[4].text_content().encode('ascii', 'ignore').lstrip()  #remove the unicode colored bullet from front of industry name

            # at least one of the rows does not have an employee number.  
            # In that case set it to zero, later change it to the base year number if possible and set incomplete data flag.
            if len(tds[5].text_content()) > 0:
                curr_emps = int(tds[5].text_content())
            else:
                curr_emps = 0
                incomplete_data.append("curr_emps")

            city = tds[6].text_content()
            city = city.title()
            state = tds[7].text_content()

            if curr_emps-jobadd == 0 :
                empgrowthf = float(curr_emps)
            else :
                empgrowthf = float(curr_emps)/float(curr_emps-jobadd)


            data = {
                'rank'            : rank,
                'company'         : company,
                'rev growth'      : revgrowth,
                'base revenue'    : base_rev,
                'curr revenue'    : curr_rev,
                'industry'        : industry,
                'curr emps'       : curr_emps,
                'jobs added'      : jobadd,
                'prev emps'       : curr_emps - jobadd,
                'emp growth'      : empgrowthf,
                'city'            : city,
                'state'           : state,
                'url'             : weburl,
                'website'         : website,
                'description'     : desc
            }
            print data
            scraperwiki.sqlite.save(unique_keys=['rank'], data=data)
