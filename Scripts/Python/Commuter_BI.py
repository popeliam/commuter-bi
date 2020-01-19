import requests
import datetime as dt
import time
import json
import psycopg2
import re
import Sheets.dsUpdate as update

key = 'YOUR-API-KEY'
url = 'https://maps.googleapis.com/maps/api/directions/json?'
conn = psycopg2.connect(host='localhost',database='postgres',user='postgres',password='password')

def getCommutes():
	cur = conn.cursor()
	cur.execute('''
	SELECT commute_id,from_lat_long,to_lat_long 
	FROM commutes
	WHERE is_active 
		AND start_time <= current_time
		AND stop_time >= current_time
	''')
	commutes=cur.fetchall()
	cur.close()
	return commutes

def getWeather(c1,c2):
	try:
		url = 'https://api.weather.gov/points/'
		latitude = (float(re.split(',',c1)[0]) + float(re.split(',',c2)[0]))/2 #retrieve weather for the midpoint of the origin and destination
		longitude = (float(re.split(',',c1)[1]) + float(re.split(',',c2)[1]))/2
		loc = requests.get(url+str(latitude)+','+str(longitude)).json()['properties']['forecastHourly']
		summary = requests.get(loc).json()["properties"]["periods"][0]["shortForecast"] #immediate forecast, same hour as request is made
		return summary
	except:
		return 'No Weather Available'

def req(o,d):
	global url,key
	reqUrl = '{}origin={}&destination={}&departure_time=now&key={}'.format(url,o,d,key)
	return requests.get(reqUrl).json()

def waypointsGen(n): #step-level rows: latitude, longitude, distane, formatted directions
	return [n['start_location']['lat'],n['start_location']['lng'],n['distance']['value'],' '.join(list(map(sliceBold,re.findall('<b>.*?</b>',n['html_instructions']))))]

def sliceBold(n):
	return n[3:len(n)-4]

def main():
	print("Run ",dt.datetime.now())
	try:
		commutes = getCommutes()
		cur = conn.cursor()
		#print(commutes)
		for i in commutes:
			trip_steps = []
			step_num = 1
			trip_id = i[0]+'_'+str(int(dt.datetime.utcnow().timestamp()))
			data = req(i[1],i[2])
			weather = getWeather(i[1],i[2])
			waypoints = list(map(waypointsGen,data['routes'][0]['legs'][0]['steps']))
			waypoints.append([data['routes'][0]['legs'][0]['steps'][0]['end_location']['lat'],data['routes'][0]['legs'][0]['steps'][0]['end_location']['lng'],0,'arrive']) #add destination as final waypoint in the trip
			for n in waypoints:
				n += [trip_id,step_num]
				trip_steps.append(tuple(n))
				step_num += 1
			fact = (trip_id,data['routes'][0]['summary'],str(dt.datetime.now()),data['routes'][0]['legs'][0]['duration_in_traffic']['value'],data['routes'][0]['legs'][0]['distance']['value'],i[0],weather)
			print(fact)
			cur.execute('INSERT INTO trips VALUES '+str(fact))
			for i in trip_steps:
				#print(i)
				cur.execute('INSERT INTO trip_steps VALUES '+str(i))
			time.sleep(2)
		cur.close()
		conn.commit()
		update.run() #update the google sheet for tableau
	except:
	 	print('Error!')
	 	True
	time.sleep(600-(int(dt.datetime.now().strftime('%M')) % 10)*60-int(dt.datetime.now().strftime('%S')))
	main()

if __name__ == '__main__':
	main()
