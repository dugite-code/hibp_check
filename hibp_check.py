import sys
if sys.version_info[0] < 3:
	raise Exception( 'Python 3 is required to run' )

from version import __version__ as version
from version import state

import platform
import argparse
import logging
import yaml
import os
import sys
import requests
import pickle
from mako.template import Template
from mako.lookup import TemplateLookup
from bs4 import BeautifulSoup

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def compare( old, new ):
	indexes = []
	for index, breach in enumerate( new ):
		logger.debug( 'Checking: ' + breach['Name'] )
		for obreach in old:
			if ( breach['Name'] == obreach['Name'] ) and ( breach['AddedDate'] == breach['AddedDate'] ):
				logger.debug( 'Already Reported Breach: ' + breach['Name'] )
				indexes.append( index )
				break
	for index in sorted(indexes, reverse=True):
		del new[ index ]

	return new


def getbreaches( root, email ):
	logger.info( 'Fetching Breaches for: ' + email )
	r = requests.get( 'https://haveibeenpwned.com/api/v2/breachedaccount/' + email )

	filename = email.replace( '@', '_' ).replace( '.', '_' ) + '.dat'
	filepath = os.path.join( root, 'data', filename )
	logger.debug( 'Accound data store: ' + str( filepath ) )

	if ( r.status_code == 200 ):
		logger.info( 'Breaches found: ' + str( len( r.json() ) ) )
		if os.path.isfile(filepath):
			old_data = pickle.load( open( filepath, "rb" ) )
			new_data = compare( old_data, r.json() )

			if len( new_data ) > 0:
				data = old_data + new_data
				pickle.dump( data, open( filepath, "wb" ) )
				logger.debug( 'New breaches for: ' + email )
				return new_data
			else:
				logger.debug( 'No new breaches for: ' + email )
				return 'None Found'
		else:
			pickle.dump( r.json(), open( filepath, "wb" ) )
			logger.debug( 'New breaches for: ' + email )
			return r.json()

	else:
		return 'None Found'

def getrender( root, base, template_dir ):

	tmpldir = os.path.join( root, template_dir )
	logger.debug( 'Templates Directory: ' + tmpldir )

	tmpllookup = TemplateLookup( directories=[ tmpldir ] )

	base_tmpl = os.path.join( root, template_dir, base )
	logger.debug( 'Using Base Template: ' + base_tmpl )

	email_template = Template( filename = base_tmpl, lookup = tmpllookup )

	return email_template

# Modified from https://stackoverflow.com/a/27974027
def sanitize( data ):
	if not isinstance( data, ( dict, list ) ):
		return data
	if isinstance( data, list ):
		return [ v for v in ( sanitize(v) for v in data ) if v ]
	return { k: v for k, v in ( (k, sanitize( v ) ) for k, v in data.items() ) if v is not None }

# From https://stackoverflow.com/a/7205672
def mergedicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(mergedicts(dict1[k], dict2[k])))
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, dict2[k])
                # Alternatively, replace this with exception raiser to alert you of value conflicts
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])

if __name__ == '__main__':
	# Fetch root directory
	root = os.path.dirname (os.path.realpath( __file__ ) )

	congifg_file = os.path.join( root, 'config.yml' )

	parser = argparse.ArgumentParser()
	parser.add_argument( '-v', '--version',
							dest='version',
							action='store_true',
							default=False,
							help='Print Version Number' )
	parser.add_argument( '-q', '--quiet',
							dest='quiet',
							action='store_true',
							default=False,
							help='Disable console output' )
	parser.add_argument( '-c', '--configuration',
							dest='config_file',
							default=congifg_file,
							help='Specify a different config file' )
	parser.add_argument( '-n', '--no-email',
							dest='nemail',
							action='store_true',
							default=False,
							help='Disable email output' )
	parser.add_argument( '-d', '--delete-data',
							dest='ddata',
							action='store_true',
							default=False,
							help='Delete saved breach data' )

	args = parser.parse_args()

	if args.version:
		print( 'Version: ' + version + ' - ' + state )
		exit()

	# Set default configuration options
	cfg_default = { 'Logging Settings' : {
						'Level' : 'WARNING',
						'Log to Console' : True,
						'Log to File' : False,
						'Logfile' : 'hibp.log'
						} }

	# Load the configuration yaml file
	with open( args.config_file, 'r' ) as ymlfile:
		cfg_file = yaml.safe_load( ymlfile )

	cfg_user = sanitize( cfg_file )

	config = dict( mergedicts(cfg_default,cfg_user) )

	del cfg_default
	del cfg_user

	# Set up Logging
	logger = logging.getLogger( __name__ )

	log_file = os.path.join( root, config['Logging Settings']['Logfile'] )

	# Set Log Level
	level = logging.getLevelName( config['Logging Settings']['Level'] )
	logger.setLevel( level )

	# Create a logging format
	formatter = logging.Formatter( '%(asctime)s %(levelname)s: %(message)s' )

	# Add the handlers to the logger
	if config['Logging Settings']['Log to File']:
		logfile_handler = logging.FileHandler( log_file )
		logfile_handler.setFormatter( formatter )
		logger.addHandler( logfile_handler )

	if config['Logging Settings']['Log to Console'] and not args.quiet:
		console_handler = logging.StreamHandler()
		console_handler.setFormatter( formatter )
		logger.addHandler( console_handler )

	# Enable/Disable Logging
	logger.disabled = not config['Logging Settings']['Enabled']

	logger.info( 'Platform: ' + platform.system() )
	logger.info( 'Version: ' + version + ' - ' + state )
	if state != 'stable':
		logger.warning( 'State is not stable: ' + state )

	if args.ddata == True:
		filepath = os.path.join( root, 'data' )
		logger.info( 'Data filepath: ' + filepath )
		for (dirpath, dirnames, filenames) in os.walk(filepath):
			for file in filenames:
				if file.endswith('.dat'):
					logger.info( 'Deleting: ' + file )
					os.remove( os.path.join( filepath, file ) )
		exit()

	email_template = getrender( root, config['Template Settings']['Email Template'],  config['Template Settings']['Template Directory'])
	breach_template = getrender( root, config['Template Settings']['Breach Template'],  config['Template Settings']['Template Directory'])

	for email in config['Email Accounts']:

		response = getbreaches( root, email )

		if response == 'None Found':
			continue

		html_body=""
		text_body=""

		for breach in response:
			logger.debug( 'Breach: ' + breach['Title'] )
			cats = ', '.join( [ str(x) for x in breach['DataClasses'] ] )
			html_body += breach_template.render( title=breach['Title'],
				domain=breach['Domain'],
				date=breach['BreachDate'],
				logo=breach['LogoPath'],
				description=breach['Description'],
				categories=cats )
			text_body += '\n'.join( [ breach['Title'],
				'Domain: '+ breach['Domain'],
				'Date: ' + breach['BreachDate'],
				'Description: ' + breach['Description'],
				'Description: ' + cats ] ) + '\n\n'

		# https://stackoverflow.com/questions/882712/sending-html-email-using-python
		# Create message container - the correct MIME type is multipart/alternative.
		msg = MIMEMultipart('alternative')
		msg['Subject'] = config['SMTP Settings']['Subject']
		msg['From'] = config['SMTP Settings']['From']
		msg['To'] = email
		# Create the body of the message (a plain-text and an HTML version).
		text = 'Breaches found for: ' + email + '\n\n' + text_body

		html = BeautifulSoup( email_template.render( email=email, admin=config['Template Settings']['Administrator'],body=html_body ), 'html.parser' ).prettify()

		# Record the MIME types of both parts - text/plain and text/html.
		part1 = MIMEText(text, 'plain')
		part2 = MIMEText(html, 'html')

		# Attach parts into message container.
		# According to RFC 2046, the last part of a multipart message, in this case
		# the HTML message, is best and preferred.
		msg.attach(part1)
		msg.attach(part2)

		if args.nemail == False:
			logger.info( 'Sending email to: ' + email )
			# Send the message via local SMTP server.
			s = smtplib.SMTP(config['SMTP Settings']['Server'])
			s.login(config['SMTP Settings']['Username'], config['SMTP Settings']['Password'])
			# sendmail function takes 3 arguments: sender's address, recipient's address
			# and message to send - here it is sent as one string.
			s.sendmail(config['SMTP Settings']['From'], email, msg.as_string())
			s.quit()