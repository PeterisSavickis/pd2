# import library
import requests
import json
import datetime
import time
import yaml
import logging
import logging.config

from datetime import datetime
from configparser import ConfigParser

# Loading logging configuration
with open('./log_worker.yaml', 'r') as stream:
    log_config = yaml.safe_load(stream)

logging.config.dictConfig(log_config)

# Creating logger
logger = logging.getLogger('root')

# Print text
logger.info('Asteroid processing service')

# Initiating and reading config values
logger.info('Loading configuration from file')

# Try-Except block
try:
	# Initialise configParser library
	config = ConfigParser()
	# Read the config file
	config.read('config.ini')

	# Use configParser library to get NASA API key and URL
	nasa_api_key = config.get('nasa', 'api_key')
	nasa_api_url = config.get('nasa', 'api_url')
except:
	#Log exception message
	logger.exception('')
# Prints DONE when API KEY and URL is saved in variables
logger.info('DONE')

# Getting todays date
dt = datetime.now()
# Format date in format yyyy-mm-dd
request_date = str(dt.year) + "-" + str(dt.month).zfill(2) + "-" + str(dt.day).zfill(2)
# Print out formated todays date
logger.debug("Generated today's date: " + str(request_date))

# Print out Request url with header parameters with start date, end date and api key
logger.debug("Request url: " + str(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key))
# Do the REST callout to NASA API
r = requests.get(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key)

# Print response status - 200 if everything went ok
logger.debug("Response status code: " + str(r.status_code))
# Print received headers
logger.debug("Response headers: " + str(r.headers))
# Print response text you receive from NASA API
logger.debug("Response content: " + str(r.text))

# Only perform action if the response is 200 - everything is good
if r.status_code == 200:

	# Format the response as JSON
	json_data = json.loads(r.text)
	# Array of safe asteroids
	ast_safe = []
	# Array of dangerous asteroids
	ast_hazardous = []

	# is there any data in response
	if 'element_count' in json_data:
		# Write in variable how many asteroids there are today
		# It gets element_count part value from the JSON response array
		ast_count = int(json_data['element_count'])
		# Print how many asteroids there were today
		# Force cast ast_count as string to print it out
		logger.info("Asteroid count today: " + str(ast_count))

		# Check if there are asteroids
		if ast_count > 0:
			# Loop through near eart object in reponse
			for val in json_data['near_earth_objects'][request_date]:
				# Check if there is all the information need form the astroid
				if 'name' and 'nasa_jpl_url' and 'estimated_diameter' and 'is_potentially_hazardous_asteroid' and 'close_approach_data' in val:
					# Assign temp variable with asteroids name
					tmp_ast_name = val['name']
					# Assign temp variable with URL
					tmp_ast_nasa_jpl_url = val['nasa_jpl_url']
					# Check if it kas kilometers in estimated diameter
					if 'kilometers' in val['estimated_diameter']:
						# Check if ther is min and max in estimated diameter
						if 'estimated_diameter_min' and 'estimated_diameter_max' in val['estimated_diameter']['kilometers']:
							# Assign min and max values in temp variables
							tmp_ast_diam_min = round(val['estimated_diameter']['kilometers']['estimated_diameter_min'], 3)
							tmp_ast_diam_max = round(val['estimated_diameter']['kilometers']['estimated_diameter_max'], 3)
						# If ther is no min and max values assign bot values with -2
						else:
							tmp_ast_diam_min = -2
							tmp_ast_diam_max = -2
					# Assign min and max values -1 if there is no estimated diameter
					else:
						tmp_ast_diam_min = -1
						tmp_ast_diam_max = -1

					# Assign boolean if the asteroid is hazardous
					tmp_ast_hazardous = val['is_potentially_hazardous_asteroid']

					# Check if there is close apreach data
					if len(val['close_approach_data']) > 0:
						# Check if there is needed aproach, velocity and distance data
						if 'epoch_date_close_approach' and 'relative_velocity' and 'miss_distance' in val['close_approach_data'][0]:
							# Assign temp variables with checked data
							tmp_ast_close_appr_ts = int(val['close_approach_data'][0]['epoch_date_close_approach']/1000)
							tmp_ast_close_appr_dt_utc = datetime.utcfromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
							tmp_ast_close_appr_dt = datetime.fromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')

							# Check if there is needed data in close aproach data
							if 'kilometers_per_hour' in val['close_approach_data'][0]['relative_velocity']:
								# Assign Speed data km per hour
								tmp_ast_speed = int(float(val['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']))
							# If there is no speed data assign speed to -1
							else:
								tmp_ast_speed = -1

							# Check if there is kilometers in in the resposne
							if 'kilometers' in val['close_approach_data'][0]['miss_distance']:
								# Assign the distacne if there is data
								tmp_ast_miss_dist = round(float(val['close_approach_data'][0]['miss_distance']['kilometers']), 3)
							# Assign distance variable to -1 if there is no data
							else:
								tmp_ast_miss_dist = -1
						# Set variables to invalid values if there are no valid data in reponse
						else:
							tmp_ast_close_appr_ts = -1
							tmp_ast_close_appr_dt_utc = "1969-12-31 23:59:59"
							tmp_ast_close_appr_dt = "1969-12-31 23:59:59"
					# Set variables to invalid values if there are no valid data in response
					else:
						logger.debug("No close approach data in message")
						tmp_ast_close_appr_ts = 0
						tmp_ast_close_appr_dt_utc = "1970-01-01 00:00:00"
						tmp_ast_close_appr_dt = "1970-01-01 00:00:00"
						tmp_ast_speed = -1
						tmp_ast_miss_dist = -1

					# Print asteroid info 
					logger.info("------------------------------------------------------- >>")
					logger.info("Asteroid name: " + str(tmp_ast_name) + " | INFO: " + str(tmp_ast_nasa_jpl_url) + " | Diameter: " + str(tmp_ast_diam_min) + " - " + str(tmp_ast_diam_max) + " km | Hazardous: " + str(tmp_ast_hazardous))
					logger.info("Close approach TS: " + str(tmp_ast_close_appr_ts) + " | Date/time UTC TZ: " + str(tmp_ast_close_appr_dt_utc) + " | Local TZ: " + str(tmp_ast_close_appr_dt))
					logger.info("Speed: " + str(tmp_ast_speed) + " km/h" + " | MISS distance: " + str(tmp_ast_miss_dist) + " km")
					
					# Adding asteroid data to the corresponding array
					if tmp_ast_hazardous == True:
						ast_hazardous.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])
					else:
						ast_safe.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])

		else:
			logger.info("No asteroids are going to hit earth today")

	# Print info about counted hazardous and safe asteroids
	logger.info("Hazardous asteorids: " + str(len(ast_hazardous)) + " | Safe asteroids: " + str(len(ast_safe)))

	# Check if there are hazardous asteroids
	if len(ast_hazardous) > 0:

		# Sort the hazardous asteroids ASC based on 4th index
		ast_hazardous.sort(key = lambda x: x[4], reverse=False)

		# Print info about todays hazardous asteroids
		logger.info("Today's possible apocalypse (asteroid impact on earth) times:")
		# Loop through hazardous asteroids and print info about them
		for asteroid in ast_hazardous:
			logger.debug(str(asteroid[6]) + " " + str(asteroid[0]) + " " + " | more info: " + str(asteroid[1]))

		#Sort hazardous asteroids ASC based on 8th index
		ast_hazardous.sort(key = lambda x: x[8], reverse=False)
		# Print info about hazardous asteroid distance 
		logger.info("Closest passing distance is for: " + str(ast_hazardous[0][0]) + " at: " + str(int(ast_hazardous[0][8])) + " km | more info: " + str(ast_hazardous[0][1]))
	else:
		# If there are no hazardous asteroids passing by print safe message
		logger.info("No asteroids close passing earth today")

else:
	# Print exception message if the is no response from the API
	logger.exception("Unable to get response from API. Response code: " + str(r.status_code) + " | content: " + str(r.text))
