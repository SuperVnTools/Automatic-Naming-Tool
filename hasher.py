from videohash import VideoHash #version 3.0.1, later or earlier versions may make different hashes
import glob
import json
import os
import argparse

doLog=True
ignore_list=["Amagami","extras","title","backdrops"] #if these words are anywhere in the filepath it will be ignored

def hamming(x,y):
	return bin(int(x,16) ^ int(y,16)).count('1')

def create_hash(filepath):
	if doLog:
		f=open("log.txt","a+")
		f.write("starting: "+ filepath+'\n')
		f.close()
	else:
		print("starting: "+ filepath)
	hash1=VideoHash(path=filepath)
	hash1.delete_storage_path()
	return hash1.hash_hex

def find_close(hash,jason):
	a=list(jason.keys())
	for i in range(len(a)):
		if hamming(a[i],hash)<=2:#4 bit difference has been seen between unrelated videos
			return jason[a[i]]
	return -1

def create_json(out,pattern,extension=".mkv",ignore=[],recursive=True,root=""):
	#use os.path.splitext(path)[0]
	outjson={}
	recursion="**/*"+extension
	pattern=os.path.join(root,pattern,recursion).replace("\\","/")
	try:
		f=open(out,'r')
		outjson=json.loads(f.read())
		f.close()
	except:
		f=open(out,'w+')
		f.close()
	files=glob.glob(pattern,recursive=recursive)
	skip=0
	counter=0
	skip_counter=0
	for file in files:
		relative_path = os.path.relpath(file, root).replace("\\","/")
		for i in ignore:
			if i in file:
				skip=1
				skip_counter+=1
				counter-=1
				break
		if skip==0 and os.path.split(relative_path)[0] in outjson.values():
			skip=1
			skip_counter+=1
			counter-=1
		if skip==0:
			print(counter,"/",len(files)-skip_counter,str(100*counter/(len(files)-skip_counter))+"%")
			temp_hash=create_hash(file)
			if temp_hash not in out:

				outjson[temp_hash]=os.path.split(relative_path)[0]
			else:
				#this probably doesnt work
				if doLog:
					f=open("log.txt","a+")
					f.write("hash collision "+file+'\n')
					f.close()
				else:
					print("hash collision",file)
				out[temp_hash].append(os.path.split(relative_path)[0])
			f=open(out,'w')
			f.write(json.dumps(outjson))
			f.close()
		skip=0
		counter+=1
def check_json(inp,outjson):
	if inp in outjson:
		return outjson[inp]
	#later change this to check if both exist, and show both to user to choose one
	return find_close(inp,outjson)

	#a=outjson.keys()
	#min=65
	#mins=[]
	#for i in range(a):
	#	val=hamming(inp,a[i])
	#	if val<min:
	#		min=val
	#		mins=[i]
	#	if val==min:
	#		mins.append(i)
	#print("dang it")
	#print("-"*40)
	#for i in mins:
	#	print(a[i])
	#print("-"*40)
	#return a[0]

def change_name(jsonpath,pattern,outpath="",extension=".mkv",root="",recursive=True):
	f=open(jsonpath,'r')
	outjson=json.loads(f.read())
	f.close()

	recursion="**/*"+extension
	pattern=os.path.join(pattern,recursion).replace("\\","/")

	files=glob.glob(pattern,recursive=recursive)

	for file in files:
		temp_hash=create_hash(file)
		name=check_json(temp_hash,outjson)
		if name!=-1:
			#optional confirm maybe idk
			#move file to name plus root
			name=os.path.join(outpath,name)+extension
			os.makedirs(os.path.dirname(name),exist_ok=True)
			try:
				os.rename(file,name)
				if doLog:
					f=open("log.txt","a+")
					f.write(file+ " -> "+ name+'\n')
					f.close()
				else:
					print(file, "->", name)
			except:
				if doLog:
					f=open("log.txt","a+")
					f.write("file " + file + " could not be moved to " + name+'\n')
					f.close()
				else:
					print("file " + file + " could not be moved to " + name + " because " + name + " already exists")
			#possibly write to a log
		else:
			if doLog:
				f=open("log.txt","a+")
				f.write("file: " + file + " not found in hashes " + temp_hash+'\n')
				f.close()
			else:
				print("file: " + file + " not found in hashes " + temp_hash)
		

def test_bit_limit(jason):
	#4 bit difference has occured between two completely unrelated videos
	#1 bit difference occurs frequently in transcoded video
	#2 bit difference has occured in transcoded video with no embedded subtitles
	f=open(jason,'r')
	jerson=json.loads(f.read())
	f.close()
	a=list(jerson.keys())
	out=[]
	for i in range(len(a)):
		for y in range(len(a)):
			if i!=y:
				out.append(hamming(a[i],a[y]))
				#if out[-1]==9:
				#	print(jerson[a[i]],jerson[a[y]])
	return min(out)


#test_bit_limit("hashes.json")
#check_json(create_hash(r"F:\Bluray\Shows\Clannad (2007)\Season 02\Clannad S02E09.mkv"))

#create_json("hashes.json","Shows",extension=".mkv",ignore=ignore_list,root="F:/Bluray/") #good :)
#change_name(r"C:\Users\benji\OneDrive\Desktop\videohash\hashes.json","Clannad",extension=".mp4",recursive=True,root="E:/Bluray/Handbraked")

if __name__=="__main__":
	parser = argparse.ArgumentParser(prog="Video Namer", description="A program to automatically name bluray rips")
	parser.add_argument('-n', '--name',help="folder path with videos to name")
	parser.add_argument('-o','--output',help="path for videos. /E:/Blue/Shows/Show1/ the path should be /E:/Blue/",required=True)
	parser.add_argument('-c','--create',help="folder path of vidoes to create hashes of. These must be named correctly in the correct folders, ie. Shows, Title (YEAR), Season, Name SxxExx.mkv must all be correct.")
	parser.add_argument('-r','--recursive',default=True,help="True to search recursively for videos, default is true",type=bool)
	parser.add_argument('-e','--extension',required="True",help="file extension to look for or to name")
	parser.add_argument('-l','--log',default='False',type=bool,help="writes to log file")
	args=parser.parse_args()
	doLog=args.log
	if args.name!=None and args.output!=None:
		#name the files in -n to -o
		change_name("hashes.json",args.name,extension=args.extension,recursive=args.recursive,outpath=args.output)
	elif args.create!=None:
		#create hashes from -c
		create_json("hashes.json",args.create,extension=args.extension,ignore=ignore_list,root=args.output)
	else:
		parser.print_help()