#!/opt/local/bin/python2.7
# Author: Brent Miszalski
# About: Query GAIA DR2 catalogue to determine a robust set of trustworthy guide stars
# so that the guide probes for SALT RSS and HRS instruments can be pre-positioned to their
# locations. The code accounts for the complex geometry of the acquisition camera chip gaps and
# the field size as it varies with any given Position Angle on the sky.
# This pre-positioning was required to dramatically reduce acquisition times at the telescope
# i.e. as soon as the telescope has arrived at a new target, the guide probe cameras can be turned on 
# and guidance started, without having to wait for valid guide stars to be accepted.
# The code is now in use at the telescope: see Page 24 of
# https://www.salt.ac.za/wp-content/uploads/2021/11/salt_newsletter_dec2020.pdf
# Visualisation was performed using ds9 and the generated region files, with real test cases
# read in from the SALT science database.
import numpy as np
import sys, os, glob,re
import os.path 
import math
import MySQLdb
from astroquery.vizier import Vizier
import astropy.units as u
from astropy.coordinates import SkyOffsetFrame,ICRS,SkyCoord

#Position angle from database - 

#NOTES
#-Do we need to adjust mag limits for bright/dark time? thick cloud? (to work out once operational)
#-Script doesn't know about which probes active (Amber only, Basil only, or Amber + Basil). 
# This should be handled outside this script
#-Position angle is handled by the script. Input PA might need to be 360-PA to get it to match what we see on SAMMI.

#A rough function that determines whether block is RSS or HRS based on the block id
def IsBlockHRS(cursor,bid):
    #input: sql cursor, block_id
    #output: True if HRS block, False if otherwise
    qtxt="select SalticamPattern_Id, RssPattern_Id, BvitPattern_Id, HrsPattern_Id from Block join Pointing using (Block_Id) join TelescopeConfigObsConfig using (Pointing_Id) join ObsConfig on (PlannedObsConfig_Id=ObsConfig_Id) join PayloadConfig using (PayloadConfig_Id) where PayloadConfigType_Id=3 and Block_Id=%s" % block_id
    cursor.execute(qtxt)
    results = cursor.fetchall()
    nrows = cursor.rowcount
    #print "block_id=%s" % block_id
    IsHRS=False
    if(nrows > 0):
	for data in results:
                if(data[3] > 0):
                    IsHRS=True
    return IsHRS

#A small function to calculate distance between two stars
def CalcDist(ra,dec,mra,mdec):
    #input: ra,dec and mra,mdec are in decimal degrees
    #output: returns distance in decimal degrees
    dtor = np.pi/180
    #distance in degrees
    dist = 180.0/np.pi*(np.arccos(np.cos(dec*dtor)*np.cos(mdec*dtor)*np.cos((ra-mra)*dtor) + np.sin(dec*dtor)*np.sin(mdec*dtor)))
    return dist

#Given an ra and dec, find the best guide stars for each RSS probe by querying GAIA DR2 catalogue
def get_stars(ra_deg,dec_deg,PA,IsHRS):
	#pre-condition: ra_deg and dec_deg in decimal degrees; 0 <= PA <= 360; IsHRS is boolean
    #post-condition: return ra, dec and Gmag of selected guide stars.
    #for converting deg to radians
    dtor = np.pi/180
	#width of box (5 arcmin)
	width=5.0/60
    #max number of stars to query for
    max_stars=200
    #magnitude limits
    faint_limit = 17.0
    bright_limit = 12.0
    #we initially include bright stars to allow us to remove nearby/double stars,
    #but we later remove them with the bright_limit later...
    mag_filter  = "<=%.2f" % faint_limit 
    #Query the GAIA DR2 vizier catalogue (vizier catalogue identifier: I/345/gaia2)
    #The '+' in "+Gmag" sorts the list by the brightest first, which is useful for us later when it comes
    #to picking the best candidate guide stars (picked out from front of list)...
    #The '_r' column gives a handy radial distance of the star from the search position ra_deg, dec_deg

    #The proper motion (pmRA and pmDE) filter is needed to remove some stars that may be fast moving
    #e.g. block_id 78169 is an interesting test! -there's a 13.5 mag star with high proper motion!
    #This is not so much a problem *now*, soon after GAIA catalogue was made, but is more important for
    #future proofing this code... Limits of +-50mas/yr are selected in RA and Dec.
    vquery = Vizier(columns=["_r",'Source','RA_ICRS','DE_ICRS','+Gmag'],
            column_filters={"Gmag":(mag_filter),"pmRA":("> -50 && < 50"),"pmDE":("> -50 && < 50")},
            row_limit=max_stars)
    field = SkyCoord(ra=ra_deg,dec=dec_deg,unit=(u.deg,u.deg),frame='icrs')
    #results are in astroquery.utils.TableList object
    results = vquery.query_region(field,radius=("%fd" % width),catalog="I/345/gaia2")[0]

    #I separate each column into their own lists 
    #(r for RA, d for Dec and m for Gmag, rad for search radius) for simplicity
    nrows = len(results)
    print "nrows = %d" % nrows
    if(nrows > 0):
        rad = results['_r']
        r = results['RA_ICRS']
        d = results['DE_ICRS']
        m = results['Gmag']
        #by default, i.e. initially, every star is a guide star candidate (useme == 1)
        #this array is setup to keep track of which stars to consider for guide stars
        useme = [1]*nrows
        #open a ds9 region file to help visualise things - for testing purposes...
        #note this is written to disk as a region file, that is then loaded from file by ds9 later
        #with a system command launching ds9 once the program is done
        reg = open("stars.reg","w")
        reg.write("global color=white\n")
        reg.write("fk5\n")
        #setup some markers for guidelines...
        #4.0 arcmin
        #rline = "circle %.6fd %.6fd 240\" #text={4 arcmin} color=white\n" % (ra_deg,dec_deg)
        #reg.write(rline)
        #5.0 arcmin
        rline = "circle %.6fd %.6fd 300\" #text={5 arcmin} color=white select=0\n" % (ra_deg,dec_deg)
        reg.write(rline)
        #chip gaps
        #original chip gaps (smaller than and inside 1.3 arcmin gap that guide probes can't reach)
        #cx1 = ra_deg-(22.4/3600)/np.cos(dtor*dec_deg)
        #cx2 = ra_deg-((22.4+15.1)/3600)/np.cos(dtor*dec_deg)

        #1.3 arcmin gap around target where probes can't reach
        #note the divide by cos(dec) term is important here!
        cx1 = ra_deg+(0.5*1.3/60)/np.cos(dtor*dec_deg)
        cx2 = ra_deg-(0.5*1.3/60)/np.cos(dtor*dec_deg)
        cy1 = dec_deg-width
        cy2= dec_deg+width

        cx0 = ra_deg

        #these points demarcate the 1.3 arcmin gap at PA=0 deg

        [r1x,r1y] = [cx1,cy1]
        [r2x,r2y] = [cx1,cy2]
        [r3x,r3y] = [cx2,cy1]
        [r4x,r4y] = [cx2,cy2]
        #zero width line...
        [r5x,r5y] = [cx0,cy1]
        [r6x,r6y] = [cx0,cy2]

        #NOTE THAT PA MUST BE 0-360 inclusive. 
        #See pre-conditions above... 
        
        ang=-PA
        dang = 7.5 #points separated +- 7.5 deg from another on the 5 arcmin radius circle
                   #correspond to roughly 1.3/2 arcmin from the ref point
                   #determined empirically using ds9; could also be worked out using formulae for a chord...

        #note that this is the proper way to rotate RA,Dec around a circle!!
        #you cannot use standard transformation matrices!
        #these points are essentially the above points that demarcate the 1.3 arcmin gap corners, but
        #now anti-rotated for the PA, so that they appear in the same position, now matter the field PA
        #i.e. we are reflecting that the chip gap on the screen never moves, but the stars in the gap
        #will of course change with PA 
        #points for top
        r7y = dec_deg + width*math.cos(ang*dtor)
        r7x = ra_deg + width*math.sin(ang*dtor)/math.cos(r7y*dtor)
        r8y = dec_deg + width*math.cos((ang+dang)*dtor)
        r8x = ra_deg + width*math.sin((ang+dang)*dtor)/math.cos(r8y*dtor)
        r9y = dec_deg + width*math.cos((ang-dang)*dtor)
        r9x = ra_deg + width*math.sin((ang-dang)*dtor)/math.cos(r9y*dtor)
        #points for bottom (i.e. 180 deg away from those at top)
        ang=ang+180
        r10y = dec_deg + width*math.cos(ang*dtor)
        r10x = ra_deg + width*math.sin(ang*dtor)/math.cos(r10y*dtor)
        r11y = dec_deg + width*math.cos((ang+dang)*dtor)
        r11x = ra_deg + width*math.sin((ang+dang)*dtor)/math.cos(r11y*dtor)
        r12y = dec_deg + width*math.cos((ang-dang)*dtor)
        r12x = ra_deg + width*math.sin((ang-dang)*dtor)/math.cos(r12y*dtor)

        #quantities that describe the equation of the line (m=slope) for each of the chip
        #gap sides. These are used below to determine if stars are on left or right of the lines,
        #or fall into the gap
        #These make more sense once looking at region file displayed in ds9
        left_m = (r12y-r8y)/(r12x-r8x)
        left_y1 = r8y
        left_x1 = r8x

        right_m = (r11y-r9y)/(r11x-r9x)
        right_y1=r9y
        right_x1=r9x
 

        #write out the above points to the region file. These could be removed (more for debugging purposes)
        rline = "circle %.6fd %.6fd 5\" #text={r1} color=magenta width=3\n" % (r1x,r1y)
        reg.write(rline)
        rline = "circle %.6fd %.6fd 5\" #text={r2} color=magenta width=3\n" % (r2x,r2y)
        reg.write(rline)
        rline = "circle %.6fd %.6fd 5\" #text={r3} color=magenta width=3\n" % (r3x,r3y)
        reg.write(rline)
        rline = "circle %.6fd %.6fd 5\" #text={r4} color=magenta width=3\n" % (r4x,r4y)
        reg.write(rline)
        rline = "circle %.6fd %.6fd 5\" #text={r5} color=magenta width=3\n" % (r5x,r5y)
        reg.write(rline)
        rline = "circle %.6fd %.6fd 5\" #text={r6} color=magenta width=3\n" % (r6x,r6y)
        reg.write(rline)

        rline = "circle %.6fd %.6fd 7\" #text={r7} color=yellow width=3\n" % (r7x,r7y)
        reg.write(rline)
        rline = "circle %.6fd %.6fd 5\" #text={r8} color=yellow width=3\n" % (r8x,r8y)
        reg.write(rline)
        rline = "circle %.6fd %.6fd 5\" #text={r9} color=yellow width=3\n" % (r9x,r9y)
        reg.write(rline)
        rline = "circle %.6fd %.6fd 7\" #text={r10} color=yellow width=3\n" % (r10x,r10y)
        reg.write(rline)
        rline = "circle %.6fd %.6fd 5\" #text={r11} color=yellow width=3\n" % (r11x,r11y)
        reg.write(rline)
        rline = "circle %.6fd %.6fd 5\" #text={r12} color=yellow width=3\n" % (r12x,r12y)
        reg.write(rline)

        rline = "line %.6fd %.6fd %.6fd %.6fd #color=white\n" % (r1x,r1y,r2x,r2y)
        reg.write(rline)
        rline = "line %.6fd %.6fd %.6fd %.6fd #color=white\n" % (r3x,r3y,r4x,r4y)
        reg.write(rline)

        rline = "line %.6fd %.6fd %.6fd %.6fd #color=yellow\n" % (r8x,r8y,r12x,r12y)
        reg.write(rline)
        rline = "line %.6fd %.6fd %.6fd %.6fd #color=yellow\n" % (r9x,r9y,r11x,r11y)
        reg.write(rline)
        #backup
        rline = "line %.6fd %.6fd %.6fd %.6fd #color=white rotate=1\n" % (cx1,cy1,cx1,cy2) 
        reg.write(rline)
        rline = "line %.6fd %.6fd %.6fd %.6fd #color=white rotate=1\n" % (cx2,cy1,cx2,cy2) 
        reg.write(rline)
        #the actual target/centre of search; in pink so it stands out!
        rline = "circle %.6fd %.6fd 10\" #text={target} color=magenta\n" % (ra_deg,dec_deg)
        reg.write(rline)
        #a line near the target to make sure the width is OK; again, more debugging stuff
        rline = "line %.6fd %.6fd %.6fd %.6fd #color=green rotate=1\n" % (cx1,dec_deg,cx2,dec_deg) 
        reg.write(rline)
        rline = "line %.6fd %.6fd %.6fd %.6fd #color=green rotate=1\n" % ((cx1+cx2)/2.0,dec_deg-(0.5*1.3/60),(cx2+cx1)/2.0,dec_deg+(0.5*1.3/60)) 
        reg.write(rline)

        #threshold to use for removing close pairs
        thresh = 20.0/3600 #20 arcsec in degrees

        #inner radius (2 arcmin) within which all guide stars are excluded
        #this is a little larger for HRS (3.0 arcmin is a guess, operationally it could be smaller or bigger
        inner_rad = 2.0/60
        if(IsHRS):
            inner_rad = 3.0/60
        
        #Now we go through each star returned by the search
        for i in range(0,nrows):
            #if star is not in useful radius, omit it...
            #the 22" here is for the edge of field / physical limits of guide probe (PFGS X-stage length limit)
            #number given by Stephen Hulme
            if(rad[i] > (5.0/60-22.0/3600) or rad[i] < inner_rad):
                useme[i] = 0
            else:  #otherwise, check if there is a nearby star, within thresh distance away
                for j in range(0,nrows):
                #first cut in distance done with radius, so we don't have to compare heaps of stars (at most N^2)
                #that are obviously already too far apart from each other (i.e. only check for close pairs 
                #amongst already somewhat nearby stars, in a radial-distance sense)
                    if(rad[j] >= rad[i]-thresh and rad[j] <= rad[i]+ thresh):
                        #note the i!=j here is important
                        if(i != j and CalcDist(r[i],d[i],r[j],d[j]) < thresh):
                            #mark both as unusable, since the nearby star (j) within the threshold, 
                            #also has by definition the search star (i) as a companion (and vice versa)
                            useme[i]=0
                            useme[j]=0
            #now finally, if the mag is too bright, remove it as well 
            #We have to include bright stars in the query above
            #to allow for bright nearby stars to be removed!
            #fainter stars are not so much a problem (though could be removed if we increase max_stars and the faint_limit, 
            #albeit at quite some time penalty
            #if(m[i] < bright_limit or (r[i] <= cx1 and r[i] >= cx2)):
                #useme[i] = 0

            #remove bright stars!
            if(m[i] < bright_limit):
                useme[i] = 0

            #yellow = good candidates 
            colour="yellow"

            #These match the right or left sides, for all PA between 0 and 360 inclusive.
            #Logic is a bit of a hack, but has been tested

            #match the left side of the field:
#           if((PA == 360 or PA <= 180) and d[i]-left_y1 >= left_m*(r[i]-left_x1)):
#               useme[i] = 2 
#           elif((PA > 180 and PA != 360) and d[i]-left_y1 <  left_m*(r[i]-left_x1)):
#               useme[i] = 2 


            #match the right side of the field:
#           if(PA !=0 and PA < 180 and (d[i]-right_y1 < right_m*(r[i]-right_x1))): 
#               useme[i] = 2
#           elif((PA ==0 or PA >=180) and (d[i]-right_y1 >=  right_m*(r[i]-right_x1))):
#               useme[i] = 2

            #These equalities were all worked out by trial and error. Yuk!
            #Note the sensitivities to PA. Differences between 0 and 0.1. The PA 360 != 0, etc.
            #match the forbidden gap:
            if(PA == 180 and (d[i]-right_y1 <  right_m*(r[i]-right_x1) and d[i]-left_y1 < left_m*(r[i]-left_x1))):
                #print "PA=180"
                useme[i] = 0
            elif((PA == 0 or PA==360)and ((d[i]-right_y1 <= right_m*(r[i]-right_x1) and d[i]-left_y1 <= left_m*(r[i]-left_x1)))):
                #print "PA=0 or 360"
                useme[i] = 0
            elif(PA !=0 and PA < 180 and d[i]-right_y1 >=  right_m*(r[i]-right_x1) and d[i]-left_y1 <= left_m*(r[i]-left_x1)):
                #print "PA<180"
                useme[i] = 0
            elif(PA != 360 and PA > 180 and d[i]-right_y1 <=  right_m*(r[i]-right_x1) and d[i]-left_y1 >= left_m*(r[i]-left_x1)):
                #print "PA>180"
                useme[i] = 0

            #red == excluded candidate guide star     
            if(useme[i] is 0):
                colour="red"
            #cyan is used for testing purposes 
            if(useme[i] is 2):
                colour="cyan"

            #write the star out to the region file, with the colour reflecting whether it passed the above 
            #tests or not. Note the *actual* best guide stars are only selected below from these candidates.
            rline = "circle %.6fd %.6fd 2\" #text={%.2f} color=%s\n" % (r[i],d[i],m[i],colour)
            reg.write(rline)

            #choose the best candidates for either side...
            #one could also try to identify the most isolated guide star, but in practice this is better done
            #by increasing the thresh value above to say 30 or 40 arcsec.
            best_left = -1
            best_right = -1
            #go through all the stars and find the first useful one (useme[i] == 1)
            #note that since the lists are arranged with brightest stars first (thanks to our clever query syntax above), those
            #will be picked preferentially over fainter stars
            #these loops won't take too long, as we break out of them once the best star has been identified
            #the search for each star is done separately and should stay that way, so that one break statement 
            #does not interfere and interrupt the search for the other one

            #Choose best guide stars for case of RSS only
            #Again, these equalities were all worked out by trial and error. Yuk!
            if(not IsHRS):
                for i in range(0,nrows):
                    #match the left side of the field:
                    if(useme[i] is not 0 and (PA == 360 or PA <= 180) and d[i]-left_y1 >= left_m*(r[i]-left_x1)):
                        best_left = i
                        break
                    elif(useme[i] is not 0 and (PA > 180 and PA != 360) and d[i]-left_y1 <  left_m*(r[i]-left_x1)):
                        best_left = i
                        break
                for i in range(0,nrows):
                    #match the right side of the field:
                    if(useme[i] is not 0 and PA !=0 and PA < 180 and (d[i]-right_y1 < right_m*(r[i]-right_x1))): 
                        best_right = i
                        break
                    elif(useme[i] is not 0 and (PA ==0 or PA >=180) and (d[i]-right_y1 >=  right_m*(r[i]-right_x1))):
                        best_right = i
                        break
            #If we have the case of HRS only
            if(IsHRS):
                #We use the 'right' star for HRS (left will be left blank/null/whatever).

                #Note the inner excluded radius (inner_radius) is larger for HRS (as a precaution for the sky fibre position)
                #That can be changed above.
                #The following chooses the first star that is not bad. 
                #It *might* choose a star in the gap, which is OK. (I haven't tested that extensively).
                #If in doubt, just select guide stars from the right side of the field, which is nicely out of the way of
                #the HRS sky fibre...

                #choose any of the good stars in the field
                for i in range(0,nrows):
                    #match the right side of the field:
                    if(useme[i] is not 0):
                        #and PA !=0 and PA < 180 and (d[i]-right_y1 < right_m*(r[i]-right_x1))): 
                        best_right = i
                        #break
                    #elif(useme[i] is not 0 and (PA ==0 or PA >=180) and (d[i]-right_y1 >=  right_m*(r[i]-right_x1))):
                    #    best_right = i
                        break

                #alternatively, choose just a star on the right side of the field (same code as above for RSS)
                #to use, uncomment this block and comment out above block
#               for i in range(0,nrows):
#                   #match the right side of the field:
#                   if(useme[i] is not 0 and PA !=0 and PA < 180 and (d[i]-right_y1 < right_m*(r[i]-right_x1))): 
#                       best_right = i
#                       break
#                   elif(useme[i] is not 0 and (PA ==0 or PA >=180) and (d[i]-right_y1 >=  right_m*(r[i]-right_x1))):
#                       best_right = i
#                       break

            #add some regions that show us which stars were chosen as the best 
            if(best_right >= 0):
                rline = "circle %.6fd %.6fd 10\" #text={best_right} width=2 color=green\n" % (r[best_right],d[best_right])
                reg.write(rline)
            if(best_left >= 0):
                rline = "circle %.6fd %.6fd 10\" #text={best_left} width=2 color=cyan\n" % (r[best_left],d[best_left])
                reg.write(rline)
            
            reg.close()
            
            #return empty values if error  
            #None for python
            #headings for table in database ra, dec, gmag, imag
            #one list of two elements, with elements having ra,dec,gmag,0 entries
            #None for cases when guide star not identified
            return (r[best_left],d[best_left],m[best_left],r[best_right],d[best_right],m[best_right])

        #if we find no stars in the field, return 0 (or some other error value)
        else: 
            return 0


#credentials to connect to science database
	
sqluser=''
sqldb=''
sqlhost=''
sqlpasswd=''
con = MySQLdb.connect(user=sqluser,db=sqldb,host=sqlhost,passwd=sqlpasswd)
cur = con.cursor()

#NGC1360 = 78881
#Hen2-113 = 78107

#read the block_id from the command line arg to the script

block_id = sys.argv[1]
PA = float(sys.argv[2])
#Note that we must require 0 <= PA <= 360
#This could probably be moved to the get_stars function
if(PA > 360.0):
    PA=PA-360.0
if(PA < 0):
    PA=PA+360.0

#select target name and coords from the science database
qtxt="SELECT tg.Target_Name, tc.RaH,tc.RaM,tc.RaS,tc.DecSign,tc.DecD,tc.DecM,tc.DecS from Block join Pointing using (Block_Id) join Observation using (Pointing_Id) join Target as tg using (Target_Id) join TargetCoordinates as tc using (TargetCoordinates_Id) where Block_Id=%s" % block_id

IsHRS=IsBlockHRS(cur,block_id)
print "Block is HRS? %d" % (IsHRS)

#execute query and process results
cur.execute(qtxt)
results = cur.fetchall()
nrows = cur.rowcount
print "block_id=%s" % block_id

if(nrows > 0):
	for data in results:
        #target name
		name = data[0]
        #coords
		rh = float(data[1])
		rm = float(data[2])
		rs = float(data[3])
		sign = data[4]
		dd = float(data[5])
		dm = float(data[6])
		ds = float(data[7])
		name = re.sub(" *$","",name)
        #put coords into decimal degrees
   		ra_deg=(rh*1.0+ rm*1.0/60 +rs*1.0/3600)*15.0
   		dec_deg = (dd + dm*1.0/60 + ds*1.0/3600) 
		if("-" in sign): 
			dec_deg *= -1.0;
		print "%s %.6f %.6f" % (name,ra_deg,dec_deg)
        #get the guide stars we need from GAIA DR2 catalogue
        #NOTE: at the moment - not doing anything with return values from the function
        #These should be added to OCS tables with some extra SQL code...
		get_stars(ra_deg,dec_deg,PA,IsHRS)
        #now write to temporary OCS tables (database), then TCS can pick up on them...
        #TODO
        #this allows us to visualise the results of get_stars
        #loads up dss image of field (magic!) and the region file containing the selected guide stars and candidate guide stars
		cmd = "ds9 -dsseso \"%.0f:%.0f:%.2f %s%.0f:%.0f:%.2f\" -geometry 1400x1200+50+0 -zoom 2 -regions stars.reg -scale mode 99.0 -match frame wcs -rotate %.2f -zoom to 1.9" % (rh,rm,rs,sign,dd,dm,ds,PA)
        os.system(cmd) 
        #if needed, one can also load up the gaia catalogue into ds9 directly, to compare against those we have filtered out above, e.g.  #cmd = "ds9 -dsseso \"%.0f:%.0f:%.2f %s%.0f:%.0f:%.2f\" -catalog cds I/345/gaia2 -catalog filter '\$Gmag >= 13 && \$Gmag <= 17' -regions stars.reg" % (rh,rm,rs,sign,dd,dm,ds)
#close connection to database
cur.close()
