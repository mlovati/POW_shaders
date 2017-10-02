PR = 0.8
efficiency = 0.16
epwpath = "trial.epw"
width_m = 0.9
height_w = 6
width_w = 4
orientation_w = 0
n_strings = 3
import math
import subprocess
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
maxmodules = math.floor(height_w / width_m)
heightlist =[]
for i in range(1,maxmodules+1):
	heightlist.append(height_w/i)

class surface():
	def __init__(self, name, p1 =[0,0,0],p2=[1,0,0],p3=[1,1,0],p4=[0,1,0]):
		self.name = name
		self.p1 = p1
		self.p2 = p2
		self.p3 = p3
		self.p4 = p4
		self.mpoints = []
		self.ipoints = []
		self.mvectors = []
		self.ivectors = []
	def makeipoints(self, heig):
		nopoints = 5
		unit = heig/(2*nopoints)
		heilist = [(i+1) for i in range(0,2*nopoints,2)]
		for i in range(0,nopoints):
			self.ipoints.append([self.p2[0]/2,(self.p3[1]+0.025),(self.p3[2]+(unit*heilist[i]))])
			self.ivectors.append([0,-1,0])
		return
	def makempoints(self,nostrings = 3): #as setdimensions this command should be applied before move or rotate
		#this command should be run after makedimensions
		multiplist = [(i+1) for i in range(0,2*nostrings,2)]
		for i in range(0,nostrings):
			self.mpoints.append([self.p2[0]/2,(self.p4[1]/(nostrings*2))*(multiplist[i]), 0.025])
			self.mvectors.append([0,0,1])
		return
	def listattr(self):
		return [self.p1,self.p2,self.p3,self.p4]
	def setdimensions(self,x,y): # this method gives the dimensions at the surface but renders it horizontal
		#it loses every rotation or movement
		self.p1 =[0,0,0]
		self.p2 = [x,0,0]
		self.p3 = [x,y,0]
		self.p4 = [0,y,0]
		return 
	def move(self,vector):
		pointlist = self.listattr()
		pointlist.extend(self.mpoints)
		for i in pointlist:
			for j in range(0,len(i)):
				i[j] += vector[j]
		return 
	def rotate(self,angle,axis):
		pointlist = self.listattr()
		pointlist.extend(self.mpoints + self.mvectors)
		#pointlist.extend(self.mvectors)
		if axis =="x":
			coords =[1,2]
		if axis =="y":
			coords =[2,0]
		if axis =="z":
			pointlist.extend(self.ipoints + self.ivectors)
			#pointlist.extend(self.ivectors)
			coords =[0,1]
		for i in pointlist:
			new0 = i[coords[0]]* math.cos(math.radians(angle))-(i[coords[1]]* math.sin(math.radians(angle)))
			new1 = i[coords[0]]* math.sin(math.radians(angle))+(i[coords[1]]* math.cos(math.radians(angle)))
			i[coords[0]] = new0
			i[coords[1]] = new1
		return
	def writeobj(self,file,position = 0): #this method exports in a format that can  be read by most CAD but is not necessary for the simulation 
		file.write("o " +str(self.__dict__["name"])+ "\n")
		for i in self.listattr():
			file.write("v ")
			for j in i:
				file.write(str(j)+" ")
			output.write("\n")
		if position == 0:
			file.write("f 1 2 3 4")
		else:
			file.write("f 5 6 7 8")
		file.write("\n")
		return
	def writerad(self,file,position = 1):
		file.write("contextmat polygon "+str(self.__dict__["name"])+"."+str(position)+"\n")
		file.write("0"+"\n"+"0"+"\n"+"12"+"\n")
		for i in self.listattr():
			for j in i:
				for k in range(0,18-len(str(j))):
					file.write(" ")
				file.write(str(j)+ " ")
			file.write("\n")
		return
	def writepts(self):
		pts = open("points.pts","w")
		plist = self.mpoints + self.ipoints
		vlist = self.mvectors + self.ivectors
		for a in range(0,len(plist)):
			for b in range(0,len(plist[a])):
				pts.write(str(plist[a][b])+" ")
			for b in range(0,len(plist[a])):
				pts.write(str(vlist[a][b])+" ")
			pts.write("\n")

def writesystem(tilt,height, nostrings = 3):
	global output
	# output = open("surfaces.obj","w")
	output = open("surf.rad","w")
	over = surface("over")
	over.setdimensions(width_w,width_m)
	over.rotate(tilt,"x")
	over.rotate(orientation_w,"z")
	under = surface("under")
	under.setdimensions(width_w,width_m)
	under.makempoints(nostrings)
	under.rotate(tilt,"x")
	under.makeipoints(heightlist[height])
	under.rotate(orientation_w,"z")
	over.move([0,0,heightlist[height]])
	under.writepts()
	over.writerad(output,1)
	under.writerad(output,2)
	output.close()
	# output.write("g surfaces" + "\n")
	# over.writeobj(output,0)
	# under.writeobj(output,1)
	# objrad = subprocess.Popen(r"obj2rad -m C:\Users\Marco\Documents\usedaysim\design\surfaces.map C:\Users\Marco\Documents\usedaysim\design\surfaces.obj > C:\Users\Marco\Documents\usedaysim\design\surfaces.rad", shell = True)
	return

def tolines(filename):
	raw = open(filename,"r")
	raw2 = raw.read()
	lines = raw2.split("\n")
	return lines

def updatefiles():
	lines = tolines(epwpath)
	localinfo = lines[0].split(",")
	global place,latitude,longitude,time_zone,site_elevation 
	place,latitude,longitude,time_zone,site_elevation = localinfo[1], localinfo[6],str(-float(localinfo[7])),str(-15*float(localinfo[8])),localinfo[9]
	lines = tolines("blueprint.hea")
	epwdict = dict( (name,eval(name)) for name in ["place","latitude","longitude","time_zone","site_elevation"] )
	header = open("header.hea","w")
	for i in range(0,len(lines)-1):
		if "#" not in lines[i].split(" ")[0]:
			if lines[i].split(" ")[0] in epwdict.keys():
				header.write(lines[i].split(" ")[0])
				for j in range(0,lines[i].count(" ")):
					header.write(" ")
				header.write(epwdict[lines[i].split(" ")[0]] + "\n")
			else:
					if "sensor_file_unit" in lines[i].split(" ")[0]:
						header.write("sensor_file_unit")
						for j in range(0,lines[i].count(" ")-1):
							header.write(" ")
						for j in range(0,n_strings+5):
							header.write("2 ")
						header.write("\n")
					elif "project_directory" in lines[i].split(" ")[0]:
						header.write("project_directory")
						for j in range(0,lines[i].count(" ")-1):
							header.write(" ")
						header.write(dir_path+ "\\" +"\n")
					elif "tmp_directory" in lines[i].split(" ")[0]:
						header.write("tmp_directory")
						for j in range(0,lines[i].count(" ")-1):
							header.write(" ")
						header.write(dir_path+"\\tmp\\"+ "\n" )
					else:
						header.write(str(lines[i])+"\n")
		else:
			header.write(str(lines[i])+"\n")
	header.write(lines[-1])
	header.close()
	trigger = tolines("dscommands.bat")
	epwtrig = trigger[0].split(" ")[1]
	batfile = open("dscommands.bat","w")
	batfile.write("epw2wea "+ epwpath +" trial.wea"+"\n")
	for i in range(1,len(trigger)-1):
		batfile.write(trigger[i]+"\n")
	batfile.write(trigger[-1])
	batfile.close()
	return

def readfitness(height):
	illfile = tolines("result.ill")
	illframe = []
	for i in range(0,len(illfile)-1):
		illframe.append(illfile[i].split(" ")[4:])
	singlehoy= [[] for i in illframe[0]]
	for a in range(0,len(illframe)):
		for b in range (0,len(illframe[a])):
			singlehoy[b].append(float(illframe[a][b]))
	pvs = singlehoy[:n_strings] # this dataframe is of type [position][hoy]
	gains = singlehoy[n_strings:]
	pows = []
	#the following code simply simulates the bypass diode, input: dataframe[position][hoy]
	for a in range(0,len(pvs[0])):
		irradiations = []
		for b in range(0,len(pvs)):
			irradiations.append(pvs[b][a])
		irradiations = sorted(irradiations)
		potpows = []
		for b in range(0,len(irradiations)):
			potpows.append(irradiations[b]*(len(irradiations)-b)*((width_m*width_w)/len(pvs))*efficiency*PR/1000)
		potpows = sorted(potpows)
		pows.append(potpows[-1])
	PVpow = sum(pows) #annual cumulative power of a single module in the array [kWh]
	totpow = PVpow* height_w/heightlist[height]
	hch = tolines("hch.dat") #is 1 in cooling hour
	if len(hch[-1]) ==0:
		hch.pop(-1)
	# hch = [] #hch stands for heating cooling hour
		# for unnoo in lines:
			# hch.append(unnoo)
	goodness = 0
	for i in range(0,len(hch)):
		totgain= []
		for j in range(0,len(gains)):
			totgain.append(gains[j][i])
		if float(hch[i]) == 0:
			goodness += (sum(totgain)/len(gains))/1000
		else:
			goodness -= (sum(totgain)/len(gains))/1000
	gainindex = goodness
	return PVpow,totpow,gainindex

print(len(heightlist))
outputt = open("output.csv","w")
updatefiles() #check if you can move it out
outputt.write("angle	distance	nomodules	PV	PVtot	gain"+"\n")
for hei in range(0,len(heightlist)):
	for ang in range(0,100,10):
		writesystem(ang,hei,n_strings)
		subprocess.call("dscommands.bat")
		PV,PVtot,gain = readfitness(hei)
		#print(PV,gain)
		outputt.write(str(ang)+"	"+str(heightlist[hei])+"	"+str(height_w/heightlist[hei])+"	"+str(PV)+"	"+str(PVtot)+"	"+str(gain)+"\n")