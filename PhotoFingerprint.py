from PIL import Image
import os
import sqlite3
import hashlib
import sys

# The following sets up a menu type environment and does some DB QA init. work.
menu = 0
while menu == 0:
	print "1. Scan images and compare against database."
	print "2. Load image signatures into database."
	choice = raw_input()
	if choice == "1":
		execute = "scan"
		menu = 1
	if choice == "2":
		execute = "load"
		menu = 1
	if choice != 1 or 2:
		os.system('cls')

print "Please enter absolute path to the database file."
db = raw_input("If you have not created a database, enter absolute path to new database: ")
if os.path.isfile(db):
	new = 0
else:
	new = 1
conn = sqlite3.connect(db)
cur = conn.cursor()
if new == 1:
	cur.execute("CREATE TABLE main(p_key INTEGER PRIMARY KEY, md5 TEXT, sha1 TEXT, sig TEXT)")
os.system('cls')

#Opening image file and getting total X, Y pixel counts.
def getQuadPX(imgObject):
	img = Image.open(imgObject)
	PX = img.load()
	aspect = img.size
	xC = aspect[0]/10
	yC = aspect[1]/10
	return(xC, yC)
	
# This function returns a list of ranges of the 100 quadrants consisting of the image.
# It's output is generally fed to the getAllQuadPXDict function.
def getQuadRanges(xAxis, yAxis):
	listObj = []
	for x in range(0, 10):
		xRng = str((xAxis*(x+1))-xAxis)+"_"+str(xAxis*(x+1))
		for y in range(0, 10):
			yRng = str((yAxis*(y+1))-yAxis)+"_"+str(yAxis*(y+1))
			listObj.append(xRng+":"+yRng)
	return(listObj)

# xbCord = x axis beginning coordinate, xeCord = x axis ending coordinate, etc.
# Returns list object containing all coordinate pairs given range of X and Y coordinate beginning/end values.
# Primarily for use in the getAllQuadPXDict function.
def getQuadPXList(xbCord, xeCord, ybCord, yeCord):
	listObj = []
	for x in range(xbCord, xeCord):
		for y in range(ybCord, yeCord):
			listObj.append(str(x)+','+str(y))
	return(listObj)

# This function takes all quadrant ranges as a list, and create a dictionary containing all the quadrants as keys, with all possible X, Y coordinates as the value in a list for each respective key.
# Intended to take the output of the getQuadRanges iteratively as input, and then utilizes the getQuadPXList function on the ranges provided by the aforementioned function.
def getAllQuadPXDict(QuadRangesList):
	cnt = 0
	dictObj = {}
	for quad in QuadRangesList:
		xyRng = quad.split(':')
		xRng = xyRng[0].split('_')
		yRng = xyRng[1].split('_')
		qPXList = getQuadPXList(int(xRng[0]), int(xRng[1]), int(yRng[0]), int(yRng[1]))
		dictObj['q'+str(cnt)] = qPXList
		cnt+=1
	return(dictObj)

# This function takes the coordinates from a list of quadrant coordinates, and returns the RGB values in a list.
# Primarily for use in the getAllQuadRGB function.
def getQuadPX_RGB(imgObject, quadPXList):
	listObj = []
	img = Image.open(imgObject)
	rgb_img = img.convert('RGB')
	for coord in quadPXList:
		xyC = coord.split(',')
		r, g, b = rgb_img.getpixel((int(xyC[0]), int(xyC[1])))
		listObj.append(str(r)+","+str(g)+","+str(b))
	return(listObj)

# This function uses the getQuadPX_RGB function on the output of the getAllQuadPXDict function to create a dictionary object containing the RGB values of all pixel coordinates in all quadrants.
def getAllQuadRGB(AllQuadCoordsDict, imgObject):
	dictObj = {}
	for key in AllQuadCoordsDict:
		coordList = AllQuadCoordsDict[key]
		quadRGBList = getQuadPX_RGB(imgObject, coordList)
		dictObj[key] = quadRGBList
	return(dictObj)

# This function takes the dictionary object containing all quadrant pixel RGB values (created by the getAllQuadRGB function) and averages each quadrants RGB values to create an average color RGB value for that quadrant.
# It returns a dictionary object, each key referring to a quadrant and it's value being the average RGB value for that quadrant.
def calcQuadAvgs(AllRGBDict):
	dictObj = {}
	rList = []
	gList = []
	bList = []
	rTot = 0
	gTot = 0
	bTot = 0
	rAvg = 0
	gAvg = 0
	bAvg = 0
	for key in AllRGBDict:
		for RGBval in AllRGBDict[key]:
			RGBval = RGBval.split(',')
			rList.append(RGBval[0])
			gList.append(RGBval[1])
			bList.append(RGBval[2])
		for rval in rList:
			rTot = rTot + int(rval)
		for gval in gList:
			gTot = gTot + int(gval)
		for bval in bList:
			bTot = bTot + int(bval)
		rAvg = rTot/len(rList)
		gAvg = gTot/len(gList)
		bAvg = bTot/len(bList)
		dictObj[key] = str(rAvg)+','+str(gAvg)+','+str(bAvg)
		rAvg=gAvg=bAvg = 0
		rTot = 0
		gTot = 0
		bTot = 0
		rList = []
		gList = []
		bList = []
		rAvg = 0
		gAvg = 0
		bAvg = 0
	return(dictObj)

# Used in calculating hashes of input image files.
def hashes(target_img):
	hash_t = open(target_img, 'rb')
	hash_b = hash_t.read()
	targ_md5 = hashlib.md5(hash_b).hexdigest()
	targ_sha1 = hashlib.sha1(hash_b).hexdigest()
	hash_t.close()
	hList = [targ_md5, targ_sha1]
	return(hList)

# Performs core function of getting pixel/quadrant information. Used for creating color signatures of images used for comparison and entry into database.
def core(target_img):
	img_XY = getQuadPX(target_img)
	QuadRanges = getQuadRanges(int(img_XY[0]), int(img_XY[1]))
	allQuadPXCoords = getAllQuadPXDict(QuadRanges)
	dictAllRGB = getAllQuadRGB(allQuadPXCoords, target_img)
	avgAllQuadRGB = calcQuadAvgs(dictAllRGB)
	return(avgAllQuadRGB)

	
def dbQuadFormatToDict(dbDATA):
	dictObj = {}
	dbQuadList = dbDATA.split(";")
	for krgb in dbQuadList:
		k_rgb = krgb.split(":")
		k = k_rgb[0]
		rgb = k_rgb[1]
		rgbs = rgb.replace("-", ",")
		dictObj[k]=rgbs
	return(dictObj)
	
# Takes a signature quadrant set from a database, compares against a signature quadrant set calculated of an image and determines match based on threshold.
def comp(srcHash, srcRGB, dbDATA):
	dbHASH = str(dbDATA.split("+")[1].strip())
	dbQuads = str(dbDATA.split("+")[0].strip())
	dbRGB = dbQuadFormatToDict(dbQuads)
	srcMD5 = str(srcHash[0]).strip()
	#255 to 100 % normalization value.
	const = float(.3921568)
	# Why do the work if MD5 hashes match.
	if srcMD5 == dbHASH:
		print 'HASH MATCH!'
		print dbHASH
		print srcMD5
		total_diff = 0
	else:
		# Begin comparing quadrants. Takes each quadrant via iteration, splits up the RGB values, normalizes determines spread in for each RGB value per quadrant compare, the normalizes them from a 0-255 to a 0-100 scale using a const. 255>100 value via multiplication, then averages the 100 scale normalized differences in RGB values and feeds that total RGB difference percent to quad_comp_percs list. This list is then average to give us a total percent difference.
		quad_comp_percs = []
		for src_key in srcRGB:
			src_rgb_l = srcRGB[src_key].split(',')
			db_rgb_l = dbRGB[src_key].split(',')
			rgb_comp_res = []
			for ind, srcVal in enumerate(src_rgb_l):
				dbVal = int(db_rgb_l[ind])
				srcVal = int(srcVal)
				if dbVal > srcVal:
					percD = int((dbVal-srcVal)*const)
				if dbVal < srcVal:
					percD = int((srcVal-dbVal)*const)
				if dbVal == srcVal:
					percD = 0
				rgb_comp_res.append(percD)
			quad_diff = int(sum(rgb_comp_res)/3)
			quad_comp_percs.append(int(quad_diff))
		total_diff = int(sum(quad_comp_percs)/100)
	return(total_diff)

def scanExecute(execute):
	if execute == "scan":
		# When we call the script, we need to have an image file made available, here I use raw_input() to take a path from a user, but this should take some sort of sysarg in the future for portability.
		target_dir = raw_input('Please enter absolute path to directory containing images to be scanned: ')
		tol = raw_input('Please enter a tolerance level for matches.\nIE, enter 10 to only show images with matches 10% or less.\n: ')
		try:
			tol = int(tol)
		except:
			print 'Invalid tolerance input, exiting.'
			sys.exit(1)
		
		# Do some QA and get info on input directory
		if target_dir.endswith("\\"):
			pass
		else:
			target_dir = target_dir+"\\"
		targ_list = os.listdir(target_dir)

		# Populate comparison DB quad data from DB into list.
		dbData = cur.execute("SELECT * FROM main")
		db_rgb_vals = []
		for row in dbData:
			db_rgb_vals.append(str(row[3])+"+"+str(row[1]))
			
		# Fire off the loop
		for target in targ_list:
			# Read in DB for comparisons.
			target_img = target_dir+target
			if target_img.endswith("jpg") or target_img.endswith("jpeg") or target_img.endswith("png") or target_img.endswith("bmp"):
				print "Current target is "+str(target)
				hashRes = hashes(target_img)
				coreOut = core(target_img)
				for db_item in db_rgb_vals:
					comp_diff_val = int(comp(hashRes, coreOut, db_item))
					if comp_diff_val < tol:
						print str(comp_diff_val)+" percent difference."

def loadExecute(execute):
	if execute == "load":
		# The next bit of code is the same as the above in the previous IF. Setup our Dirs and preform QA, except instead of scanning images in a directory, we're loading the images specified in our directory to the DB for future comparisons.
		target_dir = raw_input('Please enter absolute path to directory containing images to be loaded: ')
		
		# Do some QA and get info on input directory
		if target_dir.endswith("\\"):
			pass
		else:
			target_dir = target_dir+"\\"
		targ_list = os.listdir(target_dir)
		
		# More input QA, fire off the loop, again, the same, except lets shove the output into the DB.
		for target in targ_list:
			target_img = target_dir+target
			if target_img.endswith("jpg") or target_img.endswith("jpeg") or target_img.endswith("png") or target_img.endswith("bmp"):
				hashRes = hashes(target_img)
				coreOut = core(target_img)
				# Load color signatures and hash information into comparison database.
				keyStr = ""
				for key in coreOut:
					keyStr = keyStr + key+":"+coreOut[key] + ";"
				keyStr = keyStr.replace(",", "-")
				print keyStr
				print "MD5: "+hashRes[0]+" SHA1: "+hashRes[1]
				cur.execute("INSERT INTO main (md5, sha1, sig) VALUES ('"+str(hashRes[0])+"','"+hashRes[1]+"','"+str(keyStr)[0:-1]+"')")
				conn.commit()

loadExecute(execute)
scanExecute(execute)

conn.close()

# The following code simply creates a new image showing an example of the average color of each quadrant of an input image. Commented out, only for testing purposes.
#nimgXY = str(img_XY[0]*10)+','+str(img_XY[1]*10)
#nimgXY = nimgXY.split(',')
#print type(nimgXY)
#print nimgXY
#nimg = Image.new("RGB", (int(nimgXY[0]), int(nimgXY[1])))
#for key in avgAllQuadRGB:
	#for PX in allQuadPXCoords[key]:
		#RGBval = avgAllQuadRGB[key].split(',')
		#PX = PX.split(',')
		#nimg.putpixel((int(PX[0]), int(PX[1])), (int(RGBval[0]), int(RGBval[1]), int(RGBval[2])))
#nimg.save(target_img[0:target_img.rfind('.')]+"AVGOUT.jpg")